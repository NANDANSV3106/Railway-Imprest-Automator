"""
Tab 4 — Station Details: the form that makes this a multi-station app.
This tab wasn't in the requested module breakdown, but it's the only
place a station's identity/workers/financials get edited or switched —
without it the app can only ever run for whatever's in settings.ini.
Added here rather than left out silently.
"""
import copy
import streamlit as st

from config import STATION_DEFAULT, LABOUR_TEMPLATE_PATH
from core.balance_store import save_settings
from core.validation import count_labour_template_worker_slots


def render_tab_station(station):
    S, W = station, station["workers"]

    st.markdown('<p class="sec-title"><span class="sec-title-icon">⚙️</span>Station Details</p>', unsafe_allow_html=True)
    st.info(
        "Edit all station-specific values here. Changes are stored in this session "
        "and take effect immediately on the next Generate. "
        "Fill in all fields before generating documents.",
        icon="ℹ️")

    with st.form("station_form", clear_on_submit=False):

        # ── Station identity ──────────────────────────────
        st.markdown(
            '<p class="sec-title"><span class="sec-title-icon">🏛️</span>Station Identity</p>',
            unsafe_allow_html=True)
        id1, id2 = st.columns(2, gap="large")
        with id1:
            f_name    = st.text_input("Station Name *",
                value=S["name"], placeholder="e.g. STATION NAME",
                autocomplete="off", key="f_station_name")
            f_div     = st.text_input("Division / Station Code *",
                value=S["division"], placeholder="e.g. SMR/XXX",
                autocomplete="off", key="f_division")
            f_officer = st.text_input("Station Manager Name *",
                value=S["officer_name"], placeholder="e.g. FULL NAME",
                autocomplete="off", key="f_officer")
        with id2:
            f_atm    = st.text_input("ATM Card No. *",
                value=S["atm_no"], placeholder="e.g. 8174140400116296",
                autocomplete="off", key="f_atm")
            f_phone  = st.text_input("Auto Phone No.",
                value=S["auto_phone"], placeholder="e.g. 53807",
                autocomplete="off", key="f_phone")
            f_mobile = st.text_input("Mobile No.",
                value=S["mobile"], placeholder="e.g. 9731934623",
                autocomplete="off", key="f_mobile")

        # ── Financial ─────────────────────────────────────
        st.markdown(
            '<p class="sec-title"><span class="sec-title-icon">💰</span>Financial Details</p>',
            unsafe_allow_html=True)
        ff1, ff2 = st.columns(2, gap="large")
        with ff1:
            f_sanc = st.number_input(
                "Sanctioned Amount (Rs.) *",
                value=int(S["sanctioned_amount"]), min_value=1000, step=1000)
        with ff2:
            f_wage = st.number_input(
                "Daily Wage per Worker (Rs.) *",
                value=int(S["daily_wage"]), min_value=100, step=10)

        # ── Labour ────────────────────────────────────────
        n_workers = st.selectbox(
            "Number of Labourers *", [2, 3, 4],
            index=[2, 3, 4].index(len(W)) if len(W) in [2, 3, 4] else 0)
        tmpl_slots = count_labour_template_worker_slots(LABOUR_TEMPLATE_PATH)
        if tmpl_slots and n_workers > tmpl_slots:
            st.warning(
                f"⚠️ The current Labour Annexure template only supports "
                f"{tmpl_slots} worker(s). Documents won't generate for "
                f"{n_workers} until the template is updated or the count is reduced.")

        st.markdown(
            '<p class="sec-title"><span class="sec-title-icon">👷</span>Labourer Details</p>',
            unsafe_allow_html=True)
        worker_fields = []
        wcols = st.columns(min(n_workers, 2), gap="large")
        for wi in range(n_workers):
            ew = W[wi] if wi < len(W) else {"name": "", "full_name": ""}
            with wcols[wi % 2]:
                st.markdown(
                    f'<p style="font-size:.7rem;font-weight:700;color:#1B4DB0;text-transform:uppercase;letter-spacing:.6px;margin:0 0 .5rem">Labourer {wi + 1}</p>',
                    unsafe_allow_html=True)
                wn = st.text_input(
                    "Name (UPPERCASE) *", value=ew["name"],
                    placeholder="e.g. THAYAMMA", key=f"wn_{wi}",
                    autocomplete="off")
                wf = st.text_input(
                    "Full Name with Title *", value=ew["full_name"],
                    placeholder="e.g. Smt. THAYAMMA", key=f"wf_{wi}",
                    autocomplete="off")
                worker_fields.append({"name": wn.strip().upper(), "full_name": wf.strip()})

        # ── Form actions ──────────────────────────────────
        sc1, sc2, _ = st.columns([2, 2, 3])
        with sc1:
            saved = st.form_submit_button(
                "💾  Save Station Details", type="primary", use_container_width=True)
        with sc2:
            reset = st.form_submit_button(
                "↩️  Reset to Default", use_container_width=True)

        if saved:
            errs = []
            if not f_name.strip():     errs.append("Station Name is required")
            if not f_div.strip():      errs.append("Division / Station Code is required")
            if not f_officer.strip():  errs.append("Station Manager Name is required")
            if not f_atm.strip():      errs.append("ATM Card No. is required")
            if any(not wf["name"] or not wf["full_name"] for wf in worker_fields):
                errs.append("All labourer Name and Full Name fields must be filled")

            if errs:
                for e in errs:
                    st.error(f"❌ {e}")
            else:
                st.session_state.station = {
                    "name":              f_name.strip().upper(),
                    "division":          f_div.strip().upper(),
                    "officer_name":      f_officer.strip(),
                    "atm_no":            f_atm.strip(),
                    "auto_phone":        f_phone.strip(),
                    "mobile":            f_mobile.strip(),
                    "sanctioned_amount": int(f_sanc),
                    "daily_wage":        int(f_wage),
                    "workers":           worker_fields[:n_workers],
                }
                save_settings(st.session_state.station)
                st.success(
                    f"✅ Station details saved for **{st.session_state.station['name']}**. "
                    f"Go to Generate & Download to create documents.")
                st.rerun()

        if reset:
            st.session_state.station = copy.deepcopy(STATION_DEFAULT)
            save_settings(st.session_state.station)
            st.success("↩️ Station details have been reset.")
            st.rerun()
