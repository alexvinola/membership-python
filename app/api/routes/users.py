from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])
_bearer = HTTPBearer()


def _current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise UnauthorizedException()
    return user_id


@router.get("/me", response_model=UserOut)
def get_me(
    user_id: str = Depends(_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise NotFoundException("User not found")
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    user_id: str = Depends(_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise NotFoundException("User not found")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
