import random
import string
from datetime import datetime, timedelta, timezone

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.repositories.verification_repository import VerificationRepository
from app.services.email_service import EmailService

_jinja = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html"]),
)


def _generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


class VerificationService:
    def __init__(self, repo: VerificationRepository, email_svc: EmailService) -> None:
        self._repo = repo
        self._email = email_svc

    def send_email_verification(self, email: str, user_id: str | None = None) -> None:
        code = _generate_code()
        expires = datetime.now(timezone.utc) + timedelta(minutes=10)
        self._repo.create(email=email, code=code, expires_at=expires, user_id=user_id)
        body = _jinja.get_template("verify_email.html").render(code=code)
        self._email.send(email, "Verify your email", body)

    def send_password_reset(self, email: str, user_id: str | None = None) -> None:
        code = _generate_code()
        expires = datetime.now(timezone.utc) + timedelta(minutes=10)
        self._repo.create(email=email, code=code, expires_at=expires, user_id=user_id)
        body = _jinja.get_template("reset_password.html").render(code=code)
        self._email.send(email, "Reset your password", body)

    def consume(self, email: str, code: str) -> str | None:
        """Returns the userId associated with the code, or None if invalid."""
        record = self._repo.get_valid(email=email, code=code)
        if record is None:
            return None
        self._repo.mark_used(record)
        return record.userId
