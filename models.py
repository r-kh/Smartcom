"""
Модуль содержит модели для работы с SFTP-серверами и файлами.
"""

from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class SFTPServer(SQLModel, table=True):
    """
    Модель для таблицы sftp_servers.
    """

    __tablename__ = "sftp_servers"

    id: Optional[int] = Field(default=None, primary_key=True)
    host: str
    port: int = 22
    username: str
    password_encrypted: str
    is_active: bool = True


class FileStatus(str, Enum):
    """Статусы файла в процессе обработки."""

    DISCOVERED = "discovered"
    DOWNLOADED = "downloaded"
    MINIO_UPLOADED = "minio_uploaded"
    AMQP_NOTIFY_SENT = "amqp_notify_sent"
    COMPLETED = "completed"
    ERROR = "error"


class File(SQLModel, table=True):
    """Модель для таблицы files."""

    __tablename__ = "files"

    id: Optional[int] = Field(default=None, primary_key=True)
    server_uuid: str
    remote_path: str
    filename: str
    size_bytes: Optional[int]
    file_hash: Optional[str] = None
    hash_algo: str = Field(default="sha256")
    status: FileStatus = Field(default=FileStatus.DISCOVERED)
    error_message: Optional[str] = None
    minio_object_key: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
