from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class Operator(BaseModel):
    __tablename__ = "operators"

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=10)  # Максимальное количество активных лидов

    # Отношения
    source_weights = relationship(
        "SourceWeight", back_populates="operator", cascade="all, delete-orphan"
    )
    contacts = relationship("Contact", back_populates="operator")
