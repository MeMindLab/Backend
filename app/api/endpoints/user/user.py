# fastapi
from fastapi import APIRouter, Depends, HTTPException


# import
from app.schemas.user import User, UserCreate
from app.service.user import UserService
from app.auth.authenticate import get_current_user


user_module = APIRouter()


# create new user
@user_module.post("/signup", response_model=User)
async def create_new_user(
    request: UserCreate,
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
        return new_user

    except HTTPException:
        raise


# get all user
@user_module.get(
    "/",
    response_model=list[User],
    # dependencies=[Depends(RoleChecker(['admin']))]
)
async def get_users(
    skip: int = 0,
    limit: int = 10,
    user_service: UserService = Depends(),
):
    return await user_service.get_user_list(skip, limit)


# get current user
@user_module.get("/me", response_model=User)
async def user_me_handler(
    current_user: int = Depends(get_current_user),
    user_service: UserService = Depends(),
) -> User:
    return User.model_validate(
        await user_service.get_user_by_id(user_id=current_user),
        from_attributes=True,
    )


# get user by id
@user_module.get(
    "/{user_id}",
)
async def get_user_by_id(user_id: int, user_service: UserService = Depends()):
    result = await user_service.get_user_by_id(user_id)

    return result
