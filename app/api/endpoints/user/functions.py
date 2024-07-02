import logging

from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt

# from auth import models, schemas
from sqlalchemy.orm import Session

from app.core.dependencies import get_db

# import
from app.models import user as UserModel
from app.schemas.user import UserCreate, UserUpdate
from app.auth import hashpassword, authenticate_bearer
from app.auth.jwt_hanlder import decode_token

# Initialize HashPassword instance
hash_password = hashpassword.HashPassword()


# get user by email
def get_user_by_email(db: Session, email: str):
    return db.query(UserModel.User).filter(UserModel.User.email == email).first()


# get user by nickname
def get_user_by_nickname(db: Session, nickname: str):
    return db.query(UserModel.User).filter(UserModel.User.nickname == nickname).first()


# get user by id
def get_user_by_id(db: Session, user_id: int):
    db_user = db.query(UserModel.User).filter(UserModel.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def validate_nickname_length(nickname: str):
    """사용자 이름과 닉네임의 길이를 검증합니다."""
    if len(nickname) < 3 or len(nickname) > 10:
        detail = {"message": "Nickname must be between 3 and 10 characters"}
        status_code = 400
        raise HTTPException(status_code=status_code, detail=detail)


def create_new_user(db: Session, user: UserCreate):
    hashed_password = hash_password.create_hash(user.password)

    new_user = UserModel.User(
        email=user.email,
        password=hashed_password,
        username=user.username,
        nickname=user.nickname,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

    # get all user


def read_all_user(db: Session, skip: int, limit: int):
    return db.query(UserModel.User).offset(skip).limit(limit).all()

    # update user


def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    updated_data = user.model_dump(exclude_unset=True)  # partial update
    for key, value in updated_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

    # delete user


def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    db.delete(db_user)
    db.commit()
    # db.refresh(db_user)
    return {"msg": f"{db_user.email} deleted successfully"}

    # =====================> login/logout <============================


def verify_password(plain_password, hashed_password):
    return hash_password.verify_hash(plain_password, hashed_password)


def authenticate_user(db: Session, user: UserCreate):
    member = get_user_by_email(db, user.email)
    if not member:
        return False
    if not verify_password(user.password, member.password):
        return False
    return member


# get current users info
def get_current_user(
    token: str = Depends(authenticate_bearer),
    db: Session = Depends(get_db),
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        current_email: str = payload.get("email")
        if current_email is None:
            raise credentials_exception
        user = get_user_by_email(db, current_email)
        if user is None:
            raise credentials_exception
        return user
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )
    except Exception as e:
        raise credentials_exception
