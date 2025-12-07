from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routers import contacts, leads, operators, sources
from database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы при старте
    Base.metadata.create_all(bind=engine)
    yield
    # Очистка при остановке
    pass


app = FastAPI(
    title="CRM Lead Distribution API",
    description="Мини-CRM для распределения лидов между операторами",
    version="1.0.0",
    lifespan=lifespan,
)

# Подключаем роутеры
app.include_router(operators.router, prefix="/api/v1", tags=["operators"])
app.include_router(leads.router, prefix="/api/v1", tags=["leads"])
app.include_router(sources.router, prefix="/api/v1", tags=["sources"])
app.include_router(contacts.router, prefix="/api/v1", tags=["contacts"])


@app.get("/")
async def root():
    return {"message": "CRM Lead Distribution API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
