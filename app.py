"""Streamlit chat UI for the Fitness & Nutrition chatbot (FitBot).

Run locally:   streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

from chatbot import ask_pulse

load_dotenv()  # load GEMINI_API_KEY etc. from a local .env file if present

# On Streamlit Cloud, secrets live in st.secrets -> mirror them into env vars.
for key in ("GEMINI_API_KEY", "USDA_API_KEY"):
    if key in st.secrets and not os.getenv(key):
        os.environ[key] = st.secrets[key]

st.set_page_config(page_title="Pulse — Fitness & Nutrition AI", page_icon="💧")

st.title("💧 Pulse")
st.caption("Your AI assistant for fitness, diet and nutrition. "
           "Ask about workouts, macros, or paste a recipe URL to analyze it.")

with st.sidebar:
    st.header("About")
    st.write(
        "Pulse uses Google Gemini, plus live nutrition data from the USDA "
        "and Open Food Facts. Not a substitute for professional medical advice."
    )
    if not os.getenv("GEMINI_API_KEY"):
        st.error("No GEMINI_API_KEY found. Add it to .env or Streamlit secrets.")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay history.
for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# Handle new input.
if prompt := st.chat_input("Ask Pulse anything about fitness or nutrition..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = ask_pulse(prompt, history=st.session_state.messages[:-1])
        st.markdown(reply)

    st.session_state.messages.append({"role": "model", "content": reply})
