import jwt
from pwdlib import PasswordHash
from fastapi import HTTPException, status

def hash_password(password: str):
    if password == "":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Password must not be empty")
    password_hash = PasswordHash.recommended()
    hash = password_hash.hash(password=password)


    return hash