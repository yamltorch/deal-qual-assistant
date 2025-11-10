"""Минимальный Streamlit UI для просмотра состояния сделки."""

from __future__ import annotations

import os
from typing import Any

import requests
from requests import RequestException
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEFAULT_DEAL_ID = os.getenv("DEFAULT_DEAL_ID", "demo-deal")


def fetch_state(deal_id: str) -> dict[str, Any]:
    """Выполнить запрос состояния сделки к бэкенду."""

    response = requests.get(
        f"{BACKEND_URL}/state/{deal_id}",
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


st.set_page_config(
    page_title="Deal Qual Assistant",
    page_icon="🧭",
    layout="wide",
)
st.title("Deal Qualification Assistant")

deal_id = st.text_input("Deal ID", value=DEFAULT_DEAL_ID)
if st.button("Refresh") and deal_id:
    try:
        st.session_state["last_state"] = fetch_state(deal_id)
    except RequestException as error:
        st.error(f"Не удалось получить состояние сделки: {error}")

state = st.session_state.get("last_state")
if state:
    st.json(state)
else:
    st.info("Запросите состояние сделки, чтобы увидеть данные.")


