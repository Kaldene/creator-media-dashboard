from sqlalchemy.orm import Session
from src.api.auth.models import User
from src.api.auth.schemas import CreateUser
from src.services.authSecurity import AuthSecurity

class AuthService:
    def __init__(self,db: Session) -> None:
        self.db = db
        self.security = AuthSecurity()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_data: CreateUser):
        hashed_pw = self.security.hash_password(user_data.password)

        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_pw
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self,email: str, password: str) -> str | None:
        user =  self.get_user_by_email(email)

        if not user or not self.security.verify_password(password, user.hashed_password):
            return None

        token_data = {"sub": user.email}
        return self.security.generate_token(token_data)

