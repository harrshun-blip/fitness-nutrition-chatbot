"""Core chatbot logic: Google Gemini + lightweight tool routing.

The bot is a fitness, diet and nutrition assistant. Before answering it can:
- pull real nutrition numbers (nutrition.py) when the user asks about a food
- scrape a web page (scraper.py) when the user pastes a URL

The fetched data is injected into the prompt as grounding context so the model
answers with real facts instead of guessing.
"""

import os
import re
import google.generativeai as genai

from nutrition import get_nutrition_facts
from scraper import scrape_text

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
"""

_URL_RE = re.compile(r"https?://[^\s]+")


def _configure():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file or Streamlit secrets."
        )
    genai.configure(api_key=api_key)


def _gather_context(user_message: str) -> str:
    """Optionally enrich the prompt with scraped page text and/or nutrition data."""
    context_parts = []

    # 1. If the user pasted a URL, scrape it.
    url_match = _URL_RE.search(user_message)
    if url_match:
        page_text = scrape_text(url_match.group(0))
        context_parts.append(f"[Scraped page content]\n{page_text}")

    # 2. If the message looks like it's asking about a food's nutrition, look it up.
    nutrition_triggers = ("calorie", "calories", "protein", "carb", "nutrition",
                          "macro", "fat in", "how much", "sugar")
    lowered = user_message.lower()
    if any(t in lowered for t in nutrition_triggers):
        # Use the last few words as a rough food query; the model handles the rest.
        food_query = re.sub(r"[^a-zA-Z ]", "", lowered)
        food_query = food_query.replace("how much", "").replace("calories", "")
        food_query = food_query.replace("nutrition", "").replace("protein", "").strip()
        if food_query:
            facts = get_nutrition_facts(food_query[:60])
            context_parts.append(f"[Nutrition lookup]\n{facts}")

    return "\n\n".join(context_parts)


def ask_pulse(user_message: str, history: list[dict] | None = None) -> str:
    """Send the user message (plus any grounding context) to Gemini and return the reply.

    `history` is a list of {"role": "user"|"model", "content": str} dicts.
    """
    _configure()
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    # Rebuild prior turns for the model.
    convo = []
    for turn in (history or []):
        convo.append({"role": turn["role"], "parts": [turn["content"]]})

    context = _gather_context(user_message)
    prompt = user_message
    if context:
        prompt = f"{user_message}\n\n--- Grounding data (use this) ---\n{context}"

    convo.append({"role": "user", "parts": [prompt]})

    try:
        response = model.generate_content(convo)
        return response.text
    except Exception as exc:
        return f"Sorry, I hit an error talking to Gemini: {exc}"


if __name__ == "__main__":
    # Quick manual test: python chatbot.py
    print(ask_pulse("How many calories are in a banana, and is it good pre-workout?"))
