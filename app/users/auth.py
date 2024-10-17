from passlib.context import CryptContext
from pydantic import EmailStr
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from app.config import get_auth_data
from app.users.dao import UsersDAO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login/")


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)  # срок действия
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt


def create_refresh_token(data: dict) -> str:
    return create_access_token(data, expires_delta=timedelta(days=30))  # refresh токена 30 дней


def get_password_hash(password: str) -> str: # хеширует пароль
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool: # проверяет соответствие обычного пароля и хешированного пароля
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(email: EmailStr, password: str): # аутентификация пользователя на основе переданных email и пароля
    user = await UsersDAO.find_one_or_none(email=email)
    if not user or not verify_password(plain_password=password, hashed_password=user.hashed_password):
        return None
    return user
