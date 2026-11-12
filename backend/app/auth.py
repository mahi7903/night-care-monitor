import secrets
from datetime import timedelta

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import StaffUser, utcnow

password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user: StaffUser) -> str:
    payload = {
        "sub": str(user.id),
        "exp": utcnow() + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _user_from_token(credentials, db: Session) -> StaffUser | None:
    if credentials is None:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.InvalidTokenError:
        return None
    user_id = payload.get("sub")
    return db.get(StaffUser, int(user_id)) if user_id else None


def _valid_device_key(api_key: str | None) -> bool:
    return api_key is not None and secrets.compare_digest(api_key, settings.device_api_key)


def _unauthorised() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_staff(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> StaffUser:
    user = _user_from_token(credentials, db)
    if user is None:
        raise _unauthorised()
    return user


def require_device(x_api_key: str | None = Header(default=None)) -> None:
    if not _valid_device_key(x_api_key):
        raise _unauthorised()


def require_staff_or_device(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> None:
    if _valid_device_key(x_api_key):
        return
    if _user_from_token(credentials, db) is None:
        raise _unauthorised()