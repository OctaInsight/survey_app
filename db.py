"""
Supabase connection helper.

Reads credentials from Streamlit secrets (.streamlit/secrets.toml):

    [supabase]
    url = "https://xxxxxxxx.supabase.co"
    key = "your-anon-public-key"
"""

from __future__ import annotations

import streamlit as st
from supabase import create_client, Client

TABLE_NAME = "harmonia_needs_survey"


@st.cache_resource(show_spinner=False)
def get_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


def insert_response(data: dict) -> None:
    """Insert one survey response. Raises on failure so the caller can show an error."""
    client = get_client()
    client.table(TABLE_NAME).insert(data).execute()


def fetch_responses() -> list[dict]:
    """Return all survey responses as a list of dicts (newest first)."""
    client = get_client()
    result = client.table(TABLE_NAME).select("*").order("created_at", desc=True).execute()
    return result.data or []
