from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.contact import Contact
from models.operator import Operator
from schemas.operator import OperatorCreate, OperatorUpdate

from .base import CRUDBase


class CRUDOperator(CRUDBase[Operator, OperatorCreate, OperatorUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[Operator]:
        return db.query(Operator).filter(Operator.email == email).first()

    def get_with_load(self, db: Session, id: int) -> Optional[Operator]:
        operator = db.query(Operator).filter(Operator.id == id).first()
        if operator:
            # Считаем текущую нагрузку (количество активных контактов)
            load = (
                db.query(func.count(Contact.id))
                .filter(Contact.operator_id == id, Contact.is_active)
                .scalar()
            )
            # Добавляем нагрузку как атрибут объекта
            setattr(operator, "current_load", load or 0)
        return operator

    def get_available_operators(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Operator]:
        # Получаем операторов с текущей нагрузкой
        operators = db.query(Operator).filter(Operator.is_active).all()
        result = []
        for operator in operators:
            load = (
                db.query(func.count(Contact.id))
                .filter(Contact.operator_id == operator.id, Contact.is_active)
                .scalar()
            )
            if load is None or load < operator.max_load:
                operator.current_load = load or 0
                result.append(operator)
        return result[skip : skip + limit]


operator = CRUDOperator(Operator)
