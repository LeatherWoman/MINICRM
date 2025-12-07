from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SourceBase(BaseModel):
    name: str
    bot_token: str
    description: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    bot_token: Optional[str] = None
    description: Optional[str] = None


class SourceResponse(SourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SourceWeightBase(BaseModel):
    operator_id: int
    weight: int = 1


class SourceWeightCreate(SourceWeightBase):
    pass


class SourceWeightResponse(SourceWeightBase):
    id: int
    source_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SourceWithWeights(SourceResponse):
    weights: List[SourceWeightResponse] = []
