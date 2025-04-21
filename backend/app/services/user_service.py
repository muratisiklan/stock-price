from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..models import User
from ..schemas.auth_schema import UserVerification
from ..routers.auth import bcrypt_context


def get_user_service(user: dict, db: Session):
    """Fetch user details."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    user_model = db.query(User).filter(User.id == user.get("id")).all()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    return user_model


def change_password_service(user: dict, db: Session, user_verification: UserVerification):
    """Change user's password."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if not user_model or not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


def change_phone_number_service(user: dict, db: Session, phone_number: str):
    """Change user's phone number."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
