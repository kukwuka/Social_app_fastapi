from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType, URLType
import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    email = Column(EmailType)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    post = relationship("Post", back_populates="owner")
    comment = relationship("Comment", back_populates="user_related")


users = User.__table__


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    title = Column(String)
    body = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="post")
    post_comment = relationship("Comment", back_populates="post_related")


posts = Post.__table__


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    name = Column(String)
    email = Column(EmailType)
    url = Column(URLType)
    body = Column(String)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    post_related = relationship("Post", back_populates="post_comment")
    user_related = relationship("User", back_populates="comment")


comments = Comment.__table__