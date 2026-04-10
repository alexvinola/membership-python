from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserOut, UserUpdate
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter(prefix="/users", tags=["users"])
_bearer = HTTPBearer()


def _current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> int:
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise UnauthorizedException()
    return int(user_id)


@router.get("/me", response_model=UserOut)
def get_me(
    user_id: int = Depends(_current_user_id),
    db: Session = Depends(get_db),
):
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise NotFoundException("User not found")
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    user_id: int = Depends(_current_user_id),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise NotFoundException("User not found")
    return repo.update(user, **data.model_dump(exclude_none=True))
