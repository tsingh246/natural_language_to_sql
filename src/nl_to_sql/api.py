import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.concurrency import run_in_threadpool

from .config import get_settings, Settings
from .chain import build_chain


app = FastAPI(title="NL-to-SQL Chat Demo")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return HTMLResponse(open("static/index.html", "r", encoding="utf-8").read())


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
                merged = {**base.dict(), **db_conf}
                settings = Settings(**merged)
                chain = build_chain(settings)
                await websocket.send_text(json.dumps({"type": "status", "message": "connected"}))

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
                await websocket.send_text(json.dumps({"type": "response", "answer": str(result)}))

            else:
                await websocket.send_text(json.dumps({"type": "error", "message": "unknown message type"}))

    except WebSocketDisconnect:
        logging.info("Client disconnected")
    except Exception:
        logging.exception("Unexpected error in websocket")
