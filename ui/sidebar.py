"""
Sidebar: brand header, month/year period selector, active-period card.

CSS classes used here (sb-brand, sb-period-card, sb-chip-label, ...)
come from the reference single-station app's styles.py, adopted
verbatim — see ui/styles.py's docstring. Do not rename classes here
without updating styles.py to match.

Deliberately plain widget-wise: just `with st.sidebar:` and Streamlit's
own selectboxes. An earlier version fought Streamlit's native
collapse/expand behavior with custom JS that force-set inline styles
on the sidebar element — that's what caused the sidebar to get stuck
and stop opening. Streamlit's built-in collapse arrow is the only
toggle now.
"""
import streamlit as st

from config import MONTHS
from core.dates import get_days_in_month
from core.sanitize import esc


def render_sidebar(station):
    """Renders the sidebar and returns (sel_month, sel_year, days_in_month, month_idx)."""
    stn_name = esc(station["name"]) if station["name"] else "STATION NAME"

    with st.sidebar:
        st.markdown(f"""
        <div class="sb-brand">
            <div class="sb-brand-icon">🚆</div>
            <p class="sb-brand-name">Imprest Automator</p>
            <p class="sb-brand-sub">Indian Railways · {stn_name}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="sb-section-label">Billing Period</span>', unsafe_allow_html=True)

        if "selected_month" not in st.session_state:
            st.session_state.selected_month = MONTHS[0]
        if "selected_year" not in st.session_state:
            st.session_state.selected_year = "2026"

        year_options = [str(y) for y in range(2024, 2031)]

        sel_month = st.selectbox(
            "Month", MONTHS,
            index=MONTHS.index(st.session_state.selected_month),
            label_visibility="collapsed", key="sb_month")
        sel_year = st.selectbox(
            "Year", year_options,
            index=year_options.index(st.session_state.selected_year)
                  if st.session_state.selected_year in year_options else 2,
            label_visibility="collapsed", key="sb_year")

        st.session_state.selected_month = sel_month
        st.session_state.selected_year  = sel_year

        days_in_month, month_idx = get_days_in_month(sel_month, sel_year)

        st.markdown(f"""
        <div class="sb-period-card">
            <p class="sb-period-label-txt">Active Period</p>
            <p class="sb-period-full">{sel_month} {sel_year}</p>
            <div class="sb-period-row">
                <div class="sb-period-chip">
                    <p class="sb-chip-label">From</p>
                    <p class="sb-chip-val">01/{month_idx:02d}/{sel_year}</p>
                </div>
                <div class="sb-period-chip">
                    <p class="sb-chip-label">To</p>
                    <p class="sb-chip-val">{days_in_month}/{month_idx:02d}/{sel_year}</p>
                </div>
            </div>
            <div class="sb-period-row">
                <div class="sb-period-chip">
                    <p class="sb-chip-label">Days</p>
                    <p class="sb-chip-val">{days_in_month}</p>
                </div>
                <div class="sb-period-chip">
                    <p class="sb-chip-label">Sanctioned</p>
                    <p class="sb-chip-val">₹{station['sanctioned_amount']:,}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sb-footer">
            <p>Daily Wage · ₹{station['daily_wage']}<br>Sanctioned Amount · ₹{station['sanctioned_amount']:,}</p>
        </div>
        """, unsafe_allow_html=True)

    return sel_month, sel_year, days_in_month, month_idx
