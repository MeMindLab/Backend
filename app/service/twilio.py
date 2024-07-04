import phonenumbers
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.http.async_http_client import AsyncTwilioHttpClient

from fastapi import HTTPException, status

from app.core.config import config
from app.schemas.user import VerificationResult


class TwilioService:
    def __init__(self):
        self.account_sid = config.TWILIO_ACCOUNT_SID
        self.auth_token = config.TWILIO_AUTH_TOKEN
        self.verify_service_sid = config.TWILIO_VERIFY_SERVICE_SID
        self.http_client = None
        self.client = None

    async def initialize_client(self):
        if not self.http_client:
            self.http_client = AsyncTwilioHttpClient()
            self.client = Client(
                self.account_sid, self.auth_token, http_client=self.http_client
            )

    async def send_verification_code(self, phone: str):
        await self.initialize_client()
        try:
            verify_client = self.client.verify.v2.services(self.verify_service_sid)

            parsed_number = phonenumbers.parse(phone, "KR")
            if not phonenumbers.is_valid_number(parsed_number):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid phone number",
                )

            formatted_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )

            verification = await verify_client.verifications.create_async(
                to=formatted_number, channel="sms"
            )
            return verification
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

    async def verify_code(self, phone_number: str, code: str) -> VerificationResult:
        await self.initialize_client()
        try:
            verify_client = self.client.verify.v2.services(self.verify_service_sid)
            formatted_number = self.validate_phone_number(phone_number)

            verification_check = await verify_client.verification_checks.create_async(
                to=formatted_number, code=code
            )
            result = {
                "to": verification_check.to,
                "channel": verification_check.channel,
                "status": verification_check.status,
                "valid": verification_check.valid,
            }
        except TwilioRestException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send verification: {e.msg}",
            )
        return result

    def validate_phone_number(self, phone: str):
        try:
            parsed_number = phonenumbers.parse(phone, "KR")
            if not phonenumbers.is_valid_number(parsed_number):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid phone number",
                )
            return phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.phonenumberutil.NumberParseException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format",
            )

    def normalize_phone_number(self, phone_number: str) -> str:
        parsed_number = phonenumbers.parse(phone_number, "KR")
        return phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.E164
        )
