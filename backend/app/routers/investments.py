from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..models import Investment, User
from ..schemas.investment_schema import InvestmentRequest
from .auth import get_current_user

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
    user: user_dependency, db: db_dependency, request: InvestmentRequest
):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    investment = Investment(
        **request.model_dump(), owner_id=user.get("id"))
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user:
        user_model.number_of_investments += 1
        user_model.total_investment += (
            request.unit_price * request.quantity
        )

    db.add(user_model)
    db.add(investment)
    db.commit()


@router.put("/investment/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_investment(
    user: user_dependency,
    db: db_dependency,
    request: InvestmentRequest,
    id: int = Path(gt=0),
):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    investment = (
        db.query(Investment)
        .filter(Investment.id == id, Investment.owner_id == user.get("id"))
        .first()
    )
    old_quantity = investment.quantity
    old_price = investment.unit_price
    #! Update Investment

    if investment:
        investment.title = request.title
        investment.company = request.company
        investment.description = request.description
        investment.date_invested = request.date_invested
        investment.unit_price = request.unit_price
        investment.quantity = request.quantity
    else:
        raise HTTPException(status_code=404, detail="Investment not found")

    #! If quantity or price changed update users' total invested column
    if old_price != request.unit_price or old_quantity != request.quantity:
        diff = (request.unit_price * request.quantity) - (old_price * old_quantity)
        user_model = db.query(User).filter(User.id == user.get("id")).first()
        user_model.total_investment += diff
        db.add(user_model)


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

    #! When investment deleted, extract number of investments and investment amount
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    user_model.number_of_investments -= 1
    user_model.total_investment -= (investment.unit_price * investment.quantity)


    if investment:
        db.query(Investment).filter(
            Investment.id == id, Investment.owner_id == user.get("id")
        ).delete()

    else:
        raise HTTPException(status_code=404, detail="Investment not found!")
    db.add(user_model)
    db.commit()
