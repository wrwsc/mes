from fastapi import Request, HTTPException, status, Depends
from app.exceptions import TokenExpiredException, NoJwtException, NoUserIdException, TokenNoFoundException
from datetime import datetime, timedelta, timezone
from typing import Annotated
from jose import jwt, JWTError
from datetime import datetime, timezone
from app.config import get_auth_data
from app.users.auth import oauth2_scheme

def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise TokenNoFoundException
    return token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise NoJwtException

    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if not expire or expire_time < datetime.now(timezone.utc):
        raise TokenExpiredException

    user_id: str = payload.get('sub')
    if not user_id:
        raise NoUserIdException