from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_database
from crud.operator import operator as operator_crud
from schemas.operator import (
    OperatorCreate,
    OperatorResponse,
    OperatorUpdate,
    OperatorWithLoad,
)

router = APIRouter()


@router.post("/operators/", response_model=OperatorResponse)
def create_operator(operator_in: OperatorCreate, db: Session = Depends(get_database)):
    """Создание оператора"""
    # Проверяем, нет ли уже оператора с таким email
    existing = operator_crud.get_by_email(db, email=operator_in.email)
    if existing:
        raise HTTPException(
            status_code=400, detail="Operator with this email already exists"
        )

    operator = operator_crud.create(db, obj_in=operator_in)
    return OperatorResponse.model_validate(operator)


@router.get("/operators/", response_model=List[OperatorResponse])
def read_operators(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_database)
):
    """Получение списка операторов"""
    operators = operator_crud.get_multi(db, skip=skip, limit=limit)
    return [OperatorResponse.model_validate(op) for op in operators]


@router.get("/operators/available", response_model=List[OperatorWithLoad])
def read_available_operators(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_database)
):
    """Получение доступных операторов (с нагрузкой)"""
    operators = operator_crud.get_available_operators(db, skip=skip, limit=limit)

    result = []
    for operator in operators:
        # Создаем объект OperatorWithLoad
        op_data = OperatorWithLoad(
            id=operator.id,
            name=operator.name,
            email=operator.email,
            max_load=operator.max_load,
            is_active=operator.is_active,
            created_at=operator.created_at,
            updated_at=operator.updated_at,
            current_load=getattr(operator, "current_load", 0),
        )
        result.append(op_data)

    return result


@router.get("/operators/{operator_id}", response_model=OperatorWithLoad)
def read_operator(operator_id: int, db: Session = Depends(get_database)):
    """Получение оператора по ID с нагрузкой"""
    operator = operator_crud.get_with_load(db, id=operator_id)
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")

    return OperatorWithLoad(
        id=operator.id,
        name=operator.name,
        email=operator.email,
        max_load=operator.max_load,
        is_active=operator.is_active,
        created_at=operator.created_at,
        updated_at=operator.updated_at,
        current_load=getattr(operator, "current_load", 0),
    )


@router.put("/operators/{operator_id}", response_model=OperatorResponse)
def update_operator(
    operator_id: int, operator_in: OperatorUpdate, db: Session = Depends(get_database)
):
    """Обновление оператора"""
    operator = operator_crud.get(db, id=operator_id)
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")

    updated_operator = operator_crud.update(db, db_obj=operator, obj_in=operator_in)
    return OperatorResponse.model_validate(updated_operator)


@router.delete("/operators/{operator_id}")
def delete_operator(operator_id: int, db: Session = Depends(get_database)):
    """Удаление оператора"""
    operator = operator_crud.get(db, id=operator_id)
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")

    operator_crud.remove(db, id=operator_id)
    return {"message": "Operator deleted successfully"}
