# app.py
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Google Gen AI SDK
from google import genai
from google.genai import types

# Load environment variables from .env (development only)
load_dotenv()

# Read API key from environment
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Gemini Chatbot", page_icon="💬")
st.title("💬 Simple Gemini Chatbot (Streamlit)")

if not API_KEY:
    st.error("No API key found. Put GEMINI_API_KEY=... in a .env file.")
    st.stop()

# Create GenAI client (explicitly pass api_key)
client = genai.Client(api_key=API_KEY)

# Load prompt template
prompt_path = Path("prompt.txt")
default_system_instruction = "You are a helpful, concise assistant."
system_instruction = prompt_path.read_text(encoding="utf-8").strip() if prompt_path.exists() else default_system_instruction

# Init session state
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": "..."}
if "chat" not in st.session_state:
    # Create a chat session with system instructions
    st.session_state.chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.6,
            max_output_tokens=800,
        ),
    )

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    if st.button("Reset conversation"):
        st.session_state.messages = []
        st.session_state.chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.6,
                max_output_tokens=800,
            ),
        )
        st.success("Conversation reset")

    st.write("System instruction:")
    st.code(system_instruction, language="markdown")

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input widget
user_input = st.chat_input("Ask anything...")
if user_input:
    # show user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # send to Gemini
    try:
        response = st.session_state.chat.send_message(user_input)
        reply = response.text
    except Exception as e:
        reply = f"⚠️ Model call failed: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply) 