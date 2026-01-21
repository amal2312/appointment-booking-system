"""LLM model providers and utilities."""

import os
import streamlit as st
from langchain_groq import ChatGroq


def get_chatgroq_model(model_name="llama-3.1-8b-instant"):
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    return ChatGroq(
        model=model_name,
        temperature=0.7,
        api_key=api_key
    )
