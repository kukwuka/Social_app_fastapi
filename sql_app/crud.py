from sqlalchemy.orm import Session
import models
import schemas
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, UploadFile, File
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from models import users, posts, comments
from database import database
from sqlalchemy.sql import select
from pathlib import Path

# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()
#
#
# def create_user_item(db: Session, item: schemas.ItemCreate):
#     db_item = models.Item(**item.dict())
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item

SECRET_KEY = "bfcaa24859af5279d4ec6c1de8f9d2624f6d819b020eba2bcd9fe0483af45ed3"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_post(user_id: int, item: schemas.PostCreate):
    print("here")
    create_query = posts.insert().values(**item.dict(), owner_id=user_id)
    print(create_query)
    create_query_fetch_and_id = await database.execute(create_query)
    return {**item.dict(), "id": create_query_fetch_and_id}


async def get_post_with_comments(post_id: int):
    find_query_post = posts.select().where(posts.c.id == post_id)
    find_query_post_fetch = await database.fetch_one(query=find_query_post)
    if find_query_post_fetch is None:
        raise HTTPException(status_code=418, detail="couldn't find post")
    find_query_post_comments = comments.select().where(comments.c.post_id == post_id)
    find_query_post_comments_fetch = await database.fetch_all(query=find_query_post_comments)

    return {**find_query_post_fetch, 'comments': [dict(result) for result in find_query_post_comments_fetch]}


async def delete_post_with_comments(post_id: int, user_id=int):
    find_query_post = posts.select().where(posts.c.id == post_id)
    find_query_post_fetch = await database.fetch_one(query=find_query_post)
    if find_query_post_fetch is None:
        raise HTTPException(status_code=418, detail="couldn't find post")
    result_dict = {**find_query_post_fetch}
    if not result_dict['owner_id'] == user_id:
        raise HTTPException(status_code=418, detail="This post is not your.don't cry, just delete other one")
    delete_query = posts.delete().where(posts.c.id == post_id)
    delete_query_fetch = await database.execute(delete_query)

    delete_query_post_comments = comments.delete().where(comments.c.post_id == post_id)
    delete_query_post_comments_fetch = await database.fetch_all(query=delete_query_post_comments)

    return result_dict


async def post_list():
    join = posts.join(users, posts.c.owner_id == users.c.id)
    query = select([posts, users.c.username]).select_from(join)
    query_fetch = await database.fetch_all(query=query)
    return [dict(result) for result in query_fetch]


async def create_comment(post_id: int, user_id: int, comment: schemas.CommentBase, file: UploadFile = None):
    url = None
    if file:
        file_format = (Path(file.filename).suffix == '.PNG') \
                      or (Path(file.filename).suffix == '.png') \
                      or (Path(file.filename).suffix == '.jpg') \
                      or (Path(file.filename).suffix == '.pdf')
        if not file_format:
            raise HTTPException(status_code=418, detail="please send .png .jpg .pdf file")

        content = await file.read()
        with open(f'media/{file.filename}', "wb") as buffer:
            buffer.write(content)

        url = str("media/" + file.filename)
    create_query = comment.insert().values(**comment.dict(), user_id=user_id, url=url,post_id = post_id)
    print(create_query)
    create_query_fetch_and_id = await database.execute(create_query)
    return {**comment.dict(), 'id': create_query_fetch_and_id,'user_id':user_id, 'url':url,'post_id' : post_id}
