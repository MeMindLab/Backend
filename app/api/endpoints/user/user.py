# fastapi
from fastapi import APIRouter, Depends, HTTPException

# sqlalchemy
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, Response
from starlette import status
from app.api.endpoints.user.functions import read_all_user, validate_nickname_length

# import
from app.core.dependencies import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.api.endpoints.user import functions as user_functions
from app.service.user import UserService

from sqlalchemy.ext.asyncio import AsyncSession

user_module = APIRouter()


# @user_module.get('/')
# async def read_auth_page():
#     return {"msg": "Auth page Initialization done"}


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


# get user by id
@user_module.get(
    "/{user_id}",
)
async def get_user_by_id(user_id: int, user_service: UserService = Depends()):
    result = await user_service.get_user_by_id(user_id)

    return result


# update user
@user_module.patch(
    "/{user_id}",
    response_model=User,
    #   dependencies=[Depends(RoleChecker(['admin']))]
)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    print(f"Received data: {user.model_dump()}")
    return user_functions.update_user(db, user_id, user)


# delete user
@user_module.delete(
    "/{user_id}",
    #    response_model=User,
    #    dependencies=[Depends(RoleChecker(['admin']))]
)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_functions.delete_user(db, user_id)
