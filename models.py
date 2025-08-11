"""
Модуль содержит модели для работы с SFTP-серверами и файлами.
"""

from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from sqlmodel import SQLModel, Field


class SFTPServer(SQLModel, table=True):
    """
    Модель для таблицы sftp_servers.
    """

    __tablename__ = "sftp_servers"

    id: Optional[int] = Field(default=None, primary_key=True)
    server_uuid: UUID
    name: str = Field(max_length=100)
    host: str = Field(max_length=255)
    port: int = Field(default=22)
    username: str = Field(max_length=255)
    password_encrypted: bytes
    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime


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
    server_uuid: UUID
    remote_path: str
    filename: str = Field(max_length=255)
    size_bytes: Optional[int]
    file_hash: Optional[str] = Field(default=None, max_length=64)
    hash_algo: str = Field(default="sha256", max_length=10)
    status: FileStatus = Field(default=FileStatus.DISCOVERED)
    error_message: Optional[str] = None
    minio_object_key: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
