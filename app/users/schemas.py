from pydantic import BaseModel

# модель токена
class Token(BaseModel):
    access_token: str
    token_type: str

# модель данных токена
class TokenData(BaseModel):
    username: str | None = None