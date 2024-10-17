from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

database_url = 'sqlite+aiosqlite:///db.sqlite3'
engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase): # класс для моделей (таблиц) базы данных
    created_at: Mapped[datetime] = mapped_column(server_default=func.now()) # хранит временную метку, когда запись была создана
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now()) # хранит временную метку, когда запись была последний раз обновлена
