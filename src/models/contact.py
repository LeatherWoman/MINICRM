from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class Contact(BaseModel):
    __tablename__ = "contacts"

    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)

    message = Column(Text)
    status = Column(String, default="new")  # new, in_progress, closed
    is_active = Column(Boolean, default=True)

    # Отношения
    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")
