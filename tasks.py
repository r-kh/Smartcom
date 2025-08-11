"""
Модуль с задачами Celery.
"""

import os

from celery import Celery

from sqlalchemy import true
from database import SessionLocal
from models import SFTPServer

celery = Celery(
    "file_importer", broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
)

celery.conf.beat_schedule = {
    "scan-every-minute": {
        "task": "tasks.scan_active_servers",
        "schedule": 60.0,  # запускать каждые 60 секунд
    },
}


def decrypt_password(_: str) -> str:
    """
    По задумке пароль должен извлекаться из базы данных и расшифровываться.
    Но по задаче нужна реализация только функционала скачивания файлов.
    Поэтому эта функция не реализована и пароль берется напрямую из переменной окружения.
    """
    password = os.getenv("SFTP_PASSWORD")
    if not password:
        raise RuntimeError("Environment variable SFTP_PASSWORD is not set")
    return password


@celery.task
def scan_active_servers():
    """
    Задача Celery, которая сканирует активные SFTP-серверы.
    Получает список активных серверов из базы и запускает задачу
    discover_files_task для каждого из них.
    """
    with SessionLocal() as session:
        servers = session.query(SFTPServer).filter(SFTPServer.is_active == true()).all()
        for server in servers:
            discover_files_task.delay(server.id)


@celery.task(bind=True)
def discover_files_task(_, server_id: int):
    """
    Задача Celery, которая обрабатывает файлы для конкретного сервера по его ID.
    (Сейчас просто выводит сообщение с идентификатором сервера.)
    """
    print(f"discover_files_task called for server_id={server_id}")
