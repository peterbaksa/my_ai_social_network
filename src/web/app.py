import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.web.websocket import ConnectionManager

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="AI Social Network")
manager = ConnectionManager()

# Store engine reference — set by main.py before startup
_engine = None


def set_engine(engine) -> None:
    global _engine
    _engine = engine


@app.get("/")
async def index():
    index_file = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "start" and _engine is not None:
                _engine.set_event_callback(manager.broadcast)
                asyncio.create_task(_engine.run(resume=False))
            elif data == "resume" and _engine is not None:
                _engine.set_event_callback(manager.broadcast)
                asyncio.create_task(_engine.run(resume=True))
            elif data == "stop" and _engine is not None:
                _engine.stop()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
