#src/api/auth/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict

#============'/api/auth/register'==========
class CreateUser(BaseModel):
    username: str = Field(...,min_length=1,max_length=20)
    email: EmailStr
    password: str = Field(...,min_length=6,max_length=100)

class ShowUser(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

#============'/api/auth/login'==========
class LoginUser(BaseModel):
    email: EmailStr
    password: str = Field(...,min_length=6,max_length=100)

class ReturnToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
