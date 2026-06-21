# 💪 FitBot — Fitness & Nutrition AI Chatbot

An AI chatbot for **fitness, diet and nutrition** with built-in **web scraping**.
Built to run entirely in the cloud — no local computer required. You can develop
it in **GitHub Codespaces** (VS Code in your browser) and deploy it for free.

## What it does

- 🤖 **Conversational AI** powered by Google Gemini (free tier).
- 🥗 **Real nutrition data** from the USDA FoodData Central and Open Food Facts
  APIs — so answers use real numbers, not guesses.
- 🌐 **Web scraping** — paste a recipe or article URL and FitBot reads the page
  (politely, respecting `robots.txt`).
- 💬 **Chat UI** built with Streamlit.

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit chat interface |
| `chatbot.py` | Gemini logic + decides when to look up nutrition / scrape |
| `nutrition.py` | USDA + Open Food Facts API helpers |
| `scraper.py` | Polite web-scraping helper (requests + BeautifulSoup) |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for your API keys |

## Quick start (in GitHub Codespaces — no computer needed)

1. On this repo's GitHub page, click the green **`< > Code`** button →
   **Codespaces** tab → **Create codespace on main**. This opens a full VS Code
   environment in your browser.
2. Wait for it to finish setting up (it auto-installs the dependencies).
3. Get a free Gemini API key at <https://aistudio.google.com/app/apikey>.
4. In the Codespace, copy the example env file and add your key:
   ```bash
   cp .env.example .env
   # then open .env and paste your key after GEMINI_API_KEY=
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```
6. Click the link Codespaces pops up to open FitBot in your browser. 🎉

## Try these prompts

- "How many calories and how much protein are in 100g of chicken breast?"
- "Build me a high-protein vegetarian lunch under 600 calories."
- "https://example.com/some-recipe — is this a good post-workout meal?"
- "What's a good beginner full-body workout 3x a week?"

## Important notes

- **Never commit your API keys.** The real `.env` file is gitignored. Keep it
  that way.
- FitBot is an educational tool, **not** a substitute for advice from a doctor,
  dietitian, or qualified trainer.
- Scrape responsibly: respect each site's Terms of Service and `robots.txt`, and
  prefer official APIs when they exist.

## Deploy it for free (later)

- **Streamlit Community Cloud** — <https://share.streamlit.io>: connect this
  GitHub repo, set `app.py` as the entry point, and add `GEMINI_API_KEY` under
  the app's **Secrets**.
- **Hugging Face Spaces** — also free; create a Streamlit Space from this repo.
