from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class OperatorBase(BaseModel):
    name: str
    email: EmailStr
    max_load: int = 10
    is_active: bool = True


class OperatorCreate(OperatorBase):
    pass


class OperatorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    max_load: Optional[int] = None
    is_active: Optional[bool] = None


class OperatorResponse(OperatorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OperatorWithLoad(OperatorResponse):
    current_load: int = 0
