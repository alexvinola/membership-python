from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException, NotFoundException
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.auth import TokenOut
from app.schemas.user import UserCreate, UserOut
from app.services.verification_service import VerificationService
from app.uow.uow import UnitOfWork


class AuthService:
    def __init__(self, uow: UnitOfWork, verification_svc: VerificationService) -> None:
        self._uow = uow
        self._verification = verification_svc

    def register(self, data: UserCreate) -> UserOut:
        if self._uow.users.get_by_email(data.email):
            raise ConflictException("Email already registered")

        try:
            user = self._uow.users.create(
                email=data.email,
                hashed_password=hash_password(data.password),
                name=data.name,
            )
            self._verification.send_email_verification(email=user.email, user_id=user.id)
            self._uow.commit()
            return UserOut.model_validate(user)
        except Exception:
            self._uow.rollback()
            raise

    def login(self, email: str, password: str) -> TokenOut:
        user = self._uow.users.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise UnauthorizedException("Invalid credentials")
        if user.status != "active":
            raise UnauthorizedException("Account is not active")
        token = create_access_token(subject=user.id)
        return TokenOut(access_token=token)

    def verify_email(self, email: str, code: str) -> UserOut:
        verified = self._verification.verify_email(email, code)
        if not verified:
            raise UnauthorizedException("Invalid or expired verification code")

        user = self._uow.users.get_by_email(email)
        if not user:
            raise NotFoundException("User not found")

        try:
            self._uow.users.update(user, emailVerified=datetime.now(timezone.utc))
            self._uow.commit()
            return UserOut.model_validate(user)
        except Exception:
            self._uow.rollback()
            raise

    def request_password_reset(self, email: str) -> None:
        user = self._uow.users.get_by_email(email)
        if not user:
            return  # silent — don't reveal whether the email exists
        try:
            self._verification.send_password_reset(email=user.email, user_id=user.id)
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise

    def reset_password(self, email: str, code: str, new_password: str) -> None:
        verified = self._verification.verify_email(email, code)
        if not verified:
            raise UnauthorizedException("Invalid or expired code")

        user = self._uow.users.get_by_email(email)
        if not user:
            raise NotFoundException("User not found")

        try:
            self._uow.users.update(user, password=hash_password(new_password))
            self._uow.commit()
        except Exception:
            self._uow.rollback()
            raise
