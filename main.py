"""
FastAPI приложение для скачивания файлов для Smartcom.city.
"""

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="File Downloader")

# можно запускать main.py напрямую, необязательно через uvicorn (python main.py)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, log_level="info", reload=True)
