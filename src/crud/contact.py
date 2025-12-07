from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.contact import Contact
from schemas.contact import ContactCreateDB

from .base import CRUDBase


class CRUDContact(CRUDBase[Contact, ContactCreateDB, ContactCreateDB]):
    def get_by_lead_id(self, db: Session, lead_id: int) -> List[Contact]:
        return db.query(Contact).filter(Contact.lead_id == lead_id).all()

    def get_by_operator_id(self, db: Session, operator_id: int) -> List[Contact]:
        return db.query(Contact).filter(Contact.operator_id == operator_id).all()

    def get_active_by_operator_id(self, db: Session, operator_id: int) -> List[Contact]:
        return (
            db.query(Contact)
            .filter(Contact.operator_id == operator_id, Contact.is_active)
            .all()
        )

    def count_active_by_operator_id(self, db: Session, operator_id: int) -> int:
        return (
            db.query(func.count(Contact.id))
            .filter(Contact.operator_id == operator_id, Contact.is_active)
            .scalar()
            or 0
        )


contact = CRUDContact(Contact)
