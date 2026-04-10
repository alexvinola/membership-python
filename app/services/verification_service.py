import secrets
from datetime import datetime, timedelta, timezone

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.repositories.verification_repository import VerificationRepository
from app.services.email_service import EmailService

_jinja = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html"]),
)


class VerificationService:
    def __init__(self, repo: VerificationRepository, email_svc: EmailService) -> None:
        self._repo = repo
        self._email = email_svc

    def send_email_verification(self, user_id: int, email: str) -> None:
        code = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=24)
        self._repo.create(user_id, code, "email_verify", expires)
        body = _jinja.get_template("verify_email.html").render(token=code)
        self._email.send(email, "Verify your email", body)

    def send_password_reset(self, user_id: int, email: str) -> None:
        code = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        self._repo.create(user_id, code, "password_reset", expires)
        body = _jinja.get_template("reset_password.html").render(token=code)
        self._email.send(email, "Reset your password", body)

    def consume(self, code: str, purpose: str) -> int | None:
        record = self._repo.get_valid(code, purpose)
        if record is None:
            return None
        self._repo.mark_used(record)
        return record.user_id
