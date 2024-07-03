import logging

from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt

# from auth import models, schemas
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from app.core.dependencies import get_db

# import
from app.models import user as UserModel
from app.schemas.user import UserCreate, UserUpdate
from app.auth import hashpassword, authenticate_bearer
from app.auth.jwt_hanlder import decode_token

# Initialize HashPassword instance
hash_password = hashpassword.HashPassword()


# get user by email
async def get_user_by_email(session: AsyncSession, email: str) -> UserModel.User | None:
    query = select(UserModel.User).where(UserModel.User.email == email)
    result = await session.execute(query)

    return result.scalars().first()


# get user by nickname
async def get_user_by_nickname(session: AsyncSession, nickname: str):
    query = select(UserModel.User).where(UserModel.User.nickname == nickname)
    result = await session.execute(query)
    return result.scalars().first()


# get user by id
async def get_user_by_id(session: AsyncSession, user_id: int):
    query = select(UserModel.User).where(UserModel.User.id == user_id)
    user = await session.execute(query)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user.scalars().first()


def validate_nickname_length(nickname: str):
    """사용자 이름과 닉네임의 길이를 검증합니다."""
    if len(nickname) < 3 or len(nickname) > 10:
        detail = {"message": "Nickname must be between 3 and 10 characters"}
        status_code = 400
        raise HTTPException(status_code=status_code, detail=detail)


async def create_new_user(db: AsyncSession, user: UserCreate):
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


# get user by nickname
async def get_user_by_nickname(session: AsyncSession, nickname: str):
    query = select(UserModel.User).where(UserModel.User.nickname == nickname)
    result = await session.execute(query)
    return result.scalars().first()


async def read_all_user(session: AsyncSession, skip: int, limit: int):
    result = await session.execute(select(UserModel.User).offset(skip).limit(limit))
    return result.scalars().all()

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


async def authenticate_user(db: Session, user: UserCreate):
    member = await get_user_by_email(db, user.email)
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
