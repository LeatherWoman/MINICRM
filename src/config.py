from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Используем простой относительный путь
    # Файл будет создаваться в рабочей директории при запуске
    database_url: str = "sqlite:///database.db"  # Файл в текущей директории

    app_title: str = "CRM Lead Distribution API"
    app_version: str = "1.0.0"


settings = Settings()
