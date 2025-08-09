"""
Модуль содержит модели для работы с SFTP-серверами.
"""

from typing import Optional
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
