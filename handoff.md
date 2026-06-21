# 📘 Pulse — Project Handoff (Master Context File)

> **Purpose of this file.** This is the single source of truth for the **Pulse**
> project. If you are a new AI assistant (e.g. a fresh Claude) or a new
> developer picking this up, **read this whole file first** — it explains what
> Pulse is, how it's built, how to run/deploy it, what's done, and what's next.
> Hand this file over and you can continue seamlessly.

---

## 1. What Pulse is

**Pulse** is an AI chatbot for **fitness, diet and nutrition**, with built-in
**web scraping**. It runs as:

1. **An installable mobile app (PWA)** — custom UI, works on Android home screen. *(primary)*
2. **A Streamlit app** (`app.py`) — simple alternative interface.

It was built entirely in the cloud (GitHub + Codespaces) — **no local computer
required** — for a student, **Harrshun** (GitHub user `harrshun-blip`).

- **Repo:** https://github.com/harrshun-blip/fitness-nutrition-chatbot (public)
- **Name/brand:** "Pulse", tagline "Fitness & Nutrition AI"
- **Theme:** "Ocean Calm" (teal/cyan, clean spa feel)

## 2. How it works (architecture)

```
Phone/Browser (PWA)  ──►  FastAPI backend (server.py)  ──►  Groq LLM API
   static/ UI              /api/chat, /api/key, /api/status     (Llama 3.3 70B)
                                  │
                                  ├──►  nutrition.py  (USDA + Open Food Facts APIs)
                                  └──►  scraper.py    (requests + BeautifulSoup)
```

- The **frontend** (`static/`) is a Progressive Web App: HTML/CSS/JS + manifest +
  service worker + icons. Installable, offline app-shell.
- The **backend** (`server.py`, FastAPI) serves the PWA and exposes a JSON API.
- The **brain** (`chatbot.py`) calls **Groq** and decides when to enrich the
  prompt with real nutrition data or scraped page text ("grounding").
- **LLM:** Groq, default model `llama-3.3-70b-versatile`. Override with the
  `GROQ_MODEL` env var (e.g. `llama-3.1-8b-instant`, `openai/gpt-oss-120b`,
  `qwen/qwen3-32b`).

### Bring-Your-Own-Key (BYOK) — important design decision
Each user supplies their **own Groq API key**. We do NOT store any key in the
code or in git. Flow:
1. App loads → `GET /api/status` checks for a valid key.
2. If none/invalid → the UI shows the "Connect your Groq key" modal.
3. User pastes key → `POST /api/key` validates it and stores it in an
   **HttpOnly + Secure + SameSite cookie on the device** (so page scripts can't
   read it; only the server does, automatically, each request).
4. `POST /api/chat` reads the key from the cookie and calls Groq.
5. The 🔑 header button lets the user change/clear the key (`DELETE /api/key`).
- A `GROQ_API_KEY` env var (in `.env`) is an optional server-side fallback.

## 3. File-by-file

| Path | What it does |
|------|--------------|
| `server.py` | FastAPI app. Serves `static/` and the API: `/api/status`, `/api/key` (POST/DELETE), `/api/chat`. Manages the HttpOnly key cookie. |
| `chatbot.py` | `ask_pulse(message, history, api_key)` → Groq chat completion. `validate_key()`. `_gather_context()` adds nutrition/scrape grounding. System prompt defines Pulse's persona + safety rules. |
| `nutrition.py` | `get_nutrition_facts(query)` → USDA FoodData Central, falls back to Open Food Facts. Real per-100g numbers. |
| `scraper.py` | `scrape_text(url)` → polite scraper (respects robots.txt) returning clean page text. |
| `app.py` | Optional Streamlit version of the same chatbot. |
| `static/index.html` | PWA shell: header, chat area, composer, key modal. |
| `static/styles.css` | Ocean Calm theme, chat bubbles, modal, dark-mode support. |
| `static/app.js` | Chat logic, markdown-lite rendering, typing indicator, key modal handling, service-worker registration, history in localStorage. |
| `static/manifest.webmanifest` | PWA manifest (name, icons, theme, standalone). |
| `static/service-worker.js` | Caches the app shell (installable + offline UI). Never caches `/api/`. |
| `static/icons/` | `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` (teal pulse-line icon). |
| `.devcontainer/devcontainer.json` | Codespaces setup; auto-runs `pip install -r requirements.txt`; forwards ports 8000 (PWA) and 8501 (Streamlit). |
| `requirements.txt` | groq, requests, beautifulsoup4, python-dotenv, fastapi, uvicorn, streamlit. |
| `.env.example` | Template for `GROQ_API_KEY`, `GROQ_MODEL`, `USDA_API_KEY`. Copy to `.env` (gitignored). |
| `.gitignore` | Excludes `.env`, caches, etc. |
| `README.md` | User-facing setup + deploy guide. |
| `handoff.md` | This file. |

## 4. How to run it (in GitHub Codespaces, no computer needed)

1. Repo → green **`< > Code`** → **Codespaces** → **Create codespace on main**.
2. In the terminal:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```
3. Open the forwarded **port 8000** (Codespaces shows a popup; or the PORTS tab).
4. The app prompts for a **Groq API key** (free: https://console.groq.com/keys).
   Paste it → chat.
5. Streamlit alternative: `streamlit run app.py`.

**On a phone:** open the forwarded URL in Chrome (sign in to GitHub if the port
is private, or set the port to Public in the PORTS tab) → paste key →
**⋮ menu → Add to Home screen** to install as an app.

## 5. How to deploy permanently (free, always-on) — NOT done yet

The Codespace sleeps after ~30 min idle, and its URL changes. For permanent use,
deploy the FastAPI app to a free host:

- **Render** (https://render.com): New Web Service from the GitHub repo.
  Build: `pip install -r requirements.txt`. Start:
  `uvicorn server:app --host 0.0.0.0 --port $PORT`. (Optionally set `GROQ_API_KEY`.)
- **Hugging Face Spaces** (Docker) or **Railway** also work.
- Streamlit version → **Streamlit Community Cloud** with `app.py` as entry point.

Because of BYOK, you don't even need to set a server key — each user brings their own.

## 6. Security notes (important)

- **Never commit API keys.** `.env` is gitignored. Keys live in the device cookie
  (HttpOnly) or platform secrets — never in source/git.
- The repo is **public**; that's fine because no secrets are in it.
- Scrape responsibly: respect each site's ToS and `robots.txt`; prefer official
  APIs (that's why nutrition uses USDA/Open Food Facts, not scraping).
- Pulse is **educational**, not medical advice. The system prompt enforces this.

## 7. Status — what's DONE ✅

- Repo created on Harrshun's GitHub, all code committed.
- FastAPI backend + custom PWA frontend (Ocean Calm), installable on Android.
- BYOK with HttpOnly cookie; key modal + 🔑 change-key button.
- Switched LLM from Gemini → **Groq** (Gemini's `gemini-1.5-flash` was retired;
  Groq is faster/free and avoided the model-name problem).
- `/api/status` validates the stored key so a stale key re-prompts on refresh.
- Verified end-to-end locally and live in a Codespace on desktop + phone.

## 8. Next steps / TODO 🔜

1. **Permanent free deploy** (Render/HF Spaces) so it's not tied to the Codespace.
2. (Optional) Make the repo private — not required since no secrets are committed.
3. (Optional) Multi-provider support (let users pick Groq / Ollama / others).
4. (Optional) Richer features: save meal/workout plans, daily calorie tracker,
   barcode scan via Open Food Facts, voice input.
5. (Optional) Add automated tests and a simple rate-limit on `/api/chat`.

## 9. Quick facts for a new assistant

- GitHub user: **harrshun-blip**. Repo: **fitness-nutrition-chatbot** (public, `main`).
- LLM: **Groq**, default `llama-3.3-70b-versatile` (BYOK; key from console.groq.com/keys).
- Run: `uvicorn server:app --host 0.0.0.0 --port 8000` (PWA) or `streamlit run app.py`.
- Don't hardcode/commit keys. Keep the BYOK cookie design.
- Editing files is done via GitHub web upload (Harrshun has no local computer) or
  directly in a Codespace.
