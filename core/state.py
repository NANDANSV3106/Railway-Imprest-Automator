"""
Session-state helpers.

init_app_defaults() — called once at app startup (station config,
initial month/year).

init_default(key, value) — a general per-widget helper: sets
session_state[key] = value only if the key doesn't exist yet, then
returns nothing (Streamlit widgets read the key themselves via their
`key=` argument). Used together with month-scoped keys (see
core/balance_store.month_key) so that switching the sidebar's month/
year doesn't leave stale values from a previously-viewed month sitting
in a differently-named widget — each month gets its own session_state
slot, seeded with a sensible default the first time it's opened.
"""
import datetime
import streamlit as st

from config import MONTHS
from core.balance_store import load_settings


def init_app_defaults():
    """
    Ensure session_state has: station (loaded from disk), selected_month,
    selected_year. Safe to call on every rerun — it's a no-op after the
    first call.
    """
    if "station" not in st.session_state:
        st.session_state.station = load_settings()

    if "selected_month" not in st.session_state:
        now = datetime.datetime.now()
        st.session_state.selected_month = MONTHS[now.month - 1]

    if "selected_year" not in st.session_state:
        now = datetime.datetime.now()
        st.session_state.selected_year = str(now.year)


def init_default(key, value):
    """Seed session_state[key] with `value` only if it isn't already set."""
    if key not in st.session_state:
        st.session_state[key] = value
