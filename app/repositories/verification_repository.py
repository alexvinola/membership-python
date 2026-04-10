from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.verification_code import VerificationCode


class VerificationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, user_id: int, code: str, purpose: str, expires_at: datetime) -> VerificationCode:
        record = VerificationCode(
            user_id=user_id,
            code=code,
            purpose=purpose,
            expires_at=expires_at,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def get_valid(self, code: str, purpose: str) -> VerificationCode | None:
        now = datetime.now(timezone.utc)
        return (
            self._db.query(VerificationCode)
            .filter(
                VerificationCode.code == code,
                VerificationCode.purpose == purpose,
                VerificationCode.expires_at > now,
                VerificationCode.used_at.is_(None),
            )
            .first()
        )

    def mark_used(self, record: VerificationCode) -> None:
        record.used_at = datetime.now(timezone.utc)
        self._db.commit()
