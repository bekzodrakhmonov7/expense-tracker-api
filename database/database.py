from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import Depends, HTTPException, status
from core.config import settings
from typing import Annotated
from . import schemas

host = settings.postgres_host
port = settings.postgres_port
user = settings.postgres_user
password = settings.postgres_password.get_secret_value()
db = settings.postgres_db

conn_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(conn_string)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def init_database():
    SQLModel.metadata.create_all(engine)

def get_user_by_email(email: str, session: SessionDep, expected_result):
    statement = select(expected_result).where(schemas.Users.email == email)
    db_user = session.exec(statement=statement).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return db_user