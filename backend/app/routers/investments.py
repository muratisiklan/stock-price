from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..models import Investment, User
from .auth import get_current_user
from ..schemas.investment_schema import InvestmenRequest


router = APIRouter(prefix="/investment", tags=["investment"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_investments(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    return db.query(Investment).filter(Investment.owner_id == user.get("id")).all()


@router.get("/investment/{id}", status_code=status.HTTP_200_OK)
async def read_investment_by_id(
    user: user_dependency, db: db_dependency, id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    investment = (
        db.query(Investment)
        .filter(Investment.id == id, Investment.owner_id == user.get("id"))
        .first()
    )
    if investment:
        return investment
    else:
        raise HTTPException(status_code=404, detail="Investment not found!")

# ? SOME OTHER COLUMNS FROM USER TABLE ARE INCREMENTED HERE


@router.post("/investment", status_code=status.HTTP_201_CREATED)
async def create_investment(
    user: user_dependency, db: db_dependency, investment_request: InvestmenRequest
):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    investment = Investment(
        **investment_request.model_dump(), owner_id=user.get("id"))
    user = db.query(User).filter(User.id == user.get("id")).first()
    if user:
        user.number_of_investments += 1
        user.total_investment += (investment_request.unit_price *
                                  investment_request.quantity)

    db.add(user)
    db.add(investment)
    db.commit()


@router.put("/investment/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_investment(
    user: user_dependency,
    db: db_dependency,
    request: InvestmenRequest,
    id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    investment = (
        db.query(Investment)
        .filter(Investment.id == id, Investment.owner_id == user.get("id"))
        .first()
    )
    if investment:
        investment.title = request.title
        investment.company = request.company
        investment.description = request.description
        investment.date_invested = request.date_invested
        investment.unit_price = request.date_invested
        investment.quantity = request.quantity
    else:
        raise HTTPException(status_code=404, detail="Investment not found")

    db.add(investment)
    db.commit()


@router.delete("/investment/{id}")
async def delete_investment(
    user: user_dependency, db: db_dependency, id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    investment = (
        db.query(Investment)
        .filter(id == Investment.id, Investment.owner_id == user.get("id"))
        .first()
    )
    if investment:
        db.query(Investment).filter(
            Investment.id == id, Investment.owner_id == user.get("id")
        ).delete()

    else:
        raise HTTPException(status_code=404, detail="Investment not found!")
    db.commit()
