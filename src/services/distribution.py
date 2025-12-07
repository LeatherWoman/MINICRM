import random
from typing import Optional

from sqlalchemy.orm import Session

from crud.contact import contact as contact_crud
from crud.operator import operator as operator_crud
from models.operator import Operator
from models.source import SourceWeight


class DistributionService:
    @staticmethod
    def select_operator(
        db: Session, source_id: int, exclude_operator_id: Optional[int] = None
    ) -> Optional[Operator]:
        """
        Выбор оператора для источника с учетом весов и нагрузки.

        Алгоритм:
        1. Получаем все веса операторов для источника
        2. Фильтруем активных операторов, не превысивших лимит
        3. Выбираем оператора по весам (вероятностный выбор)
        """
        # Получаем веса операторов для источника
        weights = (
            db.query(SourceWeight).filter(SourceWeight.source_id == source_id).all()
        )

        if not weights:
            return None

        # Подготовка данных для выбора
        available_operators = []
        available_weights = []

        for weight in weights:
            # Получаем оператора с текущей нагрузкой
            op = operator_crud.get_with_load(db, weight.operator_id)

            # Проверяем условия
            if (
                op
                and op.is_active
                and op.current_load < op.max_load
                and op.id != exclude_operator_id
            ):
                available_operators.append(op)
                available_weights.append(weight.weight)

        if not available_operators:
            return None

        # Вероятностный выбор оператора на основе весов
        total_weight = sum(available_weights)
        if total_weight == 0:
            return None

        # Выбор случайного оператора с учетом весов
        rand = random.uniform(0, total_weight)
        cumulative = 0

        for i, weight in enumerate(available_weights):
            cumulative += weight
            if rand <= cumulative:
                return available_operators[i]

        # На всякий случай возвращаем первого
        return available_operators[0]

    @staticmethod
    def get_operator_load(db: Session, operator_id: int) -> int:
        """Получить текущую нагрузку оператора"""
        return contact_crud.count_active_by_operator_id(db, operator_id)


distribution_service = DistributionService()
