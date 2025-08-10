"""
FastAPI приложение для скачивания файлов (для Smartcom.city)
"""

import uvicorn
from fastapi import FastAPI
from tasks import discover_files_task

app = FastAPI(title="File Downloader")


@app.post("/files/scan")
async def scan_files():
    """
    Запускает задачу сканирования файлов на активных SFTP серверах.
    """
    discover_files_task.delay()
    return {"status": "scan_started"}


# можно запускать main.py напрямую, необязательно через uvicorn (python main.py)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, log_level="info", reload=True)
