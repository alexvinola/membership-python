from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import TokenOut
from app.schemas.user import UserCreate, UserOut
from app.services.verification_service import VerificationService


class AuthService:
    def __init__(self, db: Session, verification_svc: VerificationService) -> None:
        self._db = db
        self._verification = verification_svc

    def register(self, data: UserCreate) -> UserOut:
        if self._db.query(User).filter(User.email == data.email).first():
            raise ConflictException("Email already registered")
        try:
            user = User(
                email=data.email,
                password=hash_password(data.password),
                name=data.name,
            )
            self._db.add(user)
            self._db.flush()
            self._verification.send_email_verification(email=user.email, user_id=user.id)
            self._db.commit()
            return UserOut.model_validate(user)
        except Exception:
            self._db.rollback()
            raise

    def login(self, email: str, password: str) -> TokenOut:
        user = self._db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password):
            raise UnauthorizedException("Invalid credentials")
        if user.status != "active":
            raise UnauthorizedException("Account is not active")
        return TokenOut(access_token=create_access_token(subject=user.id))

    def verify_email(self, email: str, code: str) -> UserOut:
        verified = self._verification.verify_email(email, code)
        if not verified:
            raise UnauthorizedException("Invalid or expired verification code")
        try:
            user = self._db.query(User).filter(User.email == email).first()
            if not user:
                raise NotFoundException("User not found")
            user.emailVerified = datetime.now(timezone.utc)
            self._db.commit()
            return UserOut.model_validate(user)
        except Exception:
            self._db.rollback()
            raise

    def request_password_reset(self, email: str) -> None:
        user = self._db.query(User).filter(User.email == email).first()
        if not user:
            return  # silent — don't reveal whether the email exists
        try:
            self._verification.send_password_reset(email=user.email, user_id=user.id)
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise

    def reset_password(self, email: str, code: str, new_password: str) -> None:
        verified = self._verification.verify_email(email, code)
        if not verified:
            raise UnauthorizedException("Invalid or expired code")
        try:
            user = self._db.query(User).filter(User.email == email).first()
            if not user:
                raise NotFoundException("User not found")
            user.password = hash_password(new_password)
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise
