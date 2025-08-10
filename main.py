"""
FastAPI приложение для скачивания файлов для Smartcom.city.
"""

import os
import asyncssh
import uvicorn
from fastapi import FastAPI, HTTPException
from sqlalchemy import true
from sqlmodel import select
from models import SFTPServer
from database import AsyncSessionLocal

app = FastAPI(title="File Downloader")


def decrypt_password(_: str) -> str:
    """
    По проекту пароль должен извлекаться из базы данных и расшифровываться,
    Но по задаче нужна реализация только функционала скачивания файлов.
    Поэтому эта функция не реализована и пароль берется напрямую из переменной окружения.
    """
    password = os.getenv("SFTP_PASSWORD")
    if not password:
        raise RuntimeError("Environment variable SFTP_PASSWORD is not set")
    return password


@app.get("/test-sftp-connection/{server_id}")
async def test_sftp_connection(server_id: int):
    """
    Проверяет подключение к SFTP серверу по ID.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SFTPServer).where(
                SFTPServer.id == server_id, SFTPServer.is_active == true()
            )
        )
        server = result.scalar_one_or_none()
        if not server:
            raise HTTPException(
                status_code=404, detail="SFTP server not found or inactive"
            )

    password = decrypt_password(server.password_encrypted)

    try:
        async with asyncssh.connect(
            server.host,
            port=server.port,
            username=server.username,
            password=password,
            known_hosts=None,
        ) as conn:
            async with conn.start_sftp_client() as sftp:
                files = await sftp.listdir(".")
        return {"status": "success", "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect: {e}") from e


# можно запускать main.py напрямую, необязательно через uvicorn (python main.py)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, log_level="info", reload=True)
