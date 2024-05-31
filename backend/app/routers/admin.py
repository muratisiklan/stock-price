from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Investment
from typing import Annotated
from starlette import status
from .auth import get_current_user
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/investment", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    return db.query(Investment).all()


@router.delete("/investment/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investment(user: user_dependency, db: db_dependency, investment_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    investment_model = db.query(Investment).filter(
        Investment.id == investment_id).first()
    if investment_model is None:
        raise HTTPException(status_code=404, detail="Investment not found")

    db.query(Investment).filter(Investment.id == investment_id).delete()
    db.commit()
