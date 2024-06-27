from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..models import User, Divestment, Investment
from ..schemas.divestment_schema import DivestmentRequest
from .auth import get_current_user

router = APIRouter(prefix="/divestment", tags=["divestment"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/",  status_code=status.HTTP_200_OK)
async def read_all_divestments(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    divestments = db.query(Divestment).filter(
        Divestment.owner_id == user.get("id")).all()
    return divestments


@router.get("/{id}",  status_code=status.HTTP_200_OK)
async def read_divestment_by_id(
    user: user_dependency, db: db_dependency, id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    divestment = (
        db.query(Divestment)
        .filter(Divestment.id == id, Divestment.owner_id == user.get("id"))
        .first()
    )

    if divestment:
        return divestment
    else:
        raise HTTPException(status_code=404, detail="Divestment not found!")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_divestment(
    user: user_dependency, db: db_dependency, request: DivestmentRequest,
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    # Fetch the investment related to the divestment
    investment_model = db.query(Investment).filter(
        Investment.id == request.investment_id, Investment.owner_id == user.get("id")).first()

    if investment_model is None:
        raise HTTPException(status_code=404, detail="Investment not found!")

    # Check if the quantity to divest is valid
    if investment_model.quantity_remaining < request.quantity:
        raise HTTPException(
            status_code=400, detail="Cannot divest more than the remaining quantity.")

    # Create the new divestment
    divestment = Divestment(
        **request.model_dump(),
        owner_id=user.get("id"),
        company=investment_model.company,
        revenue = request.quantity * request.unit_price,
        cost_of_investment = request.quantity * investment_model.unit_price,
        net_return= request.quantity * (request.unit_price - investment_model.unit_price),
        date_invested = investment_model.date_invested
    )

    # Update user and investment details
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model:
        user_model.number_of_divestments += 1
        user_model.total_divestment += (request.unit_price * request.quantity)

    if investment_model:
        investment_model.quantity_remaining -= request.quantity
        if investment_model.quantity_remaining == 0:
            investment_model.is_active = False

    try:
        db.add(divestment)
        db.commit()
        db.refresh(divestment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating divestment: {str(e)}")

    return divestment


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_divestment(
    user: user_dependency,
    db: db_dependency,
    divestment_request: DivestmentRequest,
    id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    divestment = (
        db.query(Divestment)
        .filter(Divestment.id == id, Divestment.owner_id == user.get("id"))
        .first()
    )

    investment = db.query(Investment).filter(Investment.id == divestment.investment_id,
                                             Investment.owner_id == user.get("id")).first()

    if divestment is None:
        raise HTTPException(status_code=404, detail="Divestment not found")

    # Update divestment details
    divestment.date_divested = divestment_request.date_divested
    divestment.unit_price = divestment_request.unit_price
    divestment.quantity = divestment_request.quantity
    divestment.revenue = divestment_request.quantity * divestment_request.unit_price
    divestment.net_return = divestment_request.quantity * \
        (divestment_request.unit_price - investment.unit_price)

    try:
        db.add(divestment)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating divestment: {str(e)}")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_divestment(
    user: user_dependency, db: db_dependency, id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    divestment = (
        db.query(Divestment)
        .filter(Divestment.id == id, Divestment.owner_id == user.get("id"))
        .first()
    )

    if divestment is None:
        raise HTTPException(status_code=404, detail="Divestment not found!")

    # Update user's total number of divestments and total divested amount
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model:
        user_model.number_of_divestments -= 1
        user_model.total_divestment -= (divestment.unit_price *
                                        divestment.quantity)

    # Update quantity remaining for specific investment
    investment_model = db.query(Investment).filter(
        Investment.id == divestment.investment_id).first()
    if investment_model:
        investment_model.quantity_remaining += divestment.quantity
        investment_model.is_active = True

    try:
        db.delete(divestment)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting divestment: {str(e)}")
