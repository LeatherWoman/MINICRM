from typing import List, Optional

from sqlalchemy.orm import Session

from models.source import Source, SourceWeight
from schemas.source import SourceCreate, SourceUpdate, SourceWeightCreate

from .base import CRUDBase


class CRUDSource(CRUDBase[Source, SourceCreate, SourceUpdate]):
    def get_by_bot_token(self, db: Session, bot_token: str) -> Optional[Source]:
        return db.query(Source).filter(Source.bot_token == bot_token).first()

    def add_weight(
        self, db: Session, source_id: int, weight_in: SourceWeightCreate
    ) -> SourceWeight:
        weight = SourceWeight(
            source_id=source_id,
            operator_id=weight_in.operator_id,
            weight=weight_in.weight,
        )
        db.add(weight)
        db.commit()
        db.refresh(weight)
        return weight

    def get_weights(self, db: Session, source_id: int) -> List[SourceWeight]:
        return db.query(SourceWeight).filter(SourceWeight.source_id == source_id).all()

    def remove_weight(
        self, db: Session, source_id: int, operator_id: int
    ) -> SourceWeight:
        weight = (
            db.query(SourceWeight)
            .filter(
                SourceWeight.source_id == source_id,
                SourceWeight.operator_id == operator_id,
            )
            .first()
        )
        if weight:
            db.delete(weight)
            db.commit()
        return weight


source = CRUDSource(Source)
