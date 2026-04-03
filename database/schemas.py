from datetime import date, datetime

from pydantic import BaseModel, EmailStr
from sqlmodel import Column, DateTime, Field, SQLModel, func


class UsersBase(SQLModel):
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    password: str


class Users(UsersBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )


class UsersPublic(SQLModel):
    id: int
    username: str
    email: EmailStr


class UsersLogin(SQLModel):
    email: EmailStr
    password: str


class Expense_Categories(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)


class ExpensesBase(SQLModel):
    description: str = Field(nullable=False)
    amount: float = Field(nullable=False)
    category_id: int = Field(foreign_key="expense_categories.id")


class Expenses(ExpensesBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id")
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )


class ExpensesPublic(SQLModel):
    id: int
    description: str
    amount: float
    category_id: int
    created_at: datetime | None = None


class ExepenseFilter(BaseModel):
    start_date: date | None
    end_date: date | None
