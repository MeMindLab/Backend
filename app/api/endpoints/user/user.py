# fastapi
from fastapi import APIRouter, Depends, HTTPException


# import
from app.schemas.user import UserSchema, UserCreate, UserSignInResponse
from app.service.user import UserService
from app.service.lemon import LemonService
from app.schemas.lemon import LemonCreate
from app.auth.authenticate import get_current_user


user_module = APIRouter()


# create new user
@user_module.post("/signup", response_model=UserSignInResponse)
async def create_new_user(
    request: UserCreate,
    lemon_service: LemonService = Depends(),
    user_service: UserService = Depends(),
):
    try:
        # 닉네임 길이 검증
        user_service.validate_nickname_length(request.nickname)

        ## 데이터베이스에서 이메일과 닉네임 중복 검사
        db_user_by_email = await user_service.find_user_by_email(request.email)
        db_user_by_nickname = await user_service.get_user_by_nickname(request.nickname)

        if db_user_by_email and db_user_by_nickname:
            raise HTTPException(status_code=400, detail="Invalid nickname and email")
        elif db_user_by_email:
            raise HTTPException(status_code=400, detail="Invalid Email")
        elif db_user_by_nickname:
            raise HTTPException(status_code=400, detail="Invalid nickname")

        new_user = await user_service.create_new_user(user=request)

        # 레몬 초기화
        lemon_create = LemonCreate(lemon_count=0)
        await lemon_service.create_lemon_for_user(
            lemon_create=lemon_create, user_id=new_user.id
        )

        return new_user

    except HTTPException:
        raise


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
            lemons=user.lemons.lemon_count if user.lemons else None,
        )
        for user in users
    ]


# get current user
@user_module.get("/me", response_model=UserSchema)
async def user_me_handler(
    current_user: int = Depends(get_current_user),
    user_service: UserService = Depends(),
) -> UserSchema:
    user = await user_service.get_user_by_id(user_id=current_user)
    lemons_count = user.lemons.lemon_count if user.lemons else None
    user_dict = user.__dict__
    user_dict["lemons"] = lemons_count

    return UserSchema(**user_dict)


# get user by id
@user_module.get(
    "/{user_id}",
)
async def get_user_by_id(
    user_id: int, user_service: UserService = Depends()
) -> UserSchema:
    result = await user_service.get_user_by_id(user_id)
    return UserSchema(
        id=result.id,
        email=result.email,
        nickname=result.nickname,
        is_active=result.is_active,
        is_verified=result.is_verified,
        role=result.role,
        created_at=result.created_at,
        updated_at=result.updated_at,
        lemons=result.lemons.lemon_count if result.lemons else None,
    )
