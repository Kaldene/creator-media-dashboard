import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from src.core.config import Settings

settings = Settings()

class AuthSecurity:
    def __init__(self):
        self._pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
        self._jwt_secret_key = settings.jwt_secret_key
        self._jwt_algorithm = settings.jwt_algorithm

    def hash_password(self,password: str) -> str:
        return self._pwd_context.hash(password)

    def verify_password(self,password:str,hashed_password:str) -> bool:
        return self._pwd_context.verify(password,hashed_password)

    def generate_token(self,data:dict) -> dict:
        jwt_token = data.copy()
        expiration = datetime.now(timezone.utc) + timedelta(hours=1)
        jwt_token.update({"exp":expiration})

        end_coding =  jwt.encode(jwt_token,self._jwt_secret_key,algorithm=self._jwt_algorithm)

        return end_coding

    def decode_token(self,token: str) -> dict:
        return jwt.decode(token,self._jwt_secret_key,algorithms=self._jwt_algorithm)


