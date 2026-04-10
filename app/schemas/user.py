from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.models.user import Plan


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    image: str | None = None


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    email: EmailStr
    name: str | None
    plan: Plan
    status: str
    emailVerified: datetime | None
    image: str | None
    trialEndsAt: datetime | None
