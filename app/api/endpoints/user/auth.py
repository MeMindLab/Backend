# fastapi
import os
import phonenumbers
from fastapi.responses import JSONResponse
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status


# sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# twilio
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.api.endpoints.user import functions as user_functions
from app.core.dependencies import get_db
from app.auth.authenticate import authenticate_bearer

from app.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.schemas.user import User, UserLogin, Token, VerificationResult
from app.service.auth import normalize_phone_number

from app.auth.jwt_hanlder import create_access_token, decode_token, create_refresh_token


auth_module = APIRouter()


# ============> login/logout < ======================
# getting access token for login
@auth_module.post("/login", response_model=Token)
async def login_for_access_token(
    user: UserLogin, db: AsyncSession = Depends(get_db)
) -> Token:
    member = user_functions.authenticate_user(db, user=user)

    if member:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        lemons = member.lemons
        print(f"member????:{member}")
        print(f"lemons object?????:{lemons}")
        # lemon_counts = [lemon.lemon_count for lemon in lemons]  # 각 레몬의 lemon_count 추출
        # print(lemon_counts)

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # 엑세스 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"id": member.id, "email": member.email, "role": member.role},
        expires_delta=access_token_expires,
    )

    # 리프레시 토큰 생성
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"id": member.id, "email": member.email},
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
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = user_functions.create_access_token(
    #     data={"id": member.id, "email": member.email, "role": member.role}, expires_delta=access_token_expires
    # )
    # return Token(access_token=access_token, token_type="bearer")


# get current user
@auth_module.get("/users/me/", response_model=User)
async def read_current_user(
    current_user: Annotated[User, Depends(user_functions.get_current_user)]
):
    return current_user


@auth_module.get("/token/refresh")
async def refresh_access_token(
    refresh_request: str = Depends(authenticate_bearer),
    db: Session = Depends(get_db),
) -> Token:
    # 리프레시 토큰 유효성 검증
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
    user = user_functions.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 새로운 엑세스 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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


@auth_module.post("/sms", status_code=status.HTTP_201_CREATED)
async def create_verification_code(phone: str):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")

    client = Client(account_sid, auth_token)
    verify_client = client.verify.services(verify_service_sid)

    if not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number is required."
        )

    try:
        parsed_number = phonenumbers.parse(phone, "KR")
        if not phonenumbers.is_valid_number(parsed_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone number"
            )

        formatted_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.E164
        )

        verification = verify_client.verifications.create(
            to=formatted_number, channel="sms"
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Verification sent", "message_sid": verification.sid},
        )

    except phonenumbers.phonenumberutil.NumberParseException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format",
        )

    except TwilioRestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send verification: {e.msg}",
        )


@auth_module.post(
    "/sms-verify",
    status_code=status.HTTP_200_OK,
    response_model=VerificationResult,
)
async def verify_code(phone_number: str, code: str):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")

    if not all([account_sid, auth_token, verify_service_sid]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Twilio configuration is missing.",
        )

    client = Client(account_sid, auth_token)
    verify_client = client.verify.services(verify_service_sid)
    phone = normalize_phone_number(phone_number)

    try:
        verification_check = verify_client.verification_checks.create(
            to=phone, code=code
        )
        result = {
            "to": verification_check.to,
            "channel": verification_check.channel,
            "status": verification_check.status,
            "valid": verification_check.valid,
        }

        return JSONResponse(
            status_code=200,
            content={"success": True, "data": {"result": result}},
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
