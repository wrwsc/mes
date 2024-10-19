from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class User(Base):
    __tablename__ = 'users'
    #Определяем столбец id, который будет хранить в себе id пользователя
    #Столбец сделаем первичным ключом, и он будет увеличиваться автоматически
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    #Будет хранить никнеймы пользователей, без нулевых элементов
    name: Mapped[str] = mapped_column(String, nullable=False)
    #Хранит хэшированный пароль
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)