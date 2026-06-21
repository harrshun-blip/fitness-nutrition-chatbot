"""Pulse backend — FastAPI server for the installable PWA (BYOK edition).

Each user brings their own Gemini API key. The key is stored in an **HttpOnly,
Secure, SameSite cookie on the user's device**, which means:
  * the browser sends it automatically with every /api/* request,
  * page JavaScript can NOT read it (protects against XSS stealing the key),
  * it persists on the phone, so the app "remembers" it across reloads.

The key is never written to disk or to git. A "Change key" action clears it.

Run locally:   uvicorn server:app --host 0.0.0.0 --port 8000
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chatbot import ask_pulse, validate_key

load_dotenv()

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
COOKIE_NAME = "pulse_key"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year

app = FastAPI(title="Pulse API")


# ---------- models ----------
class Turn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Turn] = []


class KeyRequest(BaseModel):
    key: str


# ---------- helpers ----------
def _is_https(request: Request) -> bool:
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    return proto == "https"


def _resolve_key(request: Request) -> str | None:
    """The user's key from the cookie, else a server env key (for personal use)."""
    return request.cookies.get(COOKIE_NAME) or os.getenv("GEMINI_API_KEY") or None


# ---------- key management ----------
@app.get("/api/status")
def status(request: Request):
    """Tell the front-end whether a usable, VALID key is already set.

    Validating here means that if the stored key is wrong/expired (e.g. left
    over from a different provider), the app will re-prompt on a simple refresh.
    """
    key = _resolve_key(request)
    return {"has_key": bool(key) and validate_key(key)}


@app.post("/api/key")
def set_key(req: KeyRequest, request: Request, response: Response):
    """Validate the key and store it in an HttpOnly cookie on the device."""
    key = req.key.strip()
    if not key:
        return JSONResponse({"ok": False, "error": "Empty key."}, status_code=400)
    if not validate_key(key):
        return JSONResponse(
            {"ok": False, "error": "That key didn't work. Double-check and try again."},
            status_code=400,
        )
    response.set_cookie(
        key=COOKIE_NAME,
        value=key,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=_is_https(request),
        samesite="lax",
        path="/",
    )
    return {"ok": True}


@app.delete("/api/key")
def clear_key(response: Response):
    """Forget the stored key (logs the device out)."""
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


# ---------- chat ----------
@app.post("/api/chat")
def chat(req: ChatRequest, request: Request):
    if not req.message.strip():
        return JSONResponse({"reply": "Please type a message."}, status_code=400)
    key = _resolve_key(request)
    if not key:
        return JSONResponse({"error": "no_key"}, status_code=401)
    history = [{"role": t.role, "content": t.content} for t in req.history]
    reply = ask_pulse(req.message, history=history, api_key=key)
    return {"reply": reply}


# ---------- static PWA ----------
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
