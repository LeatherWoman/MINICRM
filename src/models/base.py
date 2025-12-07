from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.declarative import declared_attr

from database import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
