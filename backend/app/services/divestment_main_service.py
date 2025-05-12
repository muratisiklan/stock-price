from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import Investment, DivestmentMain, User, Divestment
from ..schemas.divestment_main_schema import DivestmentMainRequest
from ..schemas.divestment_schema import DivestmentRequest
from .divestment_service import create_divestment_service, delete_divestment_service


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

    # Step 3.1 Update User table

    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model:
        user_model.number_of_divestments += 1
        user_model.total_divestment += (request.unit_price * request.quantity)

    try:
        db.add(divestment_main)
        db.add(user_model)
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

# TODO: Update logic will be created from scratch


def update_divestment_main_service(db: Session, user: dict, request: DivestmentMainRequest, id: int):
    # Step 1: Fetch divestment_main
    divestment_main = db.query(DivestmentMain).filter(
        DivestmentMain.id == id,
        DivestmentMain.owner_id == user.get("id")
    ).first()

    if divestment_main is None:
        raise HTTPException(status_code=404, detail="Divestment not found")

    # Step 2: Delete all related Divestments
    existing_divestments = db.query(Divestment).filter(
        Divestment.divestmentmain_id == id).all()
    for div in existing_divestments:
        delete_divestment_service(db, user, div.id)

    # Step 3: Fetch eligible investments again
    investments = db.query(Investment).filter(
        Investment.company == request.company,
        Investment.owner_id == user["id"],
        Investment.is_active == True,
        Investment.date_invested <= request.date_divested,
    ).order_by(Investment.date_invested).all()

    if not investments:
        raise HTTPException(
            status_code=404, detail="No eligible investments found for divestment.")

    # Step 4: Validate quantity availability
    total_available = sum(inv.quantity_remaining for inv in investments)
    if total_available < request.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough quantity to divest. Available: {total_available}, Requested: {request.quantity}"
        )

    # Step 5: Update DivestmentMain
    divestment_main.date_divested = request.date_divested
    divestment_main.quantity = request.quantity
    divestment_main.unit_price = request.unit_price
    divestment_main.company = request.company
    divestment_main.revenue = request.unit_price * request.quantity

    # Step 6: Adjust User model
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model:
        old_total = divestment_main.quantity * divestment_main.unit_price
        new_total = request.unit_price * request.quantity
        user_model.total_divestment += (new_total - old_total)

    # Step 7: Re-allocate new Divestments
    try:
        db.add(divestment_main)
        db.add(user_model)
        db.flush()

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
                db=db,
                user=user,
                request=divestment_request,
                inv_id=inv.id,
                div_main_id=divestment_main.id
            )
            remaining_qty -= allocated_qty

        db.commit()
        db.refresh(divestment_main)
        return divestment_main

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating divestment_main: {str(e)}")


# TODO: Delete logic will be created from scratch


def delete_divestment_main_service(db: Session, user: dict, id: int):
    divestment_main = db.query(DivestmentMain).filter(
        DivestmentMain.id == id, DivestmentMain.owner_id == user.get("id")).first()

    if divestment_main is None:
        raise HTTPException(status_code=404, detail="Divestment not found!")

    # Find and delete divestments related with this divestment_main

    divestments = db.query(Divestment).where(
        Divestment.divestmentmain_id == id).all()
    for div in divestments:
        delete_divestment_service(db, user, div.id)

    # Update user's total number of divestments and total divested amount
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model:
        user_model.number_of_divestments -= 1
        user_model.total_divestment -= (divestment_main.unit_price *
                                        divestment_main.quantity)

    try:

        db.delete(divestment_main)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting divestment: {str(e)}")
