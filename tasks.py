"""
Модуль с задачами Celery.
"""

import os
import asyncio
from celery import Celery
import asyncssh
from sqlmodel import true
from database import SessionLocal
from models import SFTPServer, File, FileStatus

celery = Celery(
    "file_importer", broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
)

celery.conf.beat_schedule = {
    "scan-every-minute": {
        "task": "tasks.scan_active_servers",
        "schedule": 60.0,  # запускать каждые 60 секунд
    },
}


def decrypt_password(_: object) -> str:
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
def discover_files_task(_self, server_id: int):
    """
    Задача Celery, которая обрабатывает файлы для конкретного сервера по его ID.
    (Сейчас просто выводит сообщение с идентификатором сервера.)
    """
    with SessionLocal() as session:
        server = (
            session.query(SFTPServer)
            .filter(SFTPServer.id == server_id, SFTPServer.is_active == true())
            .one_or_none()
        )

        if not server:
            print(f"Server {server_id} not found or inactive")
            return

    password = decrypt_password(server.password_encrypted)

    async def list_files():
        async with asyncssh.connect(
            server.host,
            port=server.port,
            username=server.username,
            password=password,
            known_hosts=None,
        ) as conn:
            async with conn.start_sftp_client() as sftp:
                files = await sftp.listdir(".")
                result = []
                for f in files:
                    try:
                        file_info = await sftp.stat(f)
                        size = file_info.size
                    except asyncssh.sftp.SFTPError:
                        size = None
                    result.append((f, size))
                return result

    try:
        files = asyncio.run(list_files())

        with SessionLocal() as session:
            for filename, size_bytes in files:
                existing = (
                    session.query(File)
                    .filter(
                        File.filename == filename,
                        File.size_bytes == size_bytes,
                    )
                    .first()
                )

                if existing:
                    continue

                new_file = File(
                    server_uuid=server.server_uuid,
                    remote_path=".",
                    filename=filename,
                    size_bytes=size_bytes,
                    status=FileStatus.DISCOVERED,
                )
                session.add(new_file)
                session.commit()
                download_file_task.delay(new_file.id)

    except (asyncssh.Error, asyncio.TimeoutError) as e:
        print(f"Error in discover_files_task for server {server_id}: {e}")


@celery.task(bind=True)
def download_file_task(_self, file_id: int):
    """
    Задача Celery, скачивание файла по ID.
    (Сейчас просто выводит сообщение с идентификатором файла)
    """
    print(f"download_file_task called for file_id={file_id}")
