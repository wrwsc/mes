from fastapi import Request, HTTPException, status, Depends
from app.exceptions import TokenExpiredException, NoJwtException, NoUserIdException, TokenNoFoundException
from jose import jwt, JWTError
from datetime import datetime, timezone
from app.config import get_auth_data
from app.users.dao import UsersDAO
from app.users.auth import oauth2_scheme

""" Обеспечение аутентификации и авторизации пользователей на основе JWT токенов и обработка возможных ошибок при этом процессе
() get_token(request: Request) принимает объект запроса 'Request' и извлекает токен доступа пользователя 'users_access_token'. Если токен не найден, функция вызывает исключение TokenNoFoundException. В противном случае функция возвращает извлеченный токен.
() get_current_user(token: str = Depends(oauth2_scheme)) принимает токен как параметр и пытается декодировать его с использованием секретного ключа и алгоритма, которые берутся из данных аутентификации. Если декодирование не удается (JWTError), функция вызывает исключение NoJwtException.
   Затем функция проверяет срок действия токена и его содержимое. Если токен истек или не содержит идентификатор пользователя, функция вызывает соответствующие исключения (TokenExpiredException или NoUserIdException).
   Затем функция пытается найти пользователя по идентификатору, полученному из токена, используя метод UsersDAO.find_one_or_none_by_id(int(user_id)).
   Если пользователь не найден, функция вызывает исключение HTTPException с кодом статуса 401 (означает, что пользователю не удаётся авторизоваться на сайте) и сообщением об ошибке "User not found". В противном случае функция возвращает найденного пользователя.
   """

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

    user = await UsersDAO.find_one_or_none_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user
