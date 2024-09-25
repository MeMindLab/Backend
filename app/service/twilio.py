import phonenumbers

from uuid import UUID
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.http.async_http_client import AsyncTwilioHttpClient

from fastapi import HTTPException, status, Depends

from app.core.config import get_config, ConfigTemplate
from app.schemas.user import VerificationResult
from app.schemas.lemon import LemonUpdate
from app.service import LemonService


class TwilioService:
    def __init__(
        self,
        lemon_service: LemonService = Depends(LemonService),
        config: ConfigTemplate = Depends(get_config),
    ):
        self.account_sid = config.TWILIO_ACCOUNT_SID
        self.auth_token = config.TWILIO_AUTH_TOKEN
        self.verify_service_sid = config.TWILIO_VERIFY_SERVICE_SID
        self.http_client = None
        self.client = None
        self.lemon_service = lemon_service
        self.config = config

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

    async def verify_code(
        self,
        phone_number: str,
        code: str,
        user_id: UUID,
    ) -> VerificationResult:
        await self.initialize_client()
        try:
            verify_client = self.client.verify.v2.services(self.verify_service_sid)
            formatted_number = self.validate_phone_number(phone_number)

            verification_check = await verify_client.verification_checks.create_async(
                to=formatted_number, code=code
            )

            result = VerificationResult(
                to=verification_check.to,
                channel=verification_check.channel,
                status=verification_check.status,
                valid=verification_check.valid,
            )

            if verification_check.valid:
                # 여기서 레몬 갯수 업데이트
                await self.lemon_service.update_lemon_by_user_id(
                    lemon_data=LemonUpdate(
                        lemon_count=self.config.LEMON_COUNT_FOR_VERIFIED_USER
                    ),
                    user_id=user_id,
                )

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
