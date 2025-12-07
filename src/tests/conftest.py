import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app


@pytest.fixture(scope="function")
def db():
    """Фикстура для тестовой базы данных (очищается для каждого теста)"""
    # Создаем уникальную базу данных в памяти
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
    )

    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Создаем сессию
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Удаляем все таблицы
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    """Локальная функция для переопределения зависимости базы данных"""
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
    )

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Фикстура для тестового клиента с чистой базой данных для каждого теста"""
    # Переопределяем зависимость базы данных
    app.dependency_overrides[get_db] = override_get_db

    # Создаем таблицы
    from database import engine

    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c

    # Очищаем переопределения после тестов
    app.dependency_overrides.clear()

    # Удаляем таблицы
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_operator_data():
    """Фикстура с тестовыми данными оператора"""
    return {
        "name": "Тестовый Оператор",
        "email": "test.operator@example.com",
        "max_load": 10,
        "is_active": True,
    }


@pytest.fixture
def sample_source_data():
    """Фикстура с тестовыми данными источника"""
    return {
        "name": "Тестовый Бот",
        "bot_token": "test_bot_token_123",
        "description": "Тестовый источник для тестов",
    }


@pytest.fixture
def sample_lead_data():
    """Фикстура с тестовыми данными лида"""
    return {
        "external_id": "test_user_123",
        "phone": "+79161234567",
        "email": "test.user@example.com",
        "full_name": "Тестовый Пользователь",
        "notes": "Тестовый лид",
    }


@pytest.fixture
def sample_contact_data():
    """Фикстура с тестовыми данными контакта"""
    return {
        "lead_external_id": "test_user_123",
        "source_id": 1,
        "message": "Тестовое сообщение",
        "phone": "+79161234567",
        "full_name": "Тестовый Пользователь",
    }
