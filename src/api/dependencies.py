from typing import Generator

from sqlalchemy.orm import Session

from database import get_db


def get_database() -> Generator[Session, None, None]:
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()
