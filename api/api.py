from fastapi import FastAPI, HTTPException, status
from database.schemas import UsersPublic, UsersBase, Users, UsersLogin
from database.database import SessionDep, get_user_by_email
from sqlalchemy.exc import IntegrityError
from core.security import hash_password


router = FastAPI()


@router.get("/health", tags=["Helath"])
def get_health():
    return {"status": "Healthy"}

@router.post("/auth/register", response_model=UsersPublic, tags=["Auth"])
def user_register(user_info: UsersBase, session: SessionDep):
    db_user = Users.model_validate(user_info)
    db_user.password_hash = hash_password(db_user.password_hash)
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email is already taken")
    except Exception as e:
        session.rollback()
        raise 

@router.post("/auth/login", response_model=UsersPublic, tags=["Auth"])
def user_login(user_info: UsersLogin, session: SessionDep):
    db_user = get_user_by_email(email=user_info.email, session=session, expected_result=Users)
    return db_user