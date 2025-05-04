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
        db.add(user_model)
        db.commit()
        db.refresh(divestment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating divestment: {str(e)}")

    return divestment


def update_divestment_service(db: Session, user: dict, divestment_request: DivestmentRequest, id: int):
    divestment = db.query(Divestment).filter(
        Divestment.id == id, Divestment.owner_id == user.get("id")).first()

    investment = db.query(Investment).filter(Investment.id == divestment.investment_id,
                                             Investment.owner_id == user.get("id")).first()

    if divestment is None:
        raise HTTPException(status_code=404, detail="Divestment not found")

    new_quantity = divestment_request.quantity
    new_price = divestment_request.unit_price

    old_quantity = divestment.quantity
    old_price = divestment.unit_price

    if new_price != old_price or new_quantity != old_quantity:
        # Calculate the change in quantity
        quantity_diff = new_quantity - old_quantity

        # Validate quantity BEFORE making any updates
        if investment.quantity_remaining - quantity_diff < 0:
            raise HTTPException(
                status_code=404, detail="Cannot divest more than quantity remaining")

        # Proceed with updates
        diff_amount = (new_price * new_quantity) - (old_price * old_quantity)

        user_model = db.query(User).filter(User.id == user.get("id")).first()
        user_model.total_divestment += diff_amount

        investment.quantity_remaining -= quantity_diff
        investment.is_active = investment.quantity_remaining > 0

    # Update divestment details
    divestment.date_divested = divestment_request.date_divested
    divestment.unit_price = divestment_request.unit_price
    divestment.quantity = new_quantity
    divestment.revenue = new_quantity * divestment_request.unit_price
    divestment.net_return = new_quantity * \
        (divestment_request.unit_price - investment.unit_price)
    divestment.cost_of_investment = new_quantity * investment.unit_price
    try:
        db.add(divestment)
        db.add(user_model)
        db.add(investment)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating divestment: {str(e)}")


def delete_divestment_service(db: Session, user: dict, id: int):
    divestment = db.query(Divestment).filter(
        Divestment.id == id, Divestment.owner_id == user.get("id")).first()

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
