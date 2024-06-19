# auth/jwt_handler.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt_hanlder import decode_token


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/user/login")


def authenticate(token: str = Depends(oauth2_schema)) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sign in required!!"
        )
    try:
        payload = decode_token(token)
        return payload
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
