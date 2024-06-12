# fastapi
import os
import phonenumbers
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from dotenv import load_dotenv

# sqlalchemy
from sqlalchemy.orm import Session

# twilio
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.http.validation_client import ValidationClient

from app.api.endpoints.user import functions as user_functions
from app.core.dependencies import get_db, oauth2_scheme
from app.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.user import User, UserLogin, Token
from app.service.auth import normalize_phone_number

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

auth_module = APIRouter()


# ============> login/logout < ======================
# getting access token for login
@auth_module.post("/login", response_model=Token)
async def login_for_access_token(
    user: UserLogin, db: Session = Depends(get_db)
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
        data={"id": member.id, "email": member.email, "role": member.role},
        expires_delta=access_token_expires,
    )

    # 리프레시 토큰 생성
    refresh_token_expires = timedelta(days=user_functions.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = user_functions.create_refresh_token(
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


# get curren user
@auth_module.get("/users/me/", response_model=User)
async def read_current_user(
    current_user: Annotated[User, Depends(user_functions.get_current_user)]
):
    return current_user


@auth_module.get("/token/refresh")
async def refresh_access_token(
    refresh_request: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> Token:
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


class SendCodeAttempt(BaseModel):
    time: str
    channel: str
    attempt_sid: str


class TwilioVerificationCheckResponse(BaseModel):
    sid: Optional[str]
    service_sid: Optional[str]
    account_sid: Optional[str]
    to: Optional[str]
    channel: Optional[str]
    status: Optional[str]
    valid: Optional[bool]
    amount: Optional[str]
    payee: Optional[str]
    date_created: Optional[datetime]
    date_updated: Optional[datetime]
    lookup: Optional[Dict[str, Any]]
    send_code_attempts: Optional[List[Dict[str, Any]]]
    sna: Optional[str]
    url: Optional[str]


@auth_module.post(
    "/sms-verify",
    status_code=status.HTTP_200_OK,
    response_model=TwilioVerificationCheckResponse,
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

        return JSONResponse(
            status_code=200,
            content={
                "message": "Obtained verification status",
                "status": verification_check.status,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
