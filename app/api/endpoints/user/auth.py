# fastapi 
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
# sqlalchemy
from sqlalchemy.orm import Session

from app.api.endpoints.user import functions as user_functions
from app.api.endpoints.user.functions import get_user_by_id, create_access_token
from app.core.dependencies import get_db
from app.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.schemas.user import User, UserLogin, Token

auth_module = APIRouter()


# ============> login/logout < ======================
# getting access token for login 
@auth_module.post("/login", response_model=Token)
async def login_for_access_token(
        user: UserLogin,
        db: Session = Depends(get_db)
) -> Token:
    member = user_functions.authenticate_user(db, user=user)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # 엑세스 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_functions.create_access_token(
        data={"id": member.id, "email": member.email, "role": member.role}, expires_delta=access_token_expires
    )

    # 리프레시 토큰 생성
    refresh_token_expires = timedelta(days=user_functions.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = user_functions.create_refresh_token(
        data={"id": member.id, "email": member.email}, expires_delta=refresh_token_expires
    )

    # 토큰 만료 시간 계산 (엑세스 토큰)
    expires_in = access_token_expires.total_seconds()

    # 응답 구성
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in
    )
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = user_functions.create_access_token(
    #     data={"id": member.id, "email": member.email, "role": member.role}, expires_delta=access_token_expires
    # )
    # return Token(access_token=access_token, token_type="bearer")


# get curren user 
@auth_module.get('/users/me/', response_model=User)
async def read_current_user(current_user: Annotated[User, Depends(user_functions.get_current_user)]):
    return current_user


@auth_module.get("/token/refresh")
async def refresh_access_token(refresh_token: Annotated[User, Depends(user_functions.refresh_access_token)]):
    return refresh_token
