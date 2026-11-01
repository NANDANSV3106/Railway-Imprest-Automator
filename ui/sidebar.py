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
import datetime

from core.sanitize import esc

SUBMISSION_CUTOFF_DAY = 15


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

        today = datetime.date.today()
        # Last day to submit the previous month's imprest is the 15th of
        # the next month. On/before the 15th -> previous month; after -> current.
        if today.day <= SUBMISSION_CUTOFF_DAY:
            default_month_idx = today.month - 2
            default_year = today.year
            if default_month_idx < 0:
                default_month_idx = 11
                default_year -= 1
        else:
            default_month_idx = today.month - 1
            default_year = today.year

        year_options = [str(y) for y in range(today.year - 1, today.year + 3)]

        # Defaults apply only on first load; afterwards the user's pick sticks.
        if "sb_month" not in st.session_state:
            st.session_state["sb_month"] = MONTHS[default_month_idx]
        if "sb_year" not in st.session_state or st.session_state["sb_year"] not in year_options:
            st.session_state["sb_year"] = str(default_year)

        sel_month = st.selectbox("Month", MONTHS,
                                 label_visibility="collapsed", key="sb_month")
        sel_year = st.selectbox("Year", year_options,
                                label_visibility="collapsed", key="sb_year")

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
