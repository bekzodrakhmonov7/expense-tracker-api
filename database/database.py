from datetime import date, datetime, time
from typing import Annotated

from core.config import settings
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, SQLModel, create_engine, select

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


CATEGORY_NAMES = [
    "Groceries",
    "Leisure",
    "Electronics",
    "Utilities",
    "Clothing",
    "Health",
    "Others",
]


def seed_categories() -> None:
    with Session(engine) as session:
        existing_names = set(
            session.exec(select(schemas.Expense_Categories.name)).all()
        )

        for name in CATEGORY_NAMES:
            if name not in existing_names:
                session.add(schemas.Expense_Categories(name=name))

        session.commit()


def get_user_by_email(email: str, session: SessionDep, expected_result):
    statement = select(expected_result).where(schemas.Users.email == email)
    db_user = session.exec(statement=statement).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return db_user


def get_expense_by_id(id: int, session: SessionDep) -> schemas.Expenses:
    statement = select(schemas.Expenses).where(schemas.Expenses.id == id)
    db_expense = session.exec(statement).first()
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )
    return db_expense


def get_all_expenses_user(
    user_id: int,
    session: SessionDep,
    start_date: date | None = None,
    end_date: date | None = None,
):
    statement = select(schemas.Expenses).where(schemas.Expenses.user_id == user_id)
    if start_date:
        start = datetime.combine(start_date, time.min)
        statement = statement.where(schemas.Expenses.created_at >= start)  # pyright: ignore[reportOptionalOperand]
    if end_date:
        end = datetime.combine(end_date, time.max)
        statement = statement.where(schemas.Expenses.created_at < end)  # pyright: ignore[reportOptionalOperand]

    expenses = session.exec(statement).all()
    return expenses


def delete_expense_db(expense: schemas.Expenses, session: SessionDep):
    try:
        session.delete(expense)
        session.commit()
    except Exception:
        session.rollback()
        raise
