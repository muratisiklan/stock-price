from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..schemas.investment_schema import InvestmentRequest
from .auth import get_current_user
from ..services.investment_service import (
    get_all_investments,
    get_investment_by_id,
    create_new_investment,
    update_existing_investment,
    delete_existing_investment,
)

router = APIRouter(prefix="/investment", tags=["investment"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_investments(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    return get_all_investments(db, user)


@router.get("/investment/{id}", status_code=status.HTTP_200_OK)
async def read_investment_by_id(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    return get_investment_by_id(db, user, id)


@router.post("/investment", status_code=status.HTTP_201_CREATED)
async def create_investment(user: user_dependency, db: db_dependency, request: InvestmentRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    return create_new_investment(db, user, request)


@router.put("/investment/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_investment(user: user_dependency, db: db_dependency, request: InvestmentRequest, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    return update_existing_investment(db, user, request, id)


@router.delete("/investment/{id}")
async def delete_investment(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    return delete_existing_investment(db, user, id)
