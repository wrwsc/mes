from passlib.context import CryptContext
from pydantic import EmailStr
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt
from app.config import get_auth_data
import os
import requests


# создание объекта pwd_context, который используется для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# создание объекта для реализации авторизации через OAuth 2.0, определяющего URL для авторизации и получения токена
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://gitlab.com/oauth/authorize",
    tokenUrl="https://gitlab.com/oauth/token"
)

GITLAB_CLIENT_ID = os.getenv('GITLAB_CLIENT_ID')# идентификатор для авторизации пользователя в GitLab API
GITLAB_CLIENT_SECRET = os.getenv('GITLAB_CLIENT_SECRET')# секретный ключ, который используется для шифрования и расшифровки данных пользователя

# Создаёт токен доступа
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()# получение данных для аутентификации
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt


# Создаёт токен обновления
def create_refresh_token(data: dict) -> str:
    return create_access_token(data, expires_delta=timedelta(days=44))  # refresh токена 44 дня


# Возвращает хешированный пароль
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Проверяет соответствие обычного пароля и хешированного пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Аутентификация пользователя в GitLab
async def authenticate_user_in_gitlab(code: str):
    # Обмен кода на токен
    token_url = "https://gitlab.com/oauth/token"
    data = {
        "client_id": GITLAB_CLIENT_ID,
        "client_secret": GITLAB_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://your-redirect-uri"
    }
    # Отправление POST запроса на адрес, переданный в token_url, c данными, переданными в data
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return None
    # Из полученного JSON ответа извлекается токен доступа
    token = response.json().get("access_token")
    return token