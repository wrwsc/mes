from app.database import session
from app.users.models import User

class UsersDAO:
    @staticmethod
    async def find_one_or_none(email: str):
        return session.query(User).filter_by(email=email).first()

    @staticmethod
    async def add(name: str, email: str, hashed_password: str):
        new_user = User(name=name, email=email, hashed_password=hashed_password)
        session.add(new_user)
        session.commit()
