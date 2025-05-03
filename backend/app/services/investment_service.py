from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import Investment, User, Divestment
from ..schemas.investment_schema import InvestmentRequest


def get_all_investments(db: Session, user: dict):

    return db.query(Investment).filter(Investment.owner_id == user.get("id")).all()


def get_investment_by_id(db: Session, user: dict, investment_id: int):

    investment = db.query(Investment).filter(
        Investment.id == investment_id, Investment.owner_id == user.get("id")).first()
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found!")
    return investment


def create_new_investment(db: Session, user: dict, request: InvestmentRequest):

    investment = Investment(
        **request.model_dump(), owner_id=user.get("id"), quantity_remaining=request.quantity
    )
    user_model = db.query(User).filter(User.id == user.get("id")).first()

    if user_model:
        user_model.number_of_investments += 1
        user_model.total_investment += request.unit_price * request.quantity
        db.add(user_model)
        db.add(investment)
        db.commit()
        return {"id": investment.id, "message": "Investment created successfully"}
    raise HTTPException(status_code=404, detail="User not found!")


def update_existing_investment(db: Session, user: dict, request: InvestmentRequest, investment_id: int):

    # Find related investment

    investment = db.query(Investment).filter(
        Investment.id == investment_id, Investment.owner_id == user.get("id")).first()
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    # If divestment exist for current investment can not make changes

    if investment.quantity_remaining != investment.quantity:
        raise HTTPException(
            status_code=403, detail="Cannot change already divested investment!")

    old_quantity, old_price = investment.quantity, investment.unit_price
    investment.title, investment.company, investment.description = request.title, request.company, request.description
    investment.date_invested, investment.unit_price, investment.quantity = request.date_invested, request.unit_price, request.quantity

    investment.quantity_remaining += request.quantity - old_quantity

    if old_price != request.unit_price or old_quantity != request.quantity:
        diff_amount = (request.unit_price * request.quantity) - \
            (old_price * old_quantity)
        user_model = db.query(User).filter(User.id == user.get("id")).first()
        user_model.total_investment += diff_amount
        db.add(user_model)

    db.add(investment)
    db.commit()
    return {"message": "Investment updated successfully"}


def delete_existing_investment(db: Session, user: dict, investment_id: int):

    investment = db.query(Investment).filter(
        Investment.id == investment_id, Investment.owner_id == user.get("id")).first()
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found!")

    user_model = db.query(User).filter(User.id == user.get("id")).first()
    user_model.number_of_investments -= 1
    user_model.total_investment -= investment.unit_price * investment.quantity

    divestments = db.query(Divestment).filter(
        Divestment.investment_id == investment_id, Divestment.owner_id == user.get("id")).all()

    if divestments:
        user_model.number_of_divestments -= len(divestments)
        user_model.total_divestment -= sum(d.unit_price *
                                           d.quantity for d in divestments)
        db.query(Divestment).filter(Divestment.investment_id == investment_id,
                                    Divestment.owner_id == user.get("id")).delete(synchronize_session=False)

    db.query(Investment).filter(Investment.id == investment_id,
                                Investment.owner_id == user.get("id")).delete(synchronize_session=False)
    db.add(user_model)
    db.commit()
    return {"message": "Investment deleted successfully"}
