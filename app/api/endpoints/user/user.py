# fastapi
from fastapi import APIRouter, Depends, HTTPException

# sqlalchemy
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from starlette import status
from app.api.endpoints.user.functions import validate_nickname_length

# import
from app.core.dependencies import get_db, oauth2_scheme
from app.schemas.user import User, UserCreate, UserUpdate
from app.api.endpoints.user import functions as user_functions

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


# get all user
@user_module.get(
    "/",
    response_model=list[User],
    # dependencies=[Depends(RoleChecker(['admin']))]
)
async def read_all_user(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_functions.read_all_user(db, skip, limit)


# get user by id
@user_module.get(
    "/{user_id}",
    response_model=User,
    # dependencies=[Depends(RoleChecker(['admin']))]
)
async def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return user_functions.get_user_by_id(db, user_id)


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
