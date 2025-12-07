from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class LeadBase(BaseModel):
    external_id: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
