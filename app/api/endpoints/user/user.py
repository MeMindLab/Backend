# fastapi
from fastapi import APIRouter, Depends, HTTPException

# sqlalchemy
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from starlette import status
from app.api.endpoints.user.functions import validate_nickname_length

# import
from app.core.dependencies import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.api.endpoints.user import functions as user_functions
from app.service.user import UserService

user_module = APIRouter()


# @user_module.get('/')
# async def read_auth_page():
#     return {"msg": "Auth page Initialization done"}


# create new user
@user_module.post("/signup", response_model=User)
async def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    # 닉네임 길이 검증
    validate_nickname_length(user.nickname)

    # 데이터베이스에서 이메일과 닉네임 중복 검사
    db_user_by_email = user_functions.get_user_by_email(db, user.email)
    db_user_by_nickname = user_functions.get_user_by_nickname(db, user.nickname)
    print(db_user_by_email)
    print(db_user_by_nickname)

    if db_user_by_email and db_user_by_nickname:
        detail = {"message": "Invalid nickname and email"}
        status_code = 400
    elif db_user_by_email:
        detail = {"message": "Invalid Email"}
        status_code = 400
    elif db_user_by_nickname:
        detail = {"message": "Invalid nickname"}
        status_code = 400
    else:
        # 중복이 없는 경우 사용자 생성
        try:
            new_user = user_functions.create_new_user(db, user)
            print(new_user)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "created successfully", "user": new_user.email},
            )
        except Exception as e:
            print("exception?")
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"User creation failed: {str(e)}"
            )

    # 중복이나 유효성 검사 실패 시 응답
    return JSONResponse(status_code=status_code, content=detail)


@user_module.post("/signin_for_debug")
async def user_signin_for_debug_handler(
    q: UserCreate,
    user_service: UserService = Depends(),
):
    try:
        username = await user_service.get_user_by_username(q.username)
        email = await user_service.find_user_by_email(q.email)
        print(f"username : {username}")
        print(f"email : {email}")
    except HTTPException:
        print("except")
        pass
    else:
        print("else")
        raise HTTPException(status_code=400, detail="User already exists")


# get all user
@user_module.get(
    "/",
    response_model=list[User],
    # dependencies=[Depends(RoleChecker(['admin']))]
)
# async def user_list_handler(
#    skip: int = 0, limit: int = 100, user_service: UserService = Depends(),
# ):
async def user_list_handler(
    user_service: UserService = Depends(),
):
    result = await user_service.get_user_list()
    print(result)
    return result


# get user by id
@user_module.get(
    "/{user_id}",
    response_model=User,
    # dependencies=[Depends(RoleChecker(['admin']))]
)
async def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return await user_functions.get_user_by_id(db, user_id)


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
