"""
app.py — Streamlit web interface for Jazz Solo Transcriber.

Run with:
    streamlit run src/app.py
"""

import streamlit as st

st.set_page_config(page_title="Jazz Solo Transcriber", page_icon="🎷", layout="wide")

st.title("🎷 Jazz Solo Transcriber")
st.markdown("*Upload a jazz recording → get a MIDI transcription*")

st.info("🚧 Web interface coming in Week 5. For now, use the CLI:\n\n"
        "```\npython src/transcribe.py input.wav --instrument other\n```")
