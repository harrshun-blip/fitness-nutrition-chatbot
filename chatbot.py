"""Core chatbot logic: Groq LLM + lightweight tool routing.

Pulse is a fitness, diet and nutrition assistant. Before answering it can:
- pull real nutrition numbers (nutrition.py) when the user asks about a food
- scrape a web page (scraper.py) when the user pastes a URL

The fetched data is injected into the prompt as grounding context so the model
answers with real facts instead of guessing.

The model runs on Groq (fast, free tier). The default is Llama 3.3 70B; switch
it with the GROQ_MODEL environment variable, e.g.:
    GROQ_MODEL=llama-3.1-8b-instant      (faster, lighter)
    GROQ_MODEL=openai/gpt-oss-120b
    GROQ_MODEL=qwen/qwen3-32b
"""

import os
import re

from groq import Groq

from nutrition import get_nutrition_facts
from scraper import scrape_text

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are Pulse, a friendly and knowledgeable AI assistant for
fitness, diet and nutrition. You give practical, evidence-based guidance on
workouts, meal planning, macros and healthy habits.

Rules:
- Be encouraging and clear; avoid medical jargon.
- When nutrition data or scraped page content is provided below, use it and
  cite the numbers rather than guessing.
- You are not a doctor. For medical conditions, injuries, pregnancy, eating
  disorders or medication, advise the user to consult a qualified professional.
- Never promote extreme dieting, unsafe weight loss, or disordered eating.
- Keep answers focused and reasonably concise unless asked for detail."""

_URL_RE = re.compile(r"https?://[^\s]+")


def _client(api_key: str | None = None) -> Groq:
    """Build a Groq client from a per-request key, else the env key."""
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError(
            "No Groq API key provided. Enter one in the app, or set GROQ_API_KEY."
        )
    return Groq(api_key=key)


def validate_key(api_key: str) -> bool:
    """Cheap check that a key works (lists models). Returns True/False."""
    try:
        _client(api_key).models.list()
        return True
    except Exception:
        return False


def _gather_context(user_message: str) -> str:
    """Optionally enrich the prompt with scraped page text and/or nutrition data."""
    context_parts = []

    url_match = _URL_RE.search(user_message)
    if url_match:
        page_text = scrape_text(url_match.group(0))
        context_parts.append(f"[Scraped page content]\n{page_text}")

    nutrition_triggers = ("calorie", "calories", "protein", "carb", "nutrition",
                          "macro", "fat in", "how much", "sugar")
    lowered = user_message.lower()
    if any(t in lowered for t in nutrition_triggers):
        food_query = re.sub(r"[^a-zA-Z ]", "", lowered)
        food_query = food_query.replace("how much", "").replace("calories", "")
        food_query = food_query.replace("nutrition", "").replace("protein", "").strip()
        if food_query:
            facts = get_nutrition_facts(food_query[:60])
            context_parts.append(f"[Nutrition lookup]\n{facts}")

    return "\n\n".join(context_parts)


def ask_pulse(user_message: str, history: list[dict] | None = None,
              api_key: str | None = None) -> str:
    """Send the user message (plus any grounding context) to Groq and return the reply.

    `history` is a list of {"role": "user"|"model", "content": str} dicts.
    `api_key` is the caller's Groq key (from the browser cookie); falls back to env.
    """
    try:
        client = _client(api_key)
    except RuntimeError as exc:
        return str(exc)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in (history or []):
        role = "user" if turn.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": turn["content"]})

    context = _gather_context(user_message)
    prompt = user_message
    if context:
        prompt = f"{user_message}\n\n--- Grounding data (use this) ---\n{context}"
    messages.append({"role": "user", "content": prompt})

    try:
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=0.6,
            max_tokens=1024,
        )
        return resp.choices[0].message.content
    except Exception as exc:
        return f"Sorry, I hit an error talking to Groq: {exc}"


if __name__ == "__main__":
    print(ask_pulse("How many calories are in a banana, and is it good pre-workout?"))
