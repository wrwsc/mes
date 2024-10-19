from app.database import async_session_maker
from app.users.models import User
from sqlalchemy.future import select

class UsersDAO:
    @staticmethod
    async def find_one_or_none(email: str):
        async with async_session_maker() as session:
            result = await session.execute(select(User).filter_by(email=email))
            return result.scalar_one_or_none()

    @staticmethod
    async def add(name: str, email: str, hashed_password: str):
        async with async_session_maker() as session:
            new_user = User(name=name, email=email, hashed_password=hashed_password)
            session.add(new_user)
            await session.commit()