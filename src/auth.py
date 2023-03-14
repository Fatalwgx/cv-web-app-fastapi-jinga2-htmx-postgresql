import os
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .models import Accounts
from .schemas import TokenData, User, Token
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .database import get_db


load_dotenv()


class AuthHandler:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 1080


    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, db, username: str, password: str):
        user = db.query(Accounts).filter(Accounts.username == username).first()
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire - datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def get_current_user(self, db, token: str = Depends(oauth2_scheme)):
        try:
            decoded_token = jwt.decode(
                token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            username: str = decoded_token.get("sub")
            if username is None:
                return None
            token_data = TokenData(username=username)
        except JWTError:
            return None
        user = db.query(Accounts).filter(Accounts.username == token_data.username).first()
        if user is None:
            return None
        return user

    def get_current_active_user(user: User = Depends(get_current_user)):
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
            return user
