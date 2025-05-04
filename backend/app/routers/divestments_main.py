from .auth import get_current_user
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from starlette import status

from ..database import get_db
from ..models import User, Investment, Divestment
from ..schemas.divestment_schema import DivestmentRequest
from ..schemas.divestment_main_schema import DivestmentMainRequest
from ..services.divestment_main_service import create_divestment_main_service, update_divestment_main_service, read_divestment_main_by_id_service, read_all_divestments_main_service, delete_divestment_main_service

router = APIRouter(prefix="/divestment_main", tags=["divestment_main"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_divestment_mains(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    divestment_mains = read_all_divestments_main_service(db, user)
    return divestment_mains


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def read_divestment_main_by_id(
    user: user_dependency, db: db_dependency, id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    divestment_main = read_divestment_main_by_id_service(db, user, id)
    if divestment_main:
        return divestment_main
    else:
        raise HTTPException(
            status_code=404, detail="Divestment Main not found!")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_divestment_main(
    user: user_dependency, db: db_dependency, request: DivestmentMainRequest,
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    divestment_main = create_divestment_main_service(db, user, request)
    return divestment_main


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_divestment_main(
    user: user_dependency,
    db: db_dependency,
    divestment_main_request: DivestmentMainRequest,
    id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    update_divestment_main_service(db, user, divestment_main_request, id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_divestment_main(
    user: user_dependency, db: db_dependency, id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")

    delete_divestment_main_service(db, user, id)
