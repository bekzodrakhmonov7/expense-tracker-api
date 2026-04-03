from datetime import date
from pathlib import Path

from core.security import create_access_token, decode_access_token, hash_password
from database.database import (
    SessionDep,
    delete_expense_db,
    get_all_expenses_user,
    get_categories,
    get_expense_by_id,
    get_user_by_email,
)
from database.schemas import (
    Expense_Categories,
    Expenses,
    ExpensesBase,
    ExpensesPublic,
    Users,
    UsersBase,
    UsersLogin,
    UsersPublic,
)
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError

router = FastAPI()

bearer = HTTPBearer()
frontend_path = Path(__file__).resolve().parent.parent / "frontend" / "index.html"


@router.get("/", include_in_schema=False)
def get_frontend() -> FileResponse:
    return FileResponse(frontend_path)


@router.get("/health", tags=["Helath"])
def get_health():
    return {"status": "Healthy"}


@router.get("/categories", response_model=list[Expense_Categories], tags=["Expenses"])
def get_expense_categories(session: SessionDep):
    return get_categories(session)


@router.post("/auth/register", tags=["Auth"])
def user_register(user_info: UsersBase, session: SessionDep) -> dict[str, str]:
    db_user = Users.model_validate(user_info)
    db_user.password = hash_password(db_user.password)
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        access_token = create_access_token(db_user.email)
        return {"access_token": access_token}
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already taken",
        )
    except Exception:
        session.rollback()
        raise


@router.post("/auth/login", tags=["Auth"])
def user_login(user_info: UsersLogin, session: SessionDep) -> dict[str, str]:
    db_user = get_user_by_email(
        email=user_info.email, session=session, expected_result=Users
    )
    access_token = create_access_token(db_user.email)
    return {"access_token": access_token}


@router.get("/auth/me", response_model=UsersPublic, tags=["Auth"])
def get_user(
    session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer)
) -> Users:
    token = credentials.credentials
    email = decode_access_token(token)
    db_user = get_user_by_email(email, session, Users)
    return db_user


@router.post("/expenses", response_model=ExpensesPublic, tags=["Expenses"])
def create_expense(
    expense: ExpensesBase,
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = credentials.credentials
    email = decode_access_token(token)
    db_user_id = get_user_by_email(email, session, Users.id)
    db_expense = Expenses.model_validate(expense)
    if db_expense.amount < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Expense amount must be greater than 0",
        )
    if db_expense.description == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Description cannot be empty",
        )
    db_expense.user_id = db_user_id
    try:
        session.add(db_expense)
        session.commit()
        session.refresh(db_expense)
        return db_expense
    except IntegrityError:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise


@router.get("/expenses", response_model=list[ExpensesPublic], tags=["Expenses"])
def get_all_expenses(
    session: SessionDep,
    start_date: date | None = None,
    end_date: date | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    if start_date and end_date:
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="end date cannot be earlier than start date",
            )

    token = credentials.credentials
    email = decode_access_token(token)
    db_user_id = get_user_by_email(email, session, Users.id)
    expenses = get_all_expenses_user(db_user_id, session, start_date, end_date)
    return expenses


@router.get("/expenses/{expense_id}", response_model=ExpensesPublic, tags=["Expenses"])
def get_expense(
    expense_id: int,
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = credentials.credentials
    email = decode_access_token(token)
    db_user_id = get_user_by_email(email, session, Users.id)
    db_expense = get_expense_by_id(expense_id, session)
    if db_expense.user_id == db_user_id:
        return db_expense
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put("/expenses/{expense_id}", response_model=ExpensesPublic, tags=["Expenses"])
def update_expense(
    expense_id: int,
    expense_body: ExpensesBase,
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = credentials.credentials
    email = decode_access_token(token)
    db_user_id = get_user_by_email(email, session, Users.id)
    db_expense = get_expense_by_id(expense_id, session)
    if db_expense.user_id == db_user_id:
        db_expense.description = expense_body.description
        db_expense.amount = expense_body.amount
        db_expense.category_id = expense_body.category_id
        try:
            session.add(db_expense)
            session.commit()
            session.refresh(db_expense)
            return db_expense
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        except Exception:
            session.rollback()
            raise
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete(
    "/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Expenses"]
)
def delete_expense(
    expense_id: int,
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = credentials.credentials
    email = decode_access_token(token)
    db_user_id = get_user_by_email(email, session, Users.id)
    db_expense = get_expense_by_id(expense_id, session)
    if db_expense.user_id != db_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    delete_expense_db(db_expense, session)
