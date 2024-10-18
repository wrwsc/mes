from passlib.context import CryptContext
from pydantic import EmailStr
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt
from app.config import get_auth_data
import os
import requests

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://gitlab.com/oauth/authorize",
    tokenUrl="https://gitlab.com/oauth/token"
)

GITLAB_CLIENT_ID = os.getenv('GITLAB_CLIENT_ID')
GITLAB_CLIENT_SECRET = os.getenv('GITLAB_CLIENT_SECRET')

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt


def create_refresh_token(data: dict) -> str:
    return create_access_token(data, expires_delta=timedelta(days=44))  # refresh токена 44 дня


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


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

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return None

    token = response.json().get("access_token")
    return token