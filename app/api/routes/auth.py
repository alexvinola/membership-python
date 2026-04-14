from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenOut
from app.schemas.user import UserCreate, UserOut
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.verification_service import VerificationService
from app.uow.uow import UnitOfWork

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    uow = UnitOfWork(db)
    verification_service = VerificationService(
        repo=uow.verifications,
        email_svc=EmailService(),
    )
    service = AuthService(uow, verification_service)
    return service.register(data)


@router.post("/login", response_model=TokenOut)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService().login(data.email, data.password)
