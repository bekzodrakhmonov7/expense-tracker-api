from sqlmodel import SQLModel, Field, Column, DateTime, func
from pydantic import EmailStr
from datetime import datetime

class UsersBase(SQLModel):
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    password_hash: str

class Users(UsersBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None =  Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))

class UsersPublic(SQLModel):
    id: int
    username: str
    email: EmailStr
    password_hash: str

class UsersLogin(SQLModel):
    email: EmailStr
    password_hash: str
