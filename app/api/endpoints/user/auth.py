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
from app.core.config import config
from app.service.user import UserService
from app.service.auth import AuthService


from app.schemas.user import User, UserLogin, Token, VerificationResult
from app.service.auth import normalize_phone_number

from app.auth.jwt_hanlder import create_access_token, decode_token, create_refresh_token


auth_module = APIRouter()


# ============> login/logout < ======================
# getting access token for login
@auth_module.post("/login", response_model=Token)
async def user_login(user: UserLogin, auth_service: AuthService = Depends()):
    return await auth_service.login_handler(user)


@auth_module.get("/token/refresh")
async def refresh_access_token(
    refresh_request: str = Depends(authenticate_bearer),
    auth_service: AuthService = Depends(),
) -> Token:
    return await auth_service.refresh_token_handler(refresh_request)


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
