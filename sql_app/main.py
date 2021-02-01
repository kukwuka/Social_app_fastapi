from typing import List
from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile, WebSocket
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import crud
import models
import schemas
from database import SessionLocal, engine
from jose import JWTError, jwt
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from database import database
from starlette.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/media", StaticFiles(directory="media"), name="media")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, crud.SECRET_KEY, algorithms=[crud.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, username=token_data)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/users/")
def create_user(
        user: schemas.UserCreate, db: Session = Depends(get_db)
):
    try:
        new_user = crud.create_user(db=db, user=user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with this name already exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return


@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(
        item: schemas.PostCreate,
        current_user: models.User = Depends(get_current_user)
):
    print("here")
    return await crud.create_post(user_id=current_user.id, item=item)


@app.get("/posts/")
async def post_list():
    return await crud.post_list()


@app.post("/posts/{post_id}/comment")
async def create_comment(
        comment: schemas.CommentBase,
        post_id: int,
        file: UploadFile = File(...),
        current_user: models.User = Depends(get_current_user)

):
    user_id = current_user.id
    return await crud.create_comment(comment=comment, post_id=post_id, user_id=user_id, )


@app.get("/posts/{post_id}")
async def post_detail(post_id: int):
    post = await crud.get_post_with_comments(post_id)
    return post


@app.delete("/posts/{post_id}")
async def post_detail(post_id: int, current_user: models.User = Depends(get_current_user)):
    post = await crud.delete_post_with_comments(post_id, user_id=current_user.id)
    return post


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user: models.User = Depends(get_current_user)):
    await websocket.accept()
    while True:
        data = await websocket.s
        await websocket.send_text(f"Message text was: {data}")
