from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import Investment, DivestmentMain, User
from ..schemas.divestment_main_schema import DivestmentMainRequest
from ..schemas.divestment_schema import DivestmentRequest
from .divestment_service import create_divestment_service, update_divestment_service


def read_all_divestments_main_service(db: Session, user: dict):
    return db.query(DivestmentMain).filter(DivestmentMain.owner_id == user.get("id")).all()


def read_divestment_main_by_id_service(db: Session, user: dict, id: int):
    return db.query(DivestmentMain).filter(DivestmentMain.id == id, DivestmentMain.owner_id == user.get("id")).first()


def create_divestment_main_service(db: Session, user: dict, request: DivestmentMainRequest):
    # Step 1: Fetch active investments for the company owned by user before divestment date
    investments = db.query(Investment).filter(
        Investment.company == request.company,
        Investment.owner_id == user["id"],
        Investment.is_active == True,
        Investment.date_invested <= request.date_divested,

    ).order_by(Investment.date_invested).all()

    if not investments:
        raise HTTPException(
            status_code=404, detail="No eligible investments found for divestment.")

    # Step 2: Validate if enough quantity is available
    total_available = sum(inv.quantity_remaining for inv in investments)
    if total_available < request.quantity:
        raise HTTPException(
            status_code=400, detail=f"Not enough remaining quantity to divest. Available: {total_available}, Requested: {request.quantity}")

    # Step 3: Create DivestmentMain
    divestment_main = DivestmentMain(
        **request.model_dump(),
        owner_id=user["id"],
        revenue=request.quantity * request.unit_price,
    )

    try:
        db.add(divestment_main)
        db.flush()  # Ensures divestment_main.id is available for related divestments

        # Step 4: Allocate quantity to divest from oldest investments
        remaining_qty = request.quantity
        for inv in investments:
            if remaining_qty <= 0:
                break

            allocated_qty = min(inv.quantity_remaining, remaining_qty)
            divestment_request = DivestmentRequest(
                quantity=allocated_qty,
                unit_price=request.unit_price,
                date_invested=inv.date_invested,
                date_divested=request.date_divested,
                company=request.company,
            )

            create_divestment_service(
                db=db, user=user, request=divestment_request, inv_id=inv.id, div_main_id=divestment_main.id)
            remaining_qty -= allocated_qty
            # inv.quantity_remaining -= allocated_qty
            # if inv.quantity_remaining == 0:
            #     inv.is_active = False

        db.commit()
        db.refresh(divestment_main)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating divestment_main: {str(e)}")

    return divestment_main

#TODO: Update logic will be created from scratch
def update_divestment_main_service(db: Session, user: dict, request: DivestmentMainRequest, id: int):
    divestment_main = db.query(DivestmentMain).filter(
        DivestmentMain.id == id, DivestmentMain.owner_id == user.get("id")).first()

    investment = db.query(Investment).filter(Investment.id == divestment_main.investment_id,
                                             Investment.owner_id == user.get("id")).first()

    if divestment_main is None:
        raise HTTPException(status_code=404, detail="Divestment not found")

    new_quantity = request.quantity
    new_price = request.unit_price

    old_quantity = divestment_main.quantity
    old_price = divestment_main.unit_price

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
    divestment_main.date_divested = request.date_divested
    divestment_main.unit_price = request.unit_price
    divestment_main.quantity = new_quantity
    divestment_main.revenue = new_quantity * request.unit_price
    divestment_main.net_return = new_quantity * \
        (request.unit_price - investment.unit_price)
    divestment_main.cost_of_investment = new_quantity * investment.unit_price
    try:
        db.add(divestment_main)
        db.add(user_model)
        db.add(investment)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating divestment: {str(e)}")

#TODO: Delete logic will be created from scratch
def delete_divestment_main_service(db: Session, user: dict, id: int):
    divestment_main = db.query(DivestmentMain).filter(
        DivestmentMain.id == id, DivestmentMain.owner_id == user.get("id")).first()

    if divestment_main is None:
        raise HTTPException(status_code=404, detail="Divestment not found!")

    # Update user's total number of divestments and total divested amount
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model:
        user_model.number_of_divestments -= 1
        user_model.total_divestment -= (divestment_main.unit_price *
                                        divestment_main.quantity)

    # Update quantity remaining for specific investment
    investment_model = db.query(Investment).filter(
        Investment.id == divestment_main.investment_id).first()
    if investment_model:
        investment_model.quantity_remaining += divestment_main.quantity
        investment_model.is_active = True

    try:
        db.delete(divestment_main)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting divestment: {str(e)}")
