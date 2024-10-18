from fastapi import APIRouter, Response, Depends, HTTPException, Request, requests
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.config import get_auth_data
from fastapi.responses import HTMLResponse
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, PasswordMismatchException
from app.users.auth import get_password_hash, create_access_token, create_refresh_token, authenticate_user_in_gitlab
from app.users.dao import UsersDAO
from app.users.schemas import Token
from app.users.dependencies import get_current_user
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix='/auth', tags=['Auth'])
templates = Jinja2Templates(directory='app/templates')

@router.get('/login')
async def login_in_gitlab(code: str):
    token = await authenticate_user_in_gitlab(code)
    if not token:
        raise HTTPException(status_code=400, detail='Неверный код авторизации')

    #Достаем информацию о пользователе с GitLAb и регистрируем его на сайте
    user_info_url = ...
    headers = ...
    responce = requests.get(user_info_url, headers=headers)
    if responce.statuc_code != 200:
        raise HTTPException(status_code=400, detail='Не удалось получить информацию о пользователе')

    user_info = responce.json()

    user = await UsersDAO.find_one_or_none(email=user_info['email'])
    # Если пользователь не существует, то мы его зарегестрируем
    if not user:
        hashed_password = get_password_hash(token)
        await UsersDAO.add(
            name = user_info['name'],
            email = user_info['email'],
            hashed_password = hashed_password
        )

    refresh_token = create_refresh_token({'sub': str(user.id)})
    access_token = create_access_token({'sub': str(user.id)})

    return {
        'ok': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'message': 'Авторизация через GitLab прошла успешна!'
    }

@router.get("/", response_class=HTMLResponse, summary="Страница авторизации")
async def get_categories(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})