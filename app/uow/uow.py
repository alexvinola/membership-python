from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.repositories.verification_repository import VerificationRepository


class UnitOfWork:
    def __init__(self, db: Session) -> None:
        self._db = db
        self.users = UserRepository(db)
        self.verifications = VerificationRepository(db)

    def commit(self) -> None:
        self._db.commit()

    def rollback(self) -> None:
        self._db.rollback()