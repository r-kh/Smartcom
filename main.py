"""
FastAPI приложение для скачивания файлов (для Smartcom.city)
"""

import uvicorn
from fastapi import FastAPI
from tasks import scan_active_servers

app = FastAPI(title="File Downloader")


@app.post("/files/scan")
async def scan_files():
    """
    Запускает асинхронную задачу для сканирования всех активных SFTP серверов
    и обнаружения новых файлов для загрузки.
    """
    scan_active_servers.delay()
    return {"status": "scan_started"}


# можно запускать main.py напрямую, необязательно через uvicorn (python main.py)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, log_level="info", reload=True)
