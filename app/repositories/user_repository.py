from sqlalchemy.orm import Session

from app.models import User
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: str) -> type[User] | None:
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> type[User] | None:
        return self._db.query(User).filter(User.email == email).first()

    def create(self, email: str, hashed_password: str, name: str | None = None) -> User:
        user = User(email=email, password=hashed_password, name=name)
        self._db.add(user)
        self._db.flush()
        return user

    def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        self._db.flush()
        return user

    def delete(self, user: User) -> None:
        self._db.delete(user)
        self._db.flush()
