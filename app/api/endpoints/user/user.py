from uuid import UUID

# fastapi
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

# import
from app.schemas.user import (
    UserSchema,
    UserCreate,
    UserUpdate,
    UserSignInResponse,
    UserMeResponse,
    UserWithdrawal,
    UserValidation,
)
from app.service import UserService
from app.auth.authenticate import get_current_user

user_module = APIRouter()


# create new user
@user_module.post(
    "/signup", response_model=UserSignInResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_user(
    request: UserCreate,
    user_service: UserService = Depends(),
):
    new_user = await user_service.signup_user(user=request)

    return new_user


# get all user
@user_module.get(
    "/",
    response_model=list[UserSchema],
    # dependencies=[Depends(RoleChecker(['admin']))]
)
async def get_users(
    skip: int = 0,
    limit: int = 10,
    user_service: UserService = Depends(),
):
    users = await user_service.get_user_list(skip, limit)
    return [
        UserSchema(
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
            mobile=user.mobile,
            referral_code=user.referral_code,
            lemons=user.lemons.lemon_count if user.lemons else None,
        )
        for user in users
    ]


# get current user
@user_module.get("/me", response_model=UserMeResponse)
async def user_me_handler(
    current_user: UUID = Depends(get_current_user),
    user_service: UserService = Depends(),
) -> UserMeResponse:
    user = await user_service.get_user_by_id(user_id=current_user)

    return UserMeResponse.from_orm(user)


@user_module.put("/me", response_model=UserMeResponse)
async def update_user(
    update_data: UserUpdate,
    current_user: UUID = Depends(get_current_user),
    user_service: UserService = Depends(),
):
    user = await user_service.update_user(
        user_id=current_user,
        user_data=update_data,
    )

    return UserMeResponse.from_orm(user)


# get user by id
@user_module.get(
    "/{user_id}",
    response_model=UserMeResponse,
)
async def get_user_by_id(
    user_id: UUID, user_service: UserService = Depends()
) -> UserMeResponse:
    user = await user_service.get_user_by_id(user_id)
    return UserMeResponse.from_orm(user)


# user-withdrawal
@user_module.delete("/withdraw", status_code=204)
async def delete_user_handler(
    request: UserWithdrawal,
    current_user: UUID = Depends(get_current_user),
    user_service: UserService = Depends(),
):
    await user_service.deactivate_user(
        user_id=current_user,
        password=request.password,
        delete_reasons=request.delete_reasons,
    )


@user_module.get("/emails/validation", response_model=UserValidation)
async def check_email_availability(
    email: str,
    user_service: UserService = Depends(),
):
    is_available = await user_service.check_email_availability(email=email)
    return UserValidation(result=is_available)


@user_module.get("/nickname/validation", response_model=UserValidation)
async def check_nickname_availability(
    nickname: str,
    user_service: UserService = Depends(),
):
    is_available = await user_service.check_nickname_availability(nickname)
    return UserValidation(result=is_available)
