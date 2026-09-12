"""
Tab 2 — Labour: worker attendance inputs, wage computation, and leave
day selection (automatic by default, with an optional manual override
per worker for matching real recorded attendance).

IMPORTANT: the automatic leave-day assignment here (last N days of the
month, non-overlapping, in worker order) must exactly match the
fallback algorithm in docx_engine/labour.py's generate_labour_annexure()
when no explicit leave_days are passed. They diverged once before —
this screen showed one set of leave dates while the generated document
showed a different, randomly-chosen set.

When a worker's leave dates are customized here, the EXACT selected
days are passed through to the docx engine via ui/tab_generate.py, so
the generated document always matches what's shown on screen — never
independently recomputed.

Widget keys are scoped per station+month (core/balance_store.month_key)
so switching months/stations doesn't leave stale values behind.
"""
import streamlit as st

from core.balance_store import month_key
from core.state import init_default
from core.sanitize import esc


def _auto_leave_sets(W, worker_inputs, days_in_month):
    """Same deterministic algorithm as docx_engine/labour.py's fallback:
    take leave days from the end of the month, in worker order, with no
    overlap. Returns {worker_index: set(days)}."""
    remaining = list(range(1, days_in_month + 1))
    leave_sets = {}
    for wi in range(len(W)):
        lv = worker_inputs[wi]["leaves"]
        ls = set(remaining[-lv:]) if lv else set()
        leave_sets[wi] = ls
        remaining = [d for d in remaining if d not in ls]
    return leave_sets


def render_tab_labour(station, sel_month, sel_year, days_in_month):
    """
    Renders the Labour tab. Returns (worker_inputs, leave_invalid).

    worker_inputs is a dict of {worker_index: {...}} with
    days_worked/total/leaves/leave_days per worker, for Tab 3 to
    consume. "leave_days" is a sorted list of the exact calendar day
    numbers that worker is on leave — either auto-assigned or manually
    picked.

    leave_invalid is True when the combined leave days exceed the
    month, or (in manual mode) when workers' picked leave days overlap
    or don't match the count implied by Days Worked — Tab 3 should
    block generation when this is True.
    """
    W  = station["workers"]
    DW = station["daily_wage"]
    mk = month_key(station["name"], sel_month, sel_year)

    # --- Visibility fixes -------------------------------------------------
    # 1) The "Customize leave dates" checkbox label was rendering invisible
    #    (text color matched the background) on some Streamlit themes.
    # 2) Selected tags inside the per-worker leave-day multiselects were
    #    rendering as black-on-black — force a white pill with dark text
    #    so the picked days are always readable, regardless of theme.
    st.markdown("""
    <style>
    /* Checkbox label text — force a visible dark color */
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stCheckbox"] label span {
        color: #1E293B !important;
        opacity: 1 !important;
    }

    /* Multiselect: selected day "tags/pills" */
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #DBEAFE !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 999px !important;
    }
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
        color: #1E40AF !important;
        fill: #1E40AF !important; /* the little "x" remove icon */
    }

    /* Multiselect: the bar/box itself (not just its tags) */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"],
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #1E293B !important;
    }
    /* Dropdown chevron / clear-all icons drawn directly in the bar
       (not inside a selected-day tag) — keep them visible on white */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div > div svg {
        fill: #64748B !important;
    }

    /* Dropdown options list */
    div[data-baseweb="popover"] li {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #F1F5F9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p class="sec-title"><span class="sec-title-icon">👷</span>Worker Attendance</p>',
        unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:9px;padding:0.75rem 1rem;
                font-size:0.8rem;color:#1E40AF;margin-bottom:1.2rem;line-height:1.6">
        💡 <strong>Leave rule:</strong> leave days are auto-assigned from the end of the month by
        default — no two workers share the same leave day. Daily wage: <strong>₹{DW}</strong> per day.
        Turn on <strong>Customize leave dates</strong> below to match real recorded attendance instead.
    </div>
    """, unsafe_allow_html=True)

    customize_key = f"customize_leaves_{mk}"
    init_default(customize_key, False)
    customize = st.checkbox(
        "📅 Select this option to enter the exact leave days",
        key=customize_key,
        help="By default, leave days are picked automatically (the last "
             "few days of the month). Turn this on to instead choose the "
             "exact calendar days each worker was on leave — useful when "
             "you have the real attendance record and want the document "
             "to match it exactly.")
    st.markdown(
        '<hr style="margin:0 0 1rem;border:none;border-top:2px solid #E2E8F0">',
        unsafe_allow_html=True)
    if customize:
        st.markdown(
            '<p style="color:#059669;font-weight:700;font-size:0.85rem;margin:0.4rem 0 1rem">'
            '✅ Manual mode — pick each worker\'s exact leave days below.</p>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<p style="color:#64748B;font-size:0.85rem;margin:0.4rem 0 1rem">'
            'Leave days are being assigned automatically. Turn on the box above to pick them yourself.</p>',
            unsafe_allow_html=True)

    cols = st.columns(len(W), gap="large")
    worker_inputs = {}

    for wi, (w, col) in enumerate(zip(W, cols)):
        with col:
            wname = esc(w["full_name"]) if w["full_name"] else f"Worker {wi + 1}"
            st.markdown(f"""
            <div class="worker-card-header">
                <div class="worker-avatar">👷</div>
                <div>
                    <p class="worker-name">{wname}</p>
                    <p class="worker-sub">Cleaning Labour</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            wkey = f"worker_{wi}_{mk}"
            init_default(wkey, min(27, days_in_month))
            days_worked = st.number_input(
                "Days Worked", min_value=0, max_value=days_in_month, key=wkey)
            total  = days_worked * DW
            leaves = days_in_month - days_worked
            worker_inputs[wi] = {"days_worked": days_worked, "total": total, "leaves": leaves}
            st.markdown(f"""
            <div class="worker-stat-row">
                <div class="worker-stat">
                    <p class="ws-label">Days Worked</p>
                    <p class="ws-val">{days_worked}</p>
                </div>
                <div class="worker-stat">
                    <p class="ws-label">Days Leave</p>
                    <p class="ws-val leave">{leaves}</p>
                </div>
                <div class="worker-stat">
                    <p class="ws-label">Total Wages</p>
                    <p class="ws-val wage">₹{total:,}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    combined_leaves = sum(v["leaves"] for v in worker_inputs.values())
    if combined_leaves > days_in_month:
        st.error(
            f"⚠️ Combined leave days ({combined_leaves}) exceed the total days in "
            f"{sel_month.title()} ({days_in_month}). Workers cannot share leave days — "
            f"please reduce leave days.")
        for wi in range(len(W)):
            worker_inputs[wi]["leave_days"] = []
        return worker_inputs, True

    auto_sets = _auto_leave_sets(W, worker_inputs, days_in_month)

    if not customize:
        # Automatic mode — same behavior as before.
        for wi in range(len(W)):
            worker_inputs[wi]["leave_days"] = sorted(auto_sets[wi])

        any_leave = any(worker_inputs[wi]["leaves"] > 0 for wi in range(len(W)))
        if any_leave:
            lines = []
            for wi, w in enumerate(W):
                wname = esc(w["full_name"]) if w["full_name"] else f"Worker {wi + 1}"
                ds = ", ".join(map(str, worker_inputs[wi]["leave_days"])) or "None"
                lines.append(f"&nbsp;&nbsp;{wname} off on: <strong>Day(s) {ds}</strong>")
            st.markdown(
                f'<div class="leave-banner">✅ <strong>Leave plan confirmed — no overlaps</strong><br>'
                f'{"<br>".join(lines)}</div>', unsafe_allow_html=True)
    else:
        # Manual mode — one multiselect per worker, defaulting to the
        # automatic assignment but fully editable. The generated
        # document uses exactly what's picked here (see ui/tab_generate.py).
        st.markdown(
            '<p class="sec-title"><span class="sec-title-icon">🗓️</span>Pick Leave Days</p>',
            unsafe_allow_html=True)
        day_options = list(range(1, days_in_month + 1))
        picked = {}
        pick_cols = st.columns(len(W), gap="large")
        for wi, (w, col) in enumerate(zip(W, pick_cols)):
            with col:
                wname = esc(w["full_name"]) if w["full_name"] else f"Worker {wi + 1}"
                pkey = f"leavepick_{wi}_{mk}"
                if pkey not in st.session_state:
                    st.session_state[pkey] = sorted(auto_sets[wi])
                selected = st.multiselect(
                    f"{wname} — leave days", day_options, key=pkey)
                picked[wi] = sorted(selected)
                needed = worker_inputs[wi]["leaves"]
                if len(selected) != needed:
                    st.warning(
                        f"⚠️ {wname}: picked {len(selected)} day(s), but "
                        f"Days Worked implies {needed} leave day(s). Adjust "
                        f"the selection or the Days Worked value above so "
                        f"they match.")

        # Check for overlapping picks across workers.
        overlap_found = False
        seen = set()
        for wi in range(len(W)):
            dup = seen & set(picked[wi])
            if dup:
                overlap_found = True
            seen |= set(picked[wi])
        if overlap_found:
            st.error(
                "⚠️ Two or more workers have overlapping leave days selected. "
                "Each calendar day can only be one worker's leave day at a time.")

        mismatch_found = any(
            len(picked[wi]) != worker_inputs[wi]["leaves"] for wi in range(len(W)))

        for wi in range(len(W)):
            worker_inputs[wi]["leave_days"] = picked[wi]
        leave_invalid = overlap_found or mismatch_found
        return worker_inputs, leave_invalid

    return worker_inputs, False
