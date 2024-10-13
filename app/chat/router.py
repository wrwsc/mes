from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.config import get_auth_data
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, PasswordMismatchException
from app.users.auth import get_password_hash, authenticate_user, create_access_token, create_refresh_token
from app.users.dao import UsersDAO
from app.users.schemas import SUserRegister, SUserAuth, Token
from app.users.dependencies import get_current_user

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/register/")
async def register_user(user_data: SUserRegister) -> dict:
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if user:
        raise UserAlreadyExistsException

    if user_data.password != user_data.password_check:
        raise PasswordMismatchException("Пароли не совпадают")
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.add(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password
    )

    return {'message': 'Вы успешно зарегистрированы!'}


@router.post("/login/", response_model=Token)
async def auth_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(email=form_data.username, password=form_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {
        'ok': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'message': 'Авторизация успешна!'
    }


@router.post("/refresh/", response_model=Token)
async def refresh_access_token(refresh_token: str):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(refresh_token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=403, detail="Refresh token is invalid or expired.")

    user_id: str = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=403, detail="User ID not found in token.")
    access_token = create_access_token({"sub": user_id})

    return {
        'ok': True,
        'access_token': access_token,
        'token_type': 'bearer',
        'message': 'Access token refreshed successfully!'
    }


@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}