# fastapi
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status


from app.auth.authenticate import authenticate_bearer
from app.service import AuthService, TwilioService
from app.schemas.user import (
    UserLogin,
    Token,
    VerificationCheckResponse,
)


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
):
    return await auth_service.refresh_token_handler(refresh_request)


@auth_module.post("/sms", status_code=status.HTTP_201_CREATED)
async def create_verification_code(
    phone: str, twilio_service: TwilioService = Depends()
):
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number is required."
        )

    verification = await twilio_service.send_verification_code(phone)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Verification sent", "message_sid": verification.sid},
    )


@auth_module.post(
    "/sms-verify",
    status_code=status.HTTP_200_OK,
    response_model=VerificationCheckResponse,
)
async def verify_code(
    phone_number: str, code: str, twilio_service: TwilioService = Depends()
):
    try:
        result = await twilio_service.verify_code(phone_number, code)

        return JSONResponse(
            status_code=200,
            content={"success": True, "data": {"result": result}},
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
