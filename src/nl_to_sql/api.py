import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from .config import get_settings, Settings
from .chain import build_chain


load_dotenv()
STATIC_DIR = Path(__file__).resolve().parents[2] / "static"

app = FastAPI(title="NL-to-SQL Chat Demo")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))


def _settings_to_dict(settings: Settings) -> dict:
    if hasattr(settings, "model_dump"):
        return settings.model_dump()
    return settings.dict()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chain = None
    settings = None
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            mtype = msg.get("type")

            if mtype == "connect":
                db_conf = msg.get("db", {}) or {}
                base = get_settings()
                merged = {**_settings_to_dict(base), **db_conf}
                settings = Settings(**merged)
                try:
                    chain = await run_in_threadpool(build_chain, settings)
                except Exception as exc:
                    logging.exception("Database connection failed")
                    await websocket.send_text(
                        json.dumps({"type": "error", "message": str(exc)})
                    )
                    continue
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "connected",
                            "message": f"Connected to {settings.DB_NAME or settings.DB_URI}",
                        }
                    )
                )

            elif mtype == "message":
                if not chain:
                    await websocket.send_text(json.dumps({"type": "error", "message": "not connected"}))
                    continue
                question = msg.get("question")
                await websocket.send_text(json.dumps({"type": "status", "message": "thinking"}))
                try:
                    result = await run_in_threadpool(chain.invoke, {"question": question})
                except Exception as exc:
                    logging.exception("Chain invocation failed")
                    await websocket.send_text(json.dumps({"type": "error", "message": str(exc)}))
                    continue
                if isinstance(result, dict):
                    payload = {
                        "type": "response",
                        "answer": str(result.get("answer", "")),
                        "query": str(result.get("query", "")),
                        "result": str(result.get("result", "")),
                    }
                else:
                    payload = {"type": "response", "answer": str(result)}
                await websocket.send_text(json.dumps(payload))

            else:
                await websocket.send_text(json.dumps({"type": "error", "message": "unknown message type"}))

    except WebSocketDisconnect:
        logging.info("Client disconnected")
    except Exception:
        logging.exception("Unexpected error in websocket")
