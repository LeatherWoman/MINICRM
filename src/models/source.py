from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class Source(BaseModel):
    __tablename__ = "sources"

    name = Column(String, nullable=False)
    bot_token = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Отношения
    source_weights = relationship(
        "SourceWeight", back_populates="source", cascade="all, delete-orphan"
    )
    contacts = relationship("Contact", back_populates="source")

    class Config:
        from_attributes = True


class SourceWeight(BaseModel):
    __tablename__ = "source_weights"

    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False)
    weight = Column(Integer, default=1)  # Вес для распределения

    # Отношения
    source = relationship("Source", back_populates="source_weights")
    operator = relationship("Operator", back_populates="source_weights")
