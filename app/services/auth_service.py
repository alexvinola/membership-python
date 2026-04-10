from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenOut
from app.schemas.user import UserCreate, UserOut


class AuthService:
    def __init__(self, db: Session) -> None:
        self._users = UserRepository(db)

    def register(self, data: UserCreate) -> UserOut:
        if self._users.get_by_email(data.email):
            raise ConflictException("Email already registered")
        user = self._users.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            name=data.name,
        )
        return UserOut.model_validate(user)

    def login(self, email: str, password: str) -> TokenOut:
        user = self._users.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise UnauthorizedException("Invalid credentials")
        if user.status != "active":
            raise UnauthorizedException("Account is not active")
        token = create_access_token(subject=user.id)
        return TokenOut(access_token=token)
