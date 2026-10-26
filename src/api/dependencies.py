from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.services.auth_service import AuthService
from src.api.auth.models import User
# Исправлена опечатка в названии класса
from src.services.media_services import MediaRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_media_repo(db: Session = Depends(get_db)) -> MediaRepository:
    return MediaRepository(db)

def get_current_user(
        token: str = Depends(oauth2_scheme),
        service: AuthService = Depends(get_auth_service)
) -> User:
    try:
        payload = service.security.decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise ValueError()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user