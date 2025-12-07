from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_database
from crud.lead import lead as lead_crud
from schemas.lead import LeadCreate, LeadResponse, LeadUpdate

router = APIRouter()


@router.post("/leads/", response_model=LeadResponse)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_database)):
    """Создание лида"""
    # Проверяем, нет ли уже лида с таким external_id
    existing = lead_crud.get_by_external_id(db, external_id=lead_in.external_id)
    if existing:
        raise HTTPException(
            status_code=400, detail="Lead with this external_id already exists"
        )

    lead = lead_crud.create(db, obj_in=lead_in)
    return LeadResponse.model_validate(lead)


@router.get("/leads/", response_model=List[LeadResponse])
def read_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_database)):
    """Получение списка лидов"""
    leads = lead_crud.get_multi(db, skip=skip, limit=limit)
    return [LeadResponse.model_validate(lead) for lead in leads]


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def read_lead(lead_id: int, db: Session = Depends(get_database)):
    """Получение лида по ID"""
    lead = lead_crud.get(db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return LeadResponse.model_validate(lead)


@router.put("/leads/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: int, lead_in: LeadUpdate, db: Session = Depends(get_database)):
    """Обновление лида"""
    lead = lead_crud.get(db, id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    updated_lead = lead_crud.update(db, db_obj=lead, obj_in=lead_in)
    return LeadResponse.model_validate(updated_lead)
