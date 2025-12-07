from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class Lead(BaseModel):
    __tablename__ = "leads"

    external_id = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, index=True)
    email = Column(String, index=True)
    full_name = Column(String)
    notes = Column(Text)

    # Отношения
    contacts = relationship(
        "Contact", back_populates="lead", cascade="all, delete-orphan"
    )
