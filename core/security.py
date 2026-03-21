import time

import jwt
from core.config import settings
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash


def hash_password(password: str) -> str:
    if password == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Password must not be empty",
        )
    password_hash = PasswordHash.recommended()
    hash = password_hash.hash(password=password)

    return hash


def create_access_token(email: str) -> str:
    payload = {"email": email, "expires": time.time() + 900}
    access_token = jwt.encode(
        payload, key=settings.jwt_token.get_secret_value(), algorithm=settings.jwt_algo
    )
    return access_token


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            key=settings.jwt_token.get_secret_value(),
            algorithms=settings.jwt_algo,
        )
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Expired."
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invelid Token."
        )
    return email
