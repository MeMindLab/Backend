# fastapi 
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
# sqlalchemy
from sqlalchemy.orm import Session

from app.api.endpoints.user import functions as user_functions
from app.api.endpoints.user.functions import get_user_by_id, create_access_token
from app.core.dependencies import get_db, oauth2_scheme
from app.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.models.user import TokenRefresh
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
async def refresh_access_token(refresh_request: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)) -> Token:
    # 리프레시 토큰 유효성 검증
    try:
        payload = user_functions.decode_jwt(refresh_request)
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 데이터베이스에서 유저 정보 조회
    user = user_functions.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 새로운 엑세스 토큰 생성
    access_token_expires = timedelta(minutes=user_functions.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_functions.create_access_token(
        data={"id": user.id, "email": user.email, "role": user.role}, expires_delta=access_token_expires
    )

    # 토큰 만료 시간 계산
    expires_in = access_token_expires.total_seconds()

    # 새로운 토큰 정보와 함께 응답 반환
    return Token(
        access_token=access_token,
        # refresh_token=refresh_request,  # 기존 리프레시 토큰 재사용
        token_type="bearer",
        expires_in=expires_in
    )
