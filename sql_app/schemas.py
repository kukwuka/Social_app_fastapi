from typing import Optional
from pydantic import BaseModel
import datetime
from fastapi import Body

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str

class UserInDB(User):
    pass

class UserCreate(User):
    password: str
    email: str

class PostBase(BaseModel):
    title:str
    body:str

class PostList(PostBase):
    created_date: Optional[datetime.datetime]
    owner_id: int
    url: str

    class Config:
        orm_mode=True

class PostCreate(PostBase):
    pass


class CommentBase(BaseModel):
    name:str
    body:str

class CommentList(CommentBase):
    id: int
    post_id:int
    created_date: Optional[datetime.datetime]= Body(None)

    class Config:
        orm_mode= True