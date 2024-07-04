from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import JWTError

from app.auth.jwt_hanlder import decode_token

http_bearer = HTTPBearer(auto_error=False)


def authenticate_bearer(
    auth_header: HTTPAuthorizationCredentials | None = Depends(http_bearer),
) -> str | None:
    if auth_header is None:
        raise HTTPException(status_code=401, detail="Not Authorized")
    return auth_header.credentials


# get current users
def get_current_user(token: Annotated[str, Depends(authenticate_bearer)]) -> int:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="인증되지 않았습니다"
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = payload.get("id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )
    except Exception as e:
        raise credentials_exception
