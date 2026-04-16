import random
import string
from datetime import datetime, timedelta, timezone

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.models.verification_code import VerificationCode
from app.services.email_service import EmailService

_jinja = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html"]),
)


def _generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


class VerificationService:
    def __init__(self, db: Session, email_svc: EmailService) -> None:
        self._db = db
        self._email = email_svc

    def send_email_verification(self, email: str, user_id: str | None = None) -> None:
        code = _generate_code()
        record = VerificationCode(
            email=email,
            code=code,
            userId=user_id,
            expiresAt=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        self._db.add(record)
        self._db.flush()
        body = _jinja.get_template("verify_email.html").render(code=code)
        self._email.send(email, "Verify your email", body)

    def send_password_reset(self, email: str, user_id: str | None = None) -> None:
        code = _generate_code()
        record = VerificationCode(
            email=email,
            code=code,
            userId=user_id,
            expiresAt=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        self._db.add(record)
        self._db.flush()
        body = _jinja.get_template("reset_password.html").render(code=code)
        self._email.send(email, "Reset your password", body)

    def verify_email(self, email: str, code: str) -> bool:
        now = datetime.now(timezone.utc)
        record = (
            self._db.query(VerificationCode)
            .filter(
                VerificationCode.email == email,
                VerificationCode.code == code,
                VerificationCode.expiresAt > now,
                VerificationCode.used.is_(False),
            )
            .first()
        )
        if record is None:
            return False
        record.used = True
        self._db.flush()
        return True
