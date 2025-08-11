"""
Модуль для настройки подключения к базе данных с использованием SQLAlchemy и asyncpg.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+pg8000://postgres@localhost/postgres"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,  # можно уменьшить/увеличить в зависимости от ресурсов
    max_overflow=0,  # чтобы не создавать новых сверх пула
    pool_pre_ping=True,  # проверяет соединение перед использованием
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
