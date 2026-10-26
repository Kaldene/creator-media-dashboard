# src/api/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth.schemas import CreateUser, ShowUser, ReturnToken
from src.api.auth.models import User
from src.services.auth_service import AuthService
from src.api.dependencies import get_auth_service, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=ShowUser)
async def register_user(
    user_data: CreateUser, 
    service: AuthService = Depends(get_auth_service)
):
    if service.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return service.create_user(user_data)

@router.post("/login", response_model=ReturnToken)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    token = service.authenticate_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return ReturnToken(access_token=token)

# тестовый роут
@router.get("/me", response_model=ShowUser)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user