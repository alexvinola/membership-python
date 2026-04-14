from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.verification_code import VerificationCode


class VerificationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, email: str, code: str, expires_at: datetime, user_id: str | None = None) -> VerificationCode:
        record = VerificationCode(
            email=email,
            code=code,
            userId=user_id,
            expiresAt=expires_at,
        )
        self._db.add(record)
        self._db.flush()
        return record

    def get_valid(self, email: str, code: str) -> type[VerificationCode] | None:
        now = datetime.now(timezone.utc)
        return (
            self._db.query(VerificationCode)
            .filter(
                VerificationCode.email == email,
                VerificationCode.code == code,
                VerificationCode.expiresAt > now,
                VerificationCode.used.is_(False),
            )
            .first()
        )

    def mark_used(self, record: VerificationCode) -> None:
        record.used = True
        self._db.flush()
