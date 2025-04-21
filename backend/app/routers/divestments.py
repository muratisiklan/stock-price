from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..models import User, Investment, Divestment
from ..schemas.divestment_schema import DivestmentRequest
from .auth import get_current_user
from ..services.divestment_service import create_divestment_service, update_divestment_service, delete_divestment_service, read_all_divestments_service, read_divestment_by_id_service

router = APIRouter(prefix="/divestment", tags=["divestment"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_divestments(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    divestments = read_all_divestments_service(db, user)
    return divestments


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def read_divestment_by_id(
    user: user_dependency, db: db_dependency, id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    divestment = read_divestment_by_id_service(db, user, id)
    if divestment:
        return divestment
    else:
        raise HTTPException(status_code=404, detail="Divestment not found!")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_divestment(
    user: user_dependency, db: db_dependency, request: DivestmentRequest, inv_id: int = Query()
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    
    divestment = create_divestment_service(db, user, request, inv_id)
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

    update_divestment_service(db, user, divestment_request, id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_divestment(
    user: user_dependency, db: db_dependency, id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    delete_divestment_service(db, user, id)
