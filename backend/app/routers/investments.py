from fastapi import APIRouter, Depends, HTTPException, Path
from ..database import get_db
from sqlalchemy.orm import Session
from .auth import get_current_user
from starlette import status
from typing import Annotated
from ..models import Investment
from ..schemas import InvestmenRequest
import sys
sys.path.append("..")


router = APIRouter(
    prefix="/investment",
    tags=["investment"]
)

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_investments(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    return db.query(Investment).filter(Investment.owner_id == user.get("id")).all()


@router.get("/investment/{id}", status_code=status.HTTP_200_OK)
async def read_investment_by_id(user: user_dependency,
                                db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    investment = db.query(Investment).filter(
        Investment.id == id, Investment.owner_id == user.get("id")).first()
    if investment:
        return investment
    else:
        raise HTTPException(status_code=404, detail="Investment not found!")


@router.post("/investment", status_code=status.HTTP_201_CREATED)
async def create_investment(user: user_dependency,
                            db: db_dependency, todo_request: InvestmenRequest):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    investment = Investment(**todo_request.model_dump(),
                            owner_id=user.get("id"))

    db.add(investment)
    db.commit()


@router.put("/investment/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_investment(user: user_dependency,
                            db: db_dependency,  request: InvestmenRequest, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    investment = db.query(Investment).filter(
        Investment.id == id, Investment.owner_id == user.get("id")).first()
    if investment:
        investment.title = request.title
        investment.description = request.description
        investment.priority = request.priority
        investment.company = request.company
        investment.complete = request.complete
    else:
        raise HTTPException(status_code=404, detail="Investment not found")

    db.add(investment)
    db.commit()


@router.delete("/investment/{id}")
async def delete_investment(user: user_dependency,
                            db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    investment = db.query(Investment).filter(
        id == Investment.id, Investment.owner_id == user.get("id")).first()
    if investment:
        db.query(Investment).filter(Investment.id == id,
                                    Investment.owner_id == user.get("id")).delete()

    else:
        raise HTTPException(status_code=404, detail="Investment not found!")
    db.commit()
