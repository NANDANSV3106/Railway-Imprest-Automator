"""
Tab 1 — Consumables: voucher-mode selection (3 vs 4 vouchers, with or
without a Stationery bill) and Bill 1 / Bill 2 amount + date + item
entry.

Widget keys are scoped per station+month (core/balance_store.month_key)
so switching the sidebar's month/year, or switching the active
station, doesn't leave a previous selection's typed amounts sitting in
a differently-keyed widget that then reappears unreset later.
"""
import streamlit as st

from core.balance_store import month_key
from core.state import init_default


def render_tab_expenses(station, sel_month, sel_year, days_in_month, month_idx):
    """
    Renders the Consumables tab.

    Returns a dict with everything Tab 3 (Generate) needs:
      num_bills, has_stationery, num_vouchers,
      v1_amt, v1_items, v1_date, v2_amt, v2_items, v2_date, cash_total
    """
    st.markdown(
        '<p class="sec-title"><span class="sec-title-icon">⚙️</span>Voucher Mode</p>',
        unsafe_allow_html=True)
    num_bills = st.radio(
        "Voucher mode", [1, 2],
        format_func=lambda x: "3 Vouchers — 1 Consumable Bill" if x == 1 else "4 Vouchers — 2 Bills",
        horizontal=True, label_visibility="collapsed"
    )

    has_stationery = False
    if num_bills == 2:
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        bill2_type = st.radio(
            "Bill 2 type", ["Consumable", "Stationery"],
            horizontal=True, label_visibility="collapsed")
        has_stationery = (bill2_type == "Stationery")

    st.markdown("<hr style='margin:1rem 0'>", unsafe_allow_html=True)

    default_v1_day = min(25, days_in_month)
    default_v2_day = min(26, days_in_month)
    import datetime
    default_d1 = datetime.date(int(sel_year), month_idx, default_v1_day)
    default_d2 = datetime.date(int(sel_year), month_idx, default_v2_day)
    min_date   = datetime.date(int(sel_year), month_idx, 1)
    max_date   = datetime.date(int(sel_year), month_idx, days_in_month)

    mk = month_key(station["name"], sel_month, sel_year)
    v1a_key, v1d_key, v1i_key = f"v1a_{mk}", f"v1d_{mk}", f"v1i_{mk}"
    v2a_key, v2d_key, v2i_key = f"v2a_{mk}", f"v2d_{mk}", f"v2i_{mk}"
    init_default(v1a_key, 0); init_default(v1d_key, default_d1); init_default(v1i_key, 0)
    init_default(v2a_key, 0); init_default(v2d_key, default_d2); init_default(v2i_key, 0)

    if num_bills == 1:
        st.markdown(
            '<p class="sec-title"><span class="sec-title-icon">📋</span>Bill 1 — Consumable</p>',
            unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            v1_amt = st.number_input("Amount (Rs.)", min_value=0, step=10, key=v1a_key)
        with c2:
            v1_date_obj = st.date_input("Date", min_value=min_date, max_value=max_date, key=v1d_key)
        with c3:
            v1_items = st.number_input("Number of Items", min_value=0, step=1, key=v1i_key)
        v1_date = v1_date_obj.strftime("%d/%m/%Y")
        st.markdown(
            f'''<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:9px;
            padding:0.65rem 1rem;margin-top:0.8rem;display:flex;align-items:center;gap:1rem">
            <span style="font-size:0.75rem;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:0.5px">Bill Total</span>
            <span style="font-size:1.4rem;font-weight:800;color:#059669">₹{int(v1_amt):,}</span>
            </div>''', unsafe_allow_html=True)
        v2_amt, v2_items, v2_date = 0, 0, ""
    else:
        lbl2 = "Stationery" if has_stationery else "Consumable"
        cb1, cb2 = st.columns(2, gap="large")
        with cb1:
            st.markdown(
                '<p class="sec-title"><span class="sec-title-icon">📋</span>Bill 1 — Consumable</p>',
                unsafe_allow_html=True)
            v1_amt      = st.number_input("Amount (Rs.)", min_value=0, step=10, key=v1a_key)
            v1_date_obj = st.date_input("Date", min_value=min_date, max_value=max_date, key=v1d_key)
            v1_items    = st.number_input("Number of Items", min_value=0, step=1, key=v1i_key)
            v1_date     = v1_date_obj.strftime("%d/%m/%Y")
            st.markdown(
                f'''<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:9px;
                padding:0.55rem 1rem;margin-top:0.6rem;display:flex;align-items:center;gap:0.8rem">
                <span style="font-size:0.72rem;font-weight:700;color:#166534;text-transform:uppercase">Bill Total</span>
                <span style="font-size:1.2rem;font-weight:800;color:#059669">₹{int(v1_amt):,}</span>
                </div>''', unsafe_allow_html=True)
        with cb2:
            st.markdown(
                f'<p class="sec-title"><span class="sec-title-icon">📋</span>Bill 2 — {lbl2}</p>',
                unsafe_allow_html=True)
            v2_amt      = st.number_input("Amount (Rs.)", min_value=0, step=10, key=v2a_key)
            v2_date_obj = st.date_input("Date", min_value=min_date, max_value=max_date, key=v2d_key)
            v2_items    = st.number_input("Number of Items", min_value=0, step=1, key=v2i_key)
            v2_date     = v2_date_obj.strftime("%d/%m/%Y")
            st.markdown(
                f'''<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:9px;
                padding:0.55rem 1rem;margin-top:0.6rem;display:flex;align-items:center;gap:0.8rem">
                <span style="font-size:0.72rem;font-weight:700;color:#166534;text-transform:uppercase">Bill Total</span>
                <span style="font-size:1.2rem;font-weight:800;color:#059669">₹{int(v2_amt):,}</span>
                </div>''', unsafe_allow_html=True)
            v2_amt = int(v2_amt)

    cash_total = int(v1_amt) + int(v2_amt)
    st.markdown(
        f'''<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:9px;
        padding:0.65rem 1.2rem;margin-top:1rem;display:flex;align-items:center;justify-content:space-between">
        <span style="font-size:0.78rem;font-weight:700;color:#1E40AF;text-transform:uppercase;letter-spacing:0.5px">
            Combined Bill Total (excl. Labour)</span>
        <span style="font-size:1.5rem;font-weight:800;color:#1B4DB0">₹{cash_total:,}</span>
        </div>''', unsafe_allow_html=True)

    num_vouchers = 3 if num_bills == 1 else 4

    return {
        "num_bills": num_bills, "has_stationery": has_stationery,
        "num_vouchers": num_vouchers,
        "v1_amt": int(v1_amt), "v1_items": int(v1_items), "v1_date": v1_date,
        "v2_amt": int(v2_amt), "v2_items": int(v2_items), "v2_date": v2_date,
        "cash_total": cash_total,
    }
