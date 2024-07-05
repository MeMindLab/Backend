import phonenumbers

from fastapi import Depends, HTTPException, status
from datetime import timedelta


from app.core.config import config
from app.models.user import User
from app.repository.user import UserRepository

from app.auth.hashpassword import HashPassword
from app.auth.jwt_hanlder import create_access_token, create_refresh_token, decode_token
from app.schemas.user import Token, UserLogin


def normalize_phone_number(phone: str) -> str:
    try:
        # 입력된 전화번호 파싱
        parsed_number = phonenumbers.parse(phone, "KR")
        # 국가 코드를 포함한 형식으로 포맷팅
        formatted_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.E164
        )
        return formatted_number
    except phonenumbers.phonenumberutil.NumberParseException:
        # 파싱 실패 시 예외 처리
        raise ValueError("Invalid phone number format")


class AuthService:
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    async def authenticate_user(self, user_login: UserLogin) -> User:
        user = await self.user_repository.find_user_by_email(email=user_login.email)
        if not user or not HashPassword.verify_hash(user_login.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def login_handler(self, user_login: UserLogin) -> Token:
        user = await self.authenticate_user(user_login)

        # 엑세스 토큰 생성
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"id": user.id, "email": user.email, "role": user.role},
            expires_delta=access_token_expires,
        )

        # 리프레시 토큰 생성
        refresh_token_expires = timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(
            data={"id": user.id, "email": user.email},
            expires_delta=refresh_token_expires,
        )

        # 토큰 만료 시간 계산 (엑세스 토큰)
        expires_in = access_token_expires.total_seconds()

        # 응답 구성
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    async def refresh_token_handler(self, refresh_request: str) -> Token:
        try:
            payload = decode_token(refresh_request)
            token_type = payload.get("token_type")
            if token_type != "refresh_token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type. Expected refresh_token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

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
        user = await self.user_repository.find_user_by_id(user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 새로운 엑세스 토큰 생성
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"id": user.id, "email": user.email, "role": user.role},
            expires_delta=access_token_expires,
        )

        # 토큰 만료 시간 계산
        expires_in = access_token_expires.total_seconds()

        # 새로운 토큰 정보와 함께 응답 반환
        return Token(
            access_token=access_token,
            refresh_token=refresh_request,  # 기존 리프레시 토큰 재사용
            token_type="bearer",
            expires_in=expires_in,
        )
