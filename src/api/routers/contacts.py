from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_database
from crud.contact import contact as contact_crud
from crud.lead import lead as lead_crud
from crud.source import source as source_crud
from schemas.contact import (
    ContactCreate,
    ContactCreateDB,
    ContactResponse,
    ContactWithDetails,
)
from services.distribution import distribution_service

router = APIRouter()


@router.post("/contacts/", response_model=ContactResponse)
def create_contact(contact_in: ContactCreate, db: Session = Depends(get_database)):
    """
    Создание нового обращения (контакта).
    """
    # 1. Находим или создаем лида
    defaults = {}
    if contact_in.phone:
        defaults["phone"] = contact_in.phone
    if contact_in.email:
        defaults["email"] = contact_in.email
    if contact_in.full_name:
        defaults["full_name"] = contact_in.full_name

    lead = lead_crud.get_or_create_by_external_id(
        db, external_id=contact_in.lead_external_id, defaults=defaults
    )

    # 2. Проверяем существование источника
    source = source_crud.get(db, id=contact_in.source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # 3. Выбираем оператора
    operator = distribution_service.select_operator(db, contact_in.source_id)

    # 4. Создаем контакт
    contact_data = ContactCreateDB(
        lead_id=lead.id,
        source_id=contact_in.source_id,
        operator_id=operator.id if operator else None,
        message=contact_in.message,
        status="new",
        is_active=True,
    )

    contact = contact_crud.create(db, obj_in=contact_data)

    return ContactResponse(
        id=contact.id,
        lead_id=contact.lead_id,
        source_id=contact.source_id,
        operator_id=contact.operator_id,
        message=contact.message,
        status=contact.status,
        is_active=contact.is_active,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
    )


@router.get("/contacts/", response_model=List[ContactWithDetails])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_database)):
    """Получение списка контактов с деталями"""
    contacts = contact_crud.get_multi(db, skip=skip, limit=limit)

    result = []
    for contact in contacts:
        # Создаем объект ContactWithDetails
        contact_dict = ContactWithDetails(
            id=contact.id,
            lead_id=contact.lead_id,
            source_id=contact.source_id,
            operator_id=contact.operator_id,
            message=contact.message,
            status=contact.status,
            is_active=contact.is_active,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            lead_external_id=contact.lead.external_id if contact.lead else "",
            lead_phone=contact.lead.phone if contact.lead else None,
            lead_email=contact.lead.email if contact.lead else None,
            operator_name=contact.operator.name if contact.operator else None,
            source_name=contact.source.name if contact.source else "",
        )
        result.append(contact_dict)

    return result


@router.get("/contacts/by-lead/{lead_id}", response_model=List[ContactWithDetails])
def read_contacts_by_lead(lead_id: int, db: Session = Depends(get_database)):
    """Получение контактов по лиду"""
    contacts = contact_crud.get_by_lead_id(db, lead_id=lead_id)

    result = []
    for contact in contacts:
        contact_dict = ContactWithDetails(
            id=contact.id,
            lead_id=contact.lead_id,
            source_id=contact.source_id,
            operator_id=contact.operator_id,
            message=contact.message,
            status=contact.status,
            is_active=contact.is_active,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            lead_external_id=contact.lead.external_id if contact.lead else "",
            lead_phone=contact.lead.phone if contact.lead else None,
            lead_email=contact.lead.email if contact.lead else None,
            operator_name=contact.operator.name if contact.operator else None,
            source_name=contact.source.name if contact.source else "",
        )
        result.append(contact_dict)

    return result


@router.get(
    "/contacts/by-operator/{operator_id}", response_model=List[ContactWithDetails]
)
def read_contacts_by_operator(operator_id: int, db: Session = Depends(get_database)):
    """Получение контактов по оператору"""
    contacts = contact_crud.get_by_operator_id(db, operator_id=operator_id)

    result = []
    for contact in contacts:
        contact_dict = ContactWithDetails(
            id=contact.id,
            lead_id=contact.lead_id,
            source_id=contact.source_id,
            operator_id=contact.operator_id,
            message=contact.message,
            status=contact.status,
            is_active=contact.is_active,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            lead_external_id=contact.lead.external_id if contact.lead else "",
            lead_phone=contact.lead.phone if contact.lead else None,
            lead_email=contact.lead.email if contact.lead else None,
            operator_name=contact.operator.name if contact.operator else None,
            source_name=contact.source.name if contact.source else "",
        )
        result.append(contact_dict)

    return result


@router.put("/contacts/{contact_id}/close")
def close_contact(contact_id: int, db: Session = Depends(get_database)):
    """Закрытие контакта (снижение нагрузки оператора)"""
    contact = contact_crud.get(db, id=contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.is_active = False
    contact.status = "closed"
    db.commit()
    db.refresh(contact)

    return {"message": "Contact closed successfully"}
