from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, PasswordResetConfirm, PasswordResetRequest, TokenOut, VerifyEmailRequest
from app.schemas.user import UserCreate, UserOut
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.verification_service import VerificationService
from app.uow.uow import UnitOfWork

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_auth_service(db: Session) -> AuthService:
    uow = UnitOfWork(db)
    verification_svc = VerificationService(repo=uow.verifications, email_svc=EmailService())
    return AuthService(uow, verification_svc)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return _build_auth_service(db).register(data)


@router.post("/login", response_model=TokenOut)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return _build_auth_service(db).login(data.email, data.password)


@router.post("/verify-email", response_model=UserOut)
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    return _build_auth_service(db).verify_email(data.email, data.code)


@router.post("/request-reset-password", status_code=status.HTTP_204_NO_CONTENT)
def request_reset_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    _build_auth_service(db).request_password_reset(data.email)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    _build_auth_service(db).reset_password(data.email, data.code, data.new_password)
