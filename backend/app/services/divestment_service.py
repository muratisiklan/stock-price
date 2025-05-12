from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import User, Investment, Divestment
from ..schemas.divestment_schema import DivestmentRequest


def read_all_divestments_service(db: Session, user: dict):
    return db.query(Divestment).filter(Divestment.owner_id == user.get("id")).all()


def read_divestment_by_id_service(db: Session, user: dict, id: int):
    return db.query(Divestment).filter(Divestment.id == id, Divestment.owner_id == user.get("id")).first()


def create_divestment_service(db: Session, user: dict, request: DivestmentRequest, inv_id: int, div_main_id: int):
    # Fetch the investment related to the divestment
    investment_model = db.query(Investment).filter(
        Investment.id == inv_id, Investment.owner_id == user.get("id")).first()

    if investment_model is None:
        raise HTTPException(status_code=404, detail="Investment not found!")

    # Check if the quantity to divest is valid
    if investment_model.quantity_remaining < request.quantity:
        raise HTTPException(
            status_code=400, detail="Cannot divest more than the remaining quantity.")
    if investment_model.date_invested > request.date_divested:
        raise HTTPException(
            status_code=400, detail="Cannot divest before the respective investment's date!")

    # Create the new divestment
    divestment = Divestment(
        **request.model_dump(),
        investment_id=inv_id,
        owner_id=user.get("id"),
        company=investment_model.company,
        revenue=request.quantity * request.unit_price,
        cost_of_investment=request.quantity * investment_model.unit_price,
        net_return=request.quantity *
        (request.unit_price - investment_model.unit_price),
        date_invested=investment_model.date_invested,
        divestmentmain_id=div_main_id,
    )

    # Update user and investment details Will be updated in divestment_main service
    # user_model = db.query(User).filter(User.id == user.get("id")).first()
    # if user_model:
    #     user_model.number_of_divestments += 1
    #     user_model.total_divestment += (request.unit_price * request.quantity)

    if investment_model:
        investment_model.quantity_remaining -= request.quantity
        if investment_model.quantity_remaining == 0:
            investment_model.is_active = False

    try:
        db.add(divestment)
        # db.add(user_model)
        db.commit()
        db.refresh(divestment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating divestment: {str(e)}")

    return divestment


def delete_divestment_service(db: Session, user: dict, id: int):
    divestment = db.query(Divestment).filter(
        Divestment.id == id, Divestment.owner_id == user.get("id")).first()

    if divestment is None:
        raise HTTPException(status_code=404, detail="Divestment not found!")

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
