from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_database
from crud.source import source as source_crud
from schemas.source import (
    SourceCreate,
    SourceResponse,
    SourceWeightCreate,
    SourceWeightResponse,
    SourceWithWeights,
)

router = APIRouter()


@router.post("/sources/", response_model=SourceResponse)
def create_source(source_in: SourceCreate, db: Session = Depends(get_database)):
    """Создание источника"""
    # Проверяем, нет ли уже источника с таким bot_token
    existing = source_crud.get_by_bot_token(db, bot_token=source_in.bot_token)
    if existing:
        raise HTTPException(
            status_code=400, detail="Source with this bot_token already exists"
        )

    source = source_crud.create(db, obj_in=source_in)
    return SourceResponse.model_validate(source)


@router.get("/sources/", response_model=List[SourceResponse])
def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_database)):
    """Получение списка источников"""
    sources = source_crud.get_multi(db, skip=skip, limit=limit)
    return [SourceResponse.model_validate(source) for source in sources]


@router.get("/sources/{source_id}", response_model=SourceWithWeights)
def read_source(source_id: int, db: Session = Depends(get_database)):
    """Получение источника с весами"""
    source = source_crud.get(db, id=source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Получаем веса для источника
    weights = source_crud.get_weights(db, source_id=source_id)

    # Создаем список весов как Pydantic модели
    weight_responses = [
        SourceWeightResponse(
            id=weight.id,
            source_id=weight.source_id,
            operator_id=weight.operator_id,
            weight=weight.weight,
            created_at=weight.created_at,
            updated_at=weight.updated_at,
        )
        for weight in weights
    ]

    # Создаем ответ
    return SourceWithWeights(
        id=source.id,
        name=source.name,
        bot_token=source.bot_token,
        description=source.description,
        created_at=source.created_at,
        updated_at=source.updated_at,
        weights=weight_responses,
    )


@router.post("/sources/{source_id}/weights", response_model=SourceWeightResponse)
def add_source_weight(
    source_id: int, weight_in: SourceWeightCreate, db: Session = Depends(get_database)
):
    """Добавление веса оператора к источнику"""
    source = source_crud.get(db, id=source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    weight = source_crud.add_weight(db, source_id=source_id, weight_in=weight_in)

    return SourceWeightResponse(
        id=weight.id,
        source_id=weight.source_id,
        operator_id=weight.operator_id,
        weight=weight.weight,
        created_at=weight.created_at,
        updated_at=weight.updated_at,
    )


@router.delete("/sources/{source_id}/weights/{operator_id}")
def remove_source_weight(
    source_id: int, operator_id: int, db: Session = Depends(get_database)
):
    """Удаление веса источника"""
    source = source_crud.get(db, id=source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    weight = source_crud.remove_weight(db, source_id=source_id, operator_id=operator_id)
    if not weight:
        raise HTTPException(status_code=404, detail="Weight not found")

    return {"message": "Weight removed successfully"}
