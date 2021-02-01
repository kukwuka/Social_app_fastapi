from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
import os

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
load_dotenv()
SQLALCHEMY_DATABASE_URL = f'postgres://{os.environ.get("POSTGRES_USER")}:' \
                          f'{os.environ.get("POSTGRES_PASSWORD")}@' \
                          f'{os.environ.get("POSTGRES_HOST")}/' \
                          f'{os.environ.get("POSTGRES_DB")}'
# print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

database = Database(SQLALCHEMY_DATABASE_URL)

Base: DeclarativeMeta = declarative_base()