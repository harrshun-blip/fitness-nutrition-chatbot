# 💧 Pulse — Fitness & Nutrition AI Chatbot

**Pulse** is an AI chatbot for **fitness, diet and nutrition** with built-in
**web scraping**. It comes in two flavours:

1. 📱 **Installable mobile app (PWA)** — a custom-designed chat UI you can add to
   an Android home screen and use like a native app. *(recommended)*
2. 🧪 **Streamlit version** — a quick, no-frontend way to test the same brain.

Built to run entirely in the cloud — no local computer required. Develop it in
**GitHub Codespaces** (VS Code in your browser) and deploy it for free.

## What it does

- 🤖 **Conversational AI** powered by Groq (Llama 3.3 70B by default, free tier).
- 🥗 **Real nutrition data** from the USDA FoodData Central and Open Food Facts
  APIs — so answers use real numbers, not guesses.
- 🌐 **Web scraping** — paste a recipe or article URL and Pulse reads the page
  (politely, respecting `robots.txt`).
- 💧 **Beautiful chat UI** with an "Ocean Calm" theme, installable on Android.

## Project structure

| Path | Purpose |
|------|---------|
| `server.py` | FastAPI backend: serves the PWA + `/api/chat` (keeps the API key server-side) |
| `static/` | The installable web app (HTML, CSS, JS, manifest, service worker, icons) |
| `chatbot.py` | Gemini logic + decides when to look up nutrition / scrape |
| `nutrition.py` | USDA + Open Food Facts API helpers |
| `scraper.py` | Polite web-scraping helper (requests + BeautifulSoup) |
| `app.py` | Optional Streamlit version of the same chatbot |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for your API keys |

## Quick start (in GitHub Codespaces — no computer needed)

1. On this repo's GitHub page, click the green **`< > Code`** button →
   **Codespaces** → **Create codespace on main**. Wait for it to finish setting
   up (it auto-installs the dependencies).
2. Start the mobile app server:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```
3. Codespaces will pop up a notification to open the forwarded port — open it.
   The app opens and **asks for your Groq API key**. Get a free one at
   <https://console.groq.com/keys>, paste it in, and you're chatting. 🎉

> **Bring your own key (BYOK):** Pulse never stores the key in the code or in git.
> You paste your key into the app; the server saves it in a **secure, HttpOnly
> cookie on your device**, so it's remembered on reload but unreadable by page
> scripts. Use the 🔑 button in the header to change it. (A `GROQ_API_KEY` in
> `.env` also works as a fallback for personal/local use.)
>
> **Model:** default is `llama-3.3-70b-versatile`. Change it with the `GROQ_MODEL`
> env var (e.g. `llama-3.1-8b-instant`, `openai/gpt-oss-120b`, `qwen/qwen3-32b`).

> Prefer the simple Streamlit version instead? Run `streamlit run app.py`
> (that one uses `.env` / Streamlit secrets for the key).

## 📱 Install Pulse on an Android phone

The app is a **PWA (Progressive Web App)**, so it installs straight from the
browser — no Play Store needed. You need a public HTTPS URL (see *Deploy* below;
Codespaces forwarded ports are HTTPS too, handy for testing).

1. Open the app's URL in **Chrome on Android**.
2. Tap the **⋮ menu** → **Add to Home screen** (or accept the "Install app"
   prompt that appears).
3. Pulse now has its own icon and opens full-screen, like a native app.

## Try these prompts

- "How much protein is in 100g chicken breast?"
- "Build me a high-protein vegetarian lunch under 600 kcal."
- "https://example.com/some-recipe — is this a good post-workout meal?"
- "A beginner full-body workout, 3x a week."

## Important notes

- **Never commit your API keys.** The real `.env` file is gitignored.
- Pulse is an educational tool, **not** a substitute for advice from a doctor,
  dietitian, or qualified trainer.
- Scrape responsibly: respect each site's Terms of Service and `robots.txt`, and
  prefer official APIs when they exist.

## Deploy it for free (later)

The PWA needs an HTTPS host. Good free options for the FastAPI backend + static
front-end:

- **Render** (<https://render.com>) — free web service; start command
  `uvicorn server:app --host 0.0.0.0 --port $PORT`. Add `GROQ_API_KEY` as an
  environment variable.
- **Hugging Face Spaces** (Docker) or **Railway** also work well.

The Streamlit version can instead be deployed on **Streamlit Community Cloud**
(<https://share.streamlit.io>) with `app.py` as the entry point.
