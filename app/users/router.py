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

router = APIRouter(prefix='/auth', tags=['Auth'])# создание API-маршрута для авторизации пользователя
templates = Jinja2Templates(directory='app/templates') # создание шаблонизатора Jinja2

@router.get('/login')
# Выполняет авторизацию пользователя в GitLab
async def login_in_gitlab(code: str):
    token = await authenticate_user_in_gitlab(code)# ожидание аутентификации пользователя и получение токена
    # Если токен неверный, то выбрасывается HTTPException
    if not token:
        raise HTTPException(status_code=400, detail='Неверный код авторизации')

    #Достаем информацию о пользователе с GitLAb и регистрируем его на сайте
    user_info_url = "https://gitlab.com/api/v4/user"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(user_info_url, headers=headers)
    if response.statuc_code != 200:
        raise HTTPException(status_code=400, detail='Не удалось получить информацию о пользователе')

    user_info = response.json()

    user = await UsersDAO.find_one_or_none(email=user_info['email'])
    # Если пользователь не существует, то мы его зарегестрируем
    if not user:
        hashed_password = get_password_hash(token)
        await UsersDAO.add(
            name = user_info['name'],
            email = user_info['email'],
            hashed_password = hashed_password
        )

    refresh_token = create_refresh_token({'sub': str(user.id)})# токен обновления
    access_token = create_access_token({'sub': str(user.id)})# токен доступа

    return {
        'ok': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'message': 'Авторизация через GitLab прошла успешна!'
    }  # возвращает словарь с данными об авторизации, указывающее на то,
    # прошла ли авторизация; токен доступа; токен обновления; тип токена; сообщение о прохождении авторизации

@router.get("/", response_class=HTMLResponse)
# маршрут отвечает на GET запрос и возвращает шаблон HTML страницы 'auth.html'
async def get_auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})