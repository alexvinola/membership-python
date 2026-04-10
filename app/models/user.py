import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Plan(str, enum.Enum):
    FREE = "FREE"
    PRO = "PRO"
    PREMIUM = "PREMIUM"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    emailVerified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    stripeCustomerId: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    subscriptionId: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    plan: Mapped[Plan] = mapped_column(Enum(Plan, native_enum=False), default=Plan.FREE, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    trialEndsAt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    webhookEvents = relationship("WebhookEvent", back_populates="user")
    verificationCodes = relationship("VerificationCode", back_populates="user")
