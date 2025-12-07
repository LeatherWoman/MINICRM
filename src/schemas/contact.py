from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ContactBase(BaseModel):
    lead_external_id: str
    source_id: int
    message: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactCreateDB(BaseModel):
    """Схема для создания контакта в БД (используется внутри системы)"""

    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    message: Optional[str] = None
    status: str = "new"
    is_active: bool = True


class ContactResponse(BaseModel):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int]
    message: Optional[str]
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactWithDetails(ContactResponse):
    lead_external_id: str
    lead_phone: Optional[str]
    lead_email: Optional[str]
    operator_name: Optional[str]
    source_name: str
