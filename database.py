"""
Модуль для настройки подключения к базе данных с использованием SQLAlchemy и asyncpg.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres@localhost/postgres"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,           # можно уменьшить/увеличить в зависимости от ресурсов
    max_overflow=0,        # чтобы не создавать новых сверх пула
    pool_pre_ping=True     # проверяет соединение перед использованием
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
