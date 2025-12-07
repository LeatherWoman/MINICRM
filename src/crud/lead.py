from typing import Optional

from sqlalchemy.orm import Session

from models.lead import Lead
from schemas.lead import LeadCreate, LeadUpdate

from .base import CRUDBase


class CRUDLead(CRUDBase[Lead, LeadCreate, LeadUpdate]):
    def get_by_external_id(self, db: Session, external_id: str) -> Optional[Lead]:
        return db.query(Lead).filter(Lead.external_id == external_id).first()

    def get_or_create_by_external_id(
        self, db: Session, external_id: str, defaults: dict = None
    ) -> Lead:
        lead = self.get_by_external_id(db, external_id)
        if not lead:
            create_data = {"external_id": external_id}
            if defaults:
                create_data.update(defaults)
            lead = self.create(db, obj_in=LeadCreate(**create_data))
        return lead


lead = CRUDLead(Lead)
