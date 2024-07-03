from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from jose import JWTError

http_bearer = HTTPBearer(auto_error=False)


def authenticate_bearer(
    auth_header: HTTPAuthorizationCredentials | None = Depends(http_bearer),
) -> str | None:
    if auth_header is None:
        raise HTTPException(status_code=401, detail="Not Authorized")
    return auth_header.credentials
