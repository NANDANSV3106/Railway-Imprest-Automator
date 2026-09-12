"""
Tab 3 — Generate & Download: opening balance (auto-filled from the
previous month via core/balance_store), financial summary, template
validation, document generation, and download cards.

CSS classes used here (sec-title, fin-grid, fin-card, breakdown-row,
breakdown-item, dl-card, ...) come from the reference app's styles.py
— see ui/styles.py's docstring.
"""
import streamlit as st

from config import ANNEXURE_TEMPLATE_PATH, LABOUR_TEMPLATE_PATH
from core.num_to_words import amount_in_words
from core.sanitize import esc
from core.validation import (
    count_labour_template_worker_slots,
    validate_annexure1_template,
    validate_labour_template,
)
from core.balance_store import (
    save_closing_balance, get_opening_balance,
    get_prev_month, month_key,
)
from docx_engine.annexure1 import generate_annexure_1
from docx_engine.labour import generate_labour_annexure


def render_tab_generate(station, expenses, worker_inputs, leave_invalid,
                         sel_month, sel_year, days_in_month, month_idx):
    S, W, SAL, DW = station, station["workers"], station["sanctioned_amount"], station["daily_wage"]
    SH = {k: (esc(v) if isinstance(v, str) else v) for k, v in S.items() if k != "workers"}
    WH = [{kk: (esc(vv) if isinstance(vv, str) else vv) for kk, vv in w.items()} for w in W]

    num_bills      = expenses["num_bills"]
    has_stationery = expenses["has_stationery"]
    num_vouchers   = expenses["num_vouchers"]
    v1_amt, v1_items, v1_date = expenses["v1_amt"], expenses["v1_items"], expenses["v1_date"]
    v2_amt, v2_items, v2_date = expenses["v2_amt"], expenses["v2_items"], expenses["v2_date"]
    cash_total = expenses["cash_total"]

    labour_total   = sum(worker_inputs[i]["total"] for i in range(len(W)))
    total_expended = int(cash_total) + labour_total

    tha_total = worker_inputs[0]["total"] if len(W) > 0 else 0
    dev_total = worker_inputs[1]["total"] if len(W) > 1 else 0

    # ── Opening balance — auto-filled from last month's closing balance ──
    st.markdown(
        '<p class="sec-title"><span class="sec-title-icon">💳</span>Opening Balance</p>',
        unsafe_allow_html=True)

    prev_month_name, prev_year_name = get_prev_month(sel_month, sel_year)
    ob_key = f"opening_balance_{month_key(S['name'], sel_month, sel_year)}"
    if ob_key not in st.session_state:
        prev_closing = get_opening_balance(S["name"], sel_month, sel_year, default=None) if S["name"] else None
        st.session_state[ob_key] = prev_closing if prev_closing is not None else 0

    opening_balance = st.number_input(
        "Opening Balance carried forward from last month (Rs.)",
        min_value=0, key=ob_key, label_visibility="collapsed")

    _prev_closing_display = get_opening_balance(S["name"], sel_month, sel_year, default=None) if S["name"] else None
    if _prev_closing_display is not None:
        st.markdown(f"""
        <p style="font-size:0.78rem;color:#94A3B8;margin:-6px 0 1rem 0">
            ✅ Auto-filled from {prev_month_name.title()} {prev_year_name}'s closing balance
            (₹{_prev_closing_display:,}). Edit if needed.
        </p>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <p style="font-size:0.78rem;color:#94A3B8;margin:-6px 0 1rem 0">
            ⚠️ No stored closing balance found for {prev_month_name.title()} {prev_year_name} —
            enter it manually. Generating {sel_month.title()} {sel_year} will save its closing
            balance for next month.
        </p>""", unsafe_allow_html=True)

    atm_recoupment  = SAL - int(opening_balance)
    closing_balance = SAL - total_expended
    is_negative     = closing_balance < 0

    # ── Station summary ──
    worker_names_str = " · ".join(wh["full_name"] for wh in WH)
    st.markdown(f"""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:.9rem 1.1rem;margin-bottom:1.2rem">
        <p style="font-size:1rem;font-weight:700;color:#1B4DB0;margin:0 0 .6rem">
            📋 Generating for: {SH['name']} — {sel_month.title()} {sel_year}</p>
        <p style="font-size:.9rem;color:#64748B;margin:0">
            {SH['division']} · {SH['officer_name']} · ATM {SH['atm_no']} · {worker_names_str}</p>
    </div>""", unsafe_allow_html=True)

    # ── Financial cards ──
    st.markdown(
        '<p class="sec-title"><span class="sec-title-icon">📊</span>Financial Summary</p>',
        unsafe_allow_html=True)
    st.markdown(f"""
    <div class="fin-grid">
        <div class="fin-card blue">
            <span class="fin-icon">🏦</span>
            <p class="fin-label">Opening Balance</p>
            <p class="fin-value">₹{int(opening_balance):,}</p>
            <p class="fin-sub">From last month</p>
        </div>
        <div class="fin-card amber">
            <span class="fin-icon">🏧</span>
            <p class="fin-label">ATM Recoupment</p>
            <p class="fin-value">₹{atm_recoupment:,}</p>
            <p class="fin-sub">Required this month</p>
        </div>
        <div class="fin-card violet">
            <span class="fin-icon">💸</span>
            <p class="fin-label">Total Expended</p>
            <p class="fin-value">₹{total_expended:,}</p>
            <p class="fin-sub">{amount_in_words(total_expended)[:28]}…</p>
        </div>
        <div class="fin-card {'red' if is_negative else 'green'}">
            <span class="fin-icon">{'⚠️' if is_negative else '✅'}</span>
            <p class="fin-label">Closing Balance</p>
            <p class="fin-value" style="color:{'#DC2626' if is_negative else '#059669'}">₹{closing_balance:,}</p>
            <p class="fin-sub">{'Overspent!' if is_negative else 'Carry forward'}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Breakdown ──
    st.markdown(
        '<p class="sec-title"><span class="sec-title-icon">📂</span>Expenditure Breakdown</p>',
        unsafe_allow_html=True)
    worker_items = "".join(
        f'''<div class="breakdown-item">
            <p class="bd-label">👷 {WH[i]["full_name"]} Wages</p>
            <p class="bd-value">₹{int(worker_inputs[i]["total"]):,}</p>
            <p class="bd-sub">{worker_inputs[i]["days_worked"]} days × ₹{DW}</p>
        </div>''' for i in range(len(W)))
    st.markdown(f"""
    <div class="breakdown-row">
        <div class="breakdown-item">
            <p class="bd-label">🛒 Consumables</p>
            <p class="bd-value">₹{int(cash_total):,}</p>
            <p class="bd-sub">Voucher 1{" + 2" if num_bills == 2 else ""}</p>
        </div>
        {worker_items}
        <div class="breakdown-item" style="border-color:#1B4DB0">
            <p class="bd-label">📋 Grand Total</p>
            <p class="bd-value" style="color:#1B4DB0">₹{total_expended:,}</p>
            <p class="bd-sub">of ₹{SAL:,} sanctioned</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if is_negative:
        st.error(
            f"⚠️ Closing balance is negative (₹{closing_balance:,}). "
            f"You have overspent the sanctioned amount by ₹{abs(closing_balance):,}. "
            "Please review your entries before generating.")

    # ── Template structural validation ──
    a1t, lt = ANNEXURE_TEMPLATE_PATH, LABOUR_TEMPLATE_PATH
    a1_missing = validate_annexure1_template(a1t)
    lb_missing = validate_labour_template(lt)
    template_invalid = bool(a1_missing) or bool(lb_missing)
    if a1_missing:
        st.error(
            f"❌ `ANNEXURE_TEMPLATE.docx` doesn't look like a valid Annexure-1 template — "
            f"missing: {', '.join(a1_missing)}. If this file actually contains the Labour "
            f"Annexure content, the two template files may be swapped.")
    if lb_missing:
        st.error(
            f"❌ `LABOUR_TEMPLATE.docx` doesn't look like a valid Labour Annexure template — "
            f"missing: {', '.join(lb_missing)}. If this file actually contains the Annexure-1 "
            f"content, the two template files may be swapped.")

    # ── Template capacity check ──
    template_slots   = count_labour_template_worker_slots(lt)
    too_many_workers = template_slots > 0 and len(W) > template_slots
    if too_many_workers:
        st.error(
            f"⚠️ This Labour Annexure template supports {template_slots} worker(s), but "
            f"{S['name'] or 'this station'} has {len(W)} configured. The extra worker(s) "
            f"would be left out of the generated document. Reduce the worker count in "
            f"Station Details, or use a template with more worker slots.")

    blocked = is_negative or too_many_workers or template_invalid or leave_invalid

    # ── Generate ──
    st.markdown(
        '<p class="sec-title"><span class="sec-title-icon">⚡</span>Generate Documents</p>',
        unsafe_allow_html=True)
    gc, _ = st.columns([2, 1])
    with gc:
        gen_clicked = st.button("🚀  Generate All Documents", type="primary", disabled=blocked)
    if is_negative:
        st.caption("⛔ Fix the negative closing balance before generating documents.")
    elif too_many_workers:
        st.caption("⛔ Reduce workers to match the template's capacity before generating.")
    elif template_invalid:
        st.caption("⛔ Fix the template file(s) before generating.")
    elif leave_invalid:
        st.caption("⛔ Fix the leave-day selection on the Labour tab before generating.")

    if gen_clicked and not blocked:
        try:
            with st.spinner("🚆 Generating Railway Documents..."):
                af = generate_annexure_1(
                    a1t, sel_month, sel_year,
                    int(opening_balance), atm_recoupment, int(cash_total),
                    int(dev_total), int(tha_total), total_expended, int(closing_balance),
                    SAL, int(v1_amt), int(v2_amt), v1_date, v2_date,
                    v1_items=int(v1_items), v2_items=int(v2_items),
                    num_vouchers=num_vouchers,
                    has_stationery=has_stationery, station=S)
                worker_days_list = [int(worker_inputs[i]["days_worked"]) for i in range(len(W))]
                leave_days_list  = [set(worker_inputs[i]["leave_days"]) for i in range(len(W))]
                lf = generate_labour_annexure(
                    lt, sel_month, sel_year,
                    worker_days_list, DW, station=S,
                    num_vouchers=num_vouchers,
                    leave_days=leave_days_list)
            tag = S["name"].replace(" ", "_")
            st.session_state["annex_1_bytes"] = af.read()
            st.session_state["labour_bytes"]  = lf.read()
            st.session_state["annex_1_name"]  = f"ANNEXURE_1_{tag}_{sel_month}_{sel_year}.docx"
            st.session_state["labour_name"]   = f"LABOUR_{tag}_{sel_month}_{sel_year}.docx"
            st.session_state["gen_meta"] = {
                "station": S["name"], "month": sel_month, "year": sel_year,
                "total": total_expended, "closing": closing_balance,
                "vouchers": num_vouchers,
            }
            if S["name"]:
                save_closing_balance(S["name"], sel_month, sel_year, closing_balance)
            st.success("✅ Both documents generated successfully — download them below.")
        except FileNotFoundError:
            st.error(
                "❌ Template files not found!  \n"
                "Make sure these two files exist in the **templates/** folder:  \n"
                "• `ANNEXURE_TEMPLATE.docx`  \n"
                "• `LABOUR_TEMPLATE.docx`")
        except Exception as e:
            st.error(f"❌ Generation error: {e}")

    # ── Download cards ──
    if "annex_1_bytes" in st.session_state and "labour_bytes" in st.session_state:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<p class="sec-title"><span class="sec-title-icon">⬇️</span>Download Documents</p>',
            unsafe_allow_html=True)
        dl1, dl2 = st.columns(2, gap="large")

        with dl1:
            st.markdown(f"""
            <div class="dl-card">
                <div class="dl-card-header">
                    <div class="dl-file-icon">📄</div>
                    <div>
                        <p class="dl-file-title">Annexure I — Master Bill</p>
                        <p class="dl-file-sub">Balance sheet, summary, ledger &amp; certification</p>
                    </div>
                </div>
                <div class="dl-filename">{esc(st.session_state['annex_1_name'])}</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "⬇️  Download Annexure I",
                data=st.session_state["annex_1_bytes"],
                file_name=st.session_state["annex_1_name"],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="dl_annex1", use_container_width=True)

        with dl2:
            st.markdown(f"""
            <div class="dl-card">
                <div class="dl-card-header">
                    <div class="dl-file-icon">👷</div>
                    <div>
                        <p class="dl-file-title">Annexure II — Labour</p>
                        <p class="dl-file-sub">Attendance register &amp; wage disbursement</p>
                    </div>
                </div>
                <div class="dl-filename">{esc(st.session_state['labour_name'])}</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "⬇️  Download Labour Annexure",
                data=st.session_state["labour_bytes"],
                file_name=st.session_state["labour_name"],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="dl_labour", use_container_width=True)
