from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..schemas.auth_schema import UserVerification
from .auth import get_current_user
from ..services.user_service import get_user_service, change_password_service, change_phone_number_service

router = APIRouter(prefix="/user", tags=["user"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    return get_user_service(user, db)


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    return change_password_service(user, db, user_verification)


@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    return change_phone_number_service(user, db, phone_number)
