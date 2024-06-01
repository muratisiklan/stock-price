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


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_divestments(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    return db.query(Divestment).filter(Divestment.owner_id == user.get("id")).all()


@router.get("/divestment/{id}", status_code=status.HTTP_200_OK)
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

# ? SOME OTHER COLUMNS FROM USER TABLE ARE INCREMENTED HERE


@router.post("/divesment", status_code=status.HTTP_201_CREATED)
async def create_divestment(
    user: user_dependency, db: db_dependency, request: DivestmentRequest,
):
    #!Add new divestment to db

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    divestment = Divestment(
        **request.model_dump(), owner_id=user.get("id"))

    #! Update information about user
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model:
        user_model.number_of_divestments += 1
        user_model.total_divestment += (request.unit_price *
                                        request.quantity)

    #! Update information about divested investment

    investment_model = db.query(Investment).filter(
        Investment.id == request.investment_id).first()

    diff = int(investment_model.quantity_remaining - request.quantity)
    if diff < 0:
        raise HTTPException(
            status_code=401, detail="Cant sell more than you have!")
    else:
        if not diff:
            investment_model.is_active = False

        investment_model.quantity_remaining = diff

    db.add(investment_model)
    db.add(user_model)
    db.add(divestment)
    db.commit()


@router.put("/divestment/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_divestment(
    user: user_dependency,
    db: db_dependency,
    divestment_request: DivestmentRequest,
    id: int = Path(gt=0),
):
    #TODO When divestment changed corresponding changes in users total divestment and total number of divestments columns should be updated
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    divestment = (
        db.query(Divestment)
        .filter(Divestment.id == id, Divestment.owner_id == user.get("id"))
        .first()
    )
    if divestment:
        divestment.date_divested = divestment_request.date_divested
        divestment.unit_price = divestment_request.unit_price
        divestment.quantity = divestment_request.quantity
    else:
        raise HTTPException(status_code=404, detail="Divestment not found")

    db.add(divestment)
    db.commit()


@router.delete("/divestment/{id}")
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
    if divestment:
        db.query(Divestment).filter(
            Divestment.id == id, Divestment.owner_id == user.get("id")
        ).delete()

    else:
        raise HTTPException(status_code=404, detail="Divestment not found!")
    db.commit()