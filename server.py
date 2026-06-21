"""Pulse backend — FastAPI server for the installable PWA.

Serves the static front-end (the installable web app) and exposes a single
JSON endpoint, /api/chat, which runs the existing Pulse brain (Gemini + the
nutrition and scraper helpers). The Gemini API key stays on the server and is
NEVER sent to the browser.

Run locally:   uvicorn server:app --host 0.0.0.0 --port 8000
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chatbot import ask_pulse

load_dotenv()

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Pulse API")


class Turn(BaseModel):
    role: str            # "user" or "model"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Turn] = []


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Run one chat turn through the Pulse brain and return the reply."""
    if not req.message.strip():
        return JSONResponse({"reply": "Please type a message."}, status_code=400)
    history = [{"role": t.role, "content": t.content} for t in req.history]
    reply = ask_pulse(req.message, history=history)
    return {"reply": reply}


@app.get("/api/health")
def health():
    return {"status": "ok", "model": "gemini-1.5-flash", "name": "Pulse"}


# Serve the PWA. The service worker and manifest must be reachable at the root
# scope, which StaticFiles(html=True) handles by serving index.html for "/".
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
