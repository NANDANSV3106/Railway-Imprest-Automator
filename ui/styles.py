"""
Global CSS injected once at app startup — overrides Streamlit's default
widget chrome to match the custom design (sidebar, cards, tabs, etc.).

This is the exact CSS from the working single-station reference app,
adopted verbatim rather than reconstructed — an earlier rewrite of
this file used different class names than the rest of the UI modules
and silently broke the sidebar/tabs/cards styling (a class used in
markup but not defined here, or vice versa, just falls back to
unstyled Streamlit defaults with no error). If you change class names
here, grep the ui/ folder for every file using them (sidebar.py,
tab_expenses.py, tab_labour.py, tab_generate.py, tab_station.py,
app.py) and update all of them together.
"""
import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    /* ── Reset & Base ─────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    *, *::before, *::after { box-sizing: border-box; }
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .stApp { background: #EEF2F7 !important; }
    
    /* Hide Streamlit default chrome — but keep the sidebar re-open
       control visible. Hiding the whole <header> also hides the
       ">>" collapsedControl button that lives inside it, which made
       the sidebar impossible to re-open once collapsed. */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 2.5rem !important;
    }
    header[data-testid="stHeader"] * { visibility: visible !important; }
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        z-index: 999999 !important;
    }
    .block-container {
        padding: 1.5rem 2rem 3rem 2rem !important;
        max-width: 1180px !important;
    }
    
    /* ── Sidebar ───────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: #0F2A5C !important;
        border-right: 1px solid #1a3a7a !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.2rem 1rem 1rem 1rem !important;
    }
    /* All sidebar text white */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div { color: #FFFFFF !important; }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stSelectbox svg { fill: white !important; }
    
    /* Sidebar selectbox option text (dropdown list) */
    [data-testid="stSidebar"] [data-baseweb="select"] span { color: #FFFFFF !important; }
    
    /* ── Sidebar custom blocks ─────────────────────────────── */
    .sb-brand {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1.4rem;
    }
    .sb-brand-icon { font-size: 2rem; line-height: 1; }
    .sb-brand-name {
        font-size: 0.95rem; font-weight: 700;
        color: #FFFFFF !important; margin: 6px 0 2px;
    }
    .sb-brand-sub {
        font-size: 0.7rem; color: rgba(255,255,255,0.55) !important;
        margin: 0;
    }
    
    .sb-section-label {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: rgba(255,255,255,0.45) !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin: 1.2rem 0 0.4rem 0 !important;
        display: block;
    }
    
    .sb-period-card {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-top: 0.5rem;
    }
    .sb-period-row {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.6rem;
    }
    .sb-period-chip {
        flex: 1;
        background: rgba(255,255,255,0.1);
        border-radius: 7px;
        padding: 0.4rem 0.5rem;
        text-align: center;
    }
    .sb-chip-label { font-size: 0.6rem; color: rgba(255,255,255,0.5) !important; margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }
    .sb-chip-val   { font-size: 0.78rem; font-weight: 700; color: #FFFFFF !important; margin: 2px 0 0 0; }
    .sb-period-full { font-size: 0.82rem; font-weight: 600; color: #FFFFFF !important; margin: 0; }
    .sb-period-label-txt { font-size: 0.65rem; color: rgba(255,255,255,0.5) !important; margin: 0 0 3px 0; text-transform: uppercase; letter-spacing: 0.8px; }
    
    .sb-footer {
        margin-top: 2rem;
        padding: 0.8rem;
        text-align: center;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    .sb-footer p { font-size: 0.65rem; color: rgba(255,255,255,0.35) !important; margin: 0; line-height: 1.6; }
    
    /* ── Page Header ───────────────────────────────────────── */
    .page-header {
        background: linear-gradient(135deg, #0F2A5C 0%, #1B4DB0 55%, #2563EB 100%);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.6rem;
        display: flex;
        align-items: center;
        gap: 1.2rem;
        box-shadow: 0 4px 24px rgba(15,42,92,0.22);
        position: relative;
        overflow: hidden;
    }
    .page-header::after {
        content: '';
        position: absolute; right: -40px; top: -40px;
        width: 180px; height: 180px;
        background: rgba(255,255,255,0.04);
        border-radius: 50%;
    }
    .ph-icon  { font-size: 2.8rem; line-height: 1; flex-shrink: 0; }
    .ph-title { font-size: 1.45rem; font-weight: 700; color: #FFFFFF; margin: 0; line-height: 1.2; }
    .ph-sub   { font-size: 0.8rem; color: rgba(255,255,255,0.65); margin: 4px 0 0 0; }
    .ph-badge {
        margin-left: auto;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 0.35rem 0.9rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: rgba(255,255,255,0.9);
        white-space: nowrap;
        flex-shrink: 0;
    }
    
    /* ── Tabs ──────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: #FFFFFF !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 0.45rem 0.6rem 0 !important;
        gap: 0.25rem !important;
        border-bottom: 2px solid #E2E8F0 !important;
        box-shadow: 0 -1px 0 0 #E2E8F0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px 9px 0 0 !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.4rem !important;
        color: #64748B !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.15s !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1B4DB0 !important;
        color: #FFFFFF !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: #FFFFFF !important;
        border-radius: 0 0 14px 14px !important;
        padding: 1.8rem 1.8rem 2rem !important;
        border: 1px solid #E2E8F0 !important;
        border-top: none !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05) !important;
    }
    
    /* ── Section title inside tabs ─────────────────────────── */
    .sec-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #1B4DB0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 1rem 0;
        padding-bottom: 0.55rem;
        border-bottom: 2px solid #E2E8F0;
    }
    .sec-title-icon { margin-right: 5px; }
    
    /* ── Mode selector pills ───────────────────────────────── */
    .stRadio > div { gap: 0.5rem !important; }
    .stRadio label {
        background: #F1F5F9 !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 0.45rem 1.1rem !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
        cursor: pointer;
        transition: all 0.15s !important;
    }
    .stRadio label:has(input:checked) {
        background: #EFF6FF !important;
        border-color: #1B4DB0 !important;
        color: #1B4DB0 !important;
        font-weight: 600 !important;
    }
    /* Make radio text always readable */
    .stRadio [data-testid="stWidgetLabel"] p,
    .stRadio label span {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        letter-spacing: 0.2px !important;
        margin-bottom: 0.5rem !important;
    }
    .stRadio label {
        min-width: 200px !important;
        padding: 0.6rem 1.3rem !important;
        font-size: 0.9rem !important;
    }
    .stRadio label p, .stRadio label span {
        color: #1E293B !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    /* ── Inputs ────────────────────────────────────────────── */
    /* ── Main-content selectbox (e.g. Number of Labourers) ───
       White background, dark text, matching the text/number inputs
       below — this selectbox had no explicit styling at all, so it
       was falling back to Streamlit/BaseWeb's own dark default rather
       than matching the rest of the white-card form. Scoped OUTSIDE
       the sidebar and the date-picker calendar popup, both of which
       are styled intentionally elsewhere and must stay untouched. */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        color: #0F172A !important;
    }
    .stSelectbox svg { fill: #0F172A !important; }
    .stSelectbox [data-baseweb="select"] span { color: #0F172A !important; }

    /* ── Main-content multiselect (e.g. Labour tab's leave-day picker) ──
       Same issue as the selectbox above — no styling at all, so it
       fell back to BaseWeb's dark default, which is why the leave-day
       picker showed white-on-dark and was hard to read. White
       background, blue text throughout (both the box itself and each
       selected-day "tag" chip). */
    .stMultiSelect > div > div {
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        color: #1B4DB0 !important;
    }
    .stMultiSelect svg { fill: #1B4DB0 !important; }
    .stMultiSelect [data-baseweb="select"] span { color: #1B4DB0 !important; }
    .stMultiSelect [data-baseweb="tag"] {
        background: #DBEAFE !important;
        border: 1px solid #93C5FD !important;
    }
    .stMultiSelect [data-baseweb="tag"] span {
        color: #1B4DB0 !important;
    }
    .stMultiSelect [data-baseweb="tag"] svg {
        fill: #1B4DB0 !important;
    }

    /* ── Text & Date inputs ─────────────────────────────────── */
    /* Reset the baseweb wrapper's own default border/background first —
       it draws its own rounded box behind the input, which is what was
       causing the double-bar look. Only the inner <input> keeps a border. */
    .stTextInput [data-baseweb="input"],
    .stTextInput [data-baseweb="base-input"],
    .stDateInput [data-baseweb="input"],
    .stDateInput [data-baseweb="base-input"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    /* The <input> below is forced to a taller 46px than BaseWeb's
       default (~38-40px). Its wrapper elements keep their own default
       (shorter) height and often clip overflow — so without matching
       height + visible overflow here, the taller input's bottom edge
       (including its border) gets sliced off by the wrapper. */
    .stTextInput,
    .stTextInput > div,
    .stTextInput [data-baseweb="input"],
    .stTextInput [data-baseweb="base-input"],
    .stDateInput,
    .stDateInput > div,
    .stDateInput [data-baseweb="input"],
    .stDateInput [data-baseweb="base-input"] {
        min-height: 46px !important;
        overflow: visible !important;
    }
    .stTextInput input,
    .stDateInput input {
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        color: #0F172A !important;
        background: #FFFFFF !important;
        padding: 0 0.9rem !important;
        height: 46px !important;
        line-height: 46px !important;
        box-shadow: none !important;
        caret-color: #1B4DB0 !important;
    }
    .stTextInput input:focus,
    .stDateInput input:focus {
        border-color: #1B4DB0 !important;
        box-shadow: 0 0 0 3px rgba(27,77,176,0.1) !important;
        outline: none !important;
    }
    
    /* ── Number input — single unified bar ───────────────────── */
    /* Nuke ALL borders/backgrounds on every wrapper layer */
    .stNumberInput,
    .stNumberInput > div,
    .stNumberInput > div > div,
    .stNumberInput > div > div > div,
    .stNumberInput [data-baseweb="base-input"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        outline: none !important;
    }
    /* Single outer border on the widget's own flex row (holds − button, input, + button).
       NOTE: we do NOT force display/align-items here — Streamlit already lays this
       row out internally, and overriding it pushes the +/- buttons outside the box. */
    .stNumberInput [data-testid="stNumberInputContainer"] {
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
        overflow: hidden !important;
        height: 46px !important;
    }
    .stNumberInput [data-testid="stNumberInputContainer"]:focus-within {
        border-color: #1B4DB0 !important;
        box-shadow: 0 0 0 3px rgba(27,77,176,0.1) !important;
    }
    .stNumberInput [data-baseweb="input"] {
        border: none !important;
        background: #FFFFFF !important;
        height: 100% !important;
    }
    /* Value text field — fills remaining space and remains fully editable */
    .stNumberInput input {
        background: #FFFFFF !important;
        color: #0F172A !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        height: 100% !important;
        padding: 0 0.75rem !important;
        min-width: 0 !important;

        /* Keep the input interactive */
        pointer-events: auto !important;
        user-select: text !important;
        -webkit-user-select: text !important;

        /* Visible blinking text cursor / caret */
        caret-color: #1B4DB0 !important;
        cursor: text !important;
    }

    /* Make sure the input wrapper never blocks typing/clicking */
    .stNumberInput [data-baseweb="input"],
    .stNumberInput [data-baseweb="base-input"],
    .stNumberInput [data-baseweb="input"] > div {
        pointer-events: auto !important;
    }

    /* Strong focus state for the editable number field */
    .stNumberInput input:focus {
        caret-color: #1B4DB0 !important;
        cursor: text !important;
        outline: none !important;
    }

    /* Prevent the +/- controls from covering the editable text area */
    .stNumberInput button {
        position: relative !important;
        z-index: 2 !important;
    }

    .stNumberInput input {
        position: relative !important;
        z-index: 1 !important;
    }
    /* Kill any inner div that adds visual separators */
    .stNumberInput [data-baseweb="input"] > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        height: 100% !important;
    }
    /* − and + buttons flush inside the bar */
    .stNumberInput button {
        width: 36px !important;
        height: 100% !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .stNumberInput button[data-testid="stNumberInputStepDown"] {
        border-left: 1px solid #E2E8F0 !important;
        order: -1 !important;
    }
    .stNumberInput button[data-testid="stNumberInputStepUp"] {
        border-left: 1px solid #E2E8F0 !important;
    }
    .stNumberInput button:hover {
        background: #F1F5F9 !important;
    }
    .stNumberInput button svg {
        fill: #0F172A !important;
        width: 14px !important;
        height: 14px !important;
    }
    .stNumberInput button:hover svg {
        fill: #1B4DB0 !important;
    }
    
    /* ── All input labels ───────────────────────────────────── */
    label[data-testid="stWidgetLabel"] p,
    .stNumberInput label p,
    .stTextInput label p,
    .stDateInput label p {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        margin-bottom: 6px !important;
    }
    
    /* ── Bill / Worker cards ───────────────────────────────── */
    .bill-card {
        background: #F8FAFC;
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem 1.3rem 1rem;
        height: 100%;
    }
    .bill-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding-bottom: 0.7rem;
        border-bottom: 1px solid #E2E8F0;
    }
    .bill-card-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #1B4DB0;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin: 0;
    }
    .bill-card-badge {
        font-size: 0.65rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 20px;
        background: #DBEAFE;
        color: #1E40AF;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .bill-card-badge.inactive {
        background: #F1F5F9;
        color: #94A3B8;
    }
    .bill-card-total-label {
        font-size: 0.65rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0.9rem 0 2px 0;
    }
    .bill-card-total {
        font-size: 1.35rem;
        font-weight: 700;
        color: #059669;
        margin: 0;
        line-height: 1;
    }
    .bill-card-total.zero { color: #94A3B8; }
    .bill-card-disabled {
        background: #F8FAFC;
        border: 1.5px dashed #CBD5E1;
        border-radius: 12px;
        padding: 2.5rem 1.3rem;
        text-align: center;
        color: #94A3B8;
        font-size: 0.82rem;
        font-weight: 500;
    }
    
    /* ── Worker cards (Labour tab) ─────────────────────────── */
    .worker-card {
        background: #F8FAFC;
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem 1.3rem;
    }
    .worker-card-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.7rem;
        border-bottom: 1px solid #E2E8F0;
    }
    .worker-avatar {
        width: 32px; height: 32px;
        border-radius: 50%;
        background: #DBEAFE;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .worker-name {
        font-size: 0.82rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .worker-sub {
        font-size: 0.65rem;
        color: #94A3B8;
        margin: 1px 0 0 0;
    }
    .worker-stat-row {
        display: flex;
        gap: 0.6rem;
        margin-top: 0.9rem;
    }
    .worker-stat {
        flex: 1;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.55rem 0.7rem;
    }
    .ws-label { font-size: 0.62rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; margin: 0; }
    .ws-val   { font-size: 1rem; font-weight: 700; color: #0F172A; margin: 2px 0 0 0; }
    .ws-val.leave { color: #EA580C; }
    .ws-val.wage  { color: #059669; }
    
    /* ── Leave preview banner ──────────────────────────────── */
    .leave-banner {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 10px;
        padding: 0.8rem 1.1rem;
        margin-top: 1rem;
        font-size: 0.8rem;
        color: #166534;
        line-height: 1.6;
    }
    .leave-banner strong { color: #15803D; }
    
    /* ── Financial metric cards ────────────────────────────── */
    .fin-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
        margin-bottom: 1.4rem;
    }
    .fin-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        position: relative;
        overflow: hidden;
    }
    .fin-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: #CBD5E1;
        border-radius: 12px 12px 0 0;
    }
    .fin-card.blue::before   { background: #1B4DB0; }
    .fin-card.amber::before  { background: #D97706; }
    .fin-card.violet::before { background: #7C3AED; }
    .fin-card.green::before  { background: #059669; }
    .fin-card.red::before    { background: #DC2626; }
    
    .fin-icon {
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    .fin-label {
        font-size: 0.65rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 0 0 4px 0;
    }
    .fin-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
        line-height: 1.1;
    }
    .fin-sub {
        font-size: 0.67rem;
        color: #94A3B8;
        margin: 4px 0 0 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* ── Breakdown row ─────────────────────────────────────── */
    .breakdown-row {
        display: flex;
        gap: 0.7rem;
        margin-bottom: 1.4rem;
    }
    .breakdown-item {
        flex: 1;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }
    .bd-label { font-size: 0.65rem; color: #94A3B8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; margin: 0 0 4px 0; }
    .bd-value { font-size: 1.05rem; font-weight: 700; color: #0F172A; margin: 0; }
    .bd-sub   { font-size: 0.67rem; color: #94A3B8; margin: 2px 0 0 0; }
    
    /* ── Generate button ───────────────────────────────────── */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 0.65rem 1.5rem !important;
        transition: all 0.18s !important;
        border: 1.5px solid transparent !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0F2A5C 0%, #1B4DB0 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 18px rgba(27,77,176,0.3) !important;
        width: 100% !important;
        padding: 0.8rem 2rem !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(27,77,176,0.38) !important;
    }
    .stButton > button[kind="primary"]:disabled {
        background: #CBD5E1 !important;
        box-shadow: none !important;
        transform: none !important;
        cursor: not-allowed !important;
    }
    
    /* ── Download file cards ───────────────────────────────── */
    .dl-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.3rem 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 0.9rem;
    }
    .dl-card-header {
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
    }
    .dl-file-icon {
        width: 40px; height: 40px;
        border-radius: 10px;
        background: #DBEAFE;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    .dl-file-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0 0 3px 0;
    }
    .dl-file-sub {
        font-size: 0.7rem;
        color: #94A3B8;
        margin: 0;
    }
    .dl-filename {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.35rem 0.7rem;
        font-size: 0.72rem;
        color: #475569;
        font-family: monospace;
        word-break: break-all;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        width: 100% !important;
        background: #1B4DB0 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.15s !important;
        letter-spacing: 0.2px !important;
    }
    .stDownloadButton > button:hover {
        background: #1440A0 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(27,77,176,0.28) !important;
    }
    
    /* ── Success / error alerts ────────────────────────────── */
    .stAlert {
        border-radius: 10px !important;
        font-size: 0.84rem !important;
        border: none !important;
    }
    
    /* ── Divider ───────────────────────────────────────────── */
    hr { border-color: #E2E8F0 !important; margin: 1.2rem 0 !important; }
    
    /* ── Footer ────────────────────────────────────────────── */
    .page-footer {
        text-align: center;
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid #E2E8F0;
        font-size: 0.72rem;
        color: #94A3B8;
        line-height: 1.8;
    }
    
    /* ── Date input field: calendar icon button ─────────────── */
    .stDateInput [data-baseweb="input"] button { background: #FFFFFF !important; color: #374151 !important; }
    .stDateInput [data-baseweb="input"] svg { fill: #374151 !important; }
    
    /* ── Entire calendar popup ───────────────────────────────── */
    [data-baseweb="datepicker"],
    [data-baseweb="datepicker"] > div,
    [data-baseweb="calendar"],
    [data-baseweb="calendar"] > div {
        background: #FFFFFF !important;
        color: #0F172A !important;
    }
    
    /* ── Month/Year header row ───────────────────────────────── */
    [data-baseweb="calendar"] [data-baseweb="select"] > div,
    [data-baseweb="calendar"] [data-baseweb="select"] > div > div,
    [data-baseweb="calendar"] [data-baseweb="select"] span,
    [data-baseweb="calendar"] [data-baseweb="select"] div {
        background: #FFFFFF !important;
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    /* Dropdown arrow in month/year selects */
    [data-baseweb="calendar"] [data-baseweb="select"] svg { fill: #0F172A !important; }
    
    /* Nav arrows < > */
    [data-baseweb="calendar"] button[aria-label*="previous"],
    [data-baseweb="calendar"] button[aria-label*="next"],
    [data-baseweb="calendar"] button[aria-label*="Previous"],
    [data-baseweb="calendar"] button[aria-label*="Next"] {
        background: #F1F5F9 !important;
        color: #0F172A !important;
        border-radius: 6px !important;
    }
    [data-baseweb="calendar"] button[aria-label*="previous"] svg,
    [data-baseweb="calendar"] button[aria-label*="next"] svg,
    [data-baseweb="calendar"] button[aria-label*="Previous"] svg,
    [data-baseweb="calendar"] button[aria-label*="Next"] svg {
        fill: #0F172A !important;
        stroke: #0F172A !important;
    }
    
    /* ── Day-of-week headers (Su Mo Tu...) ──────────────────── */
    [data-baseweb="calendar"] [aria-label="day header"],
    [data-baseweb="calendar"] [role="columnheader"] {
        color: #64748B !important;
        background: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.75rem !important;
    }
    
    /* ── Day number cells ────────────────────────────────────── */
    [data-baseweb="calendar"] [role="gridcell"] button,
    [data-baseweb="calendar"] [role="gridcell"] div {
        background: transparent !important;
        color: #0F172A !important;
    }
    [data-baseweb="calendar"] [role="gridcell"] button:hover div {
        background: #EFF6FF !important;
        color: #1B4DB0 !important;
        border-radius: 50% !important;
    }
    
    /* ── Selected day ────────────────────────────────────────── */
    [data-baseweb="calendar"] [aria-selected="true"] div,
    [data-baseweb="calendar"] [data-baseweb="day"][aria-selected="true"] div {
        background: #1B4DB0 !important;
        color: #FFFFFF !important;
        border-radius: 50% !important;
    }
    
    /* ── Month/Year dropdown popup list ─────────────────────── */
    [data-baseweb="popover"] [role="option"],
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="popover"] ul li {
        background: #FFFFFF !important;
        color: #0F172A !important;
    }
    [data-baseweb="popover"] [aria-selected="true"] {
        background: #EFF6FF !important;
        color: #1B4DB0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _inject_sidebar_select_fix_js()


def _inject_sidebar_select_fix_js():
    """
    Belt-and-braces JS fallback for the sidebar selectbox CSS above,
    and for the main-content multiselect (Labour tab's leave-day
    picker). Only needed if some Streamlit version re-mounts a BaseWeb
    widget with inline styles that win over our stylesheet — re-asserts
    colors directly on the elements' inline style, which always wins
    over external CSS, on every DOM mutation. Cosmetic only: never
    touches display/visibility/transform, so it cannot fight
    Streamlit's own sidebar open/close state machine (see
    ui/sidebar.py's docstring for why that distinction matters).
    """
    st.markdown("""
<script>
(function () {
    function paintSidebarSelects() {
        document.querySelectorAll(
            '[data-testid="stSidebar"] .stSelectbox > div > div'
        ).forEach(function (el) {
            el.style.setProperty('background', 'rgba(255,255,255,.1)', 'important');
            el.style.setProperty('border', '1px solid rgba(255,255,255,.2)', 'important');
            el.style.setProperty('color', '#FFFFFF', 'important');
        });
        document.querySelectorAll(
            '[data-testid="stSidebar"] [data-baseweb="select"] span'
        ).forEach(function (el) {
            el.style.setProperty('color', '#FFFFFF', 'important');
        });
    }
    function paintMainMultiselect() {
        document.querySelectorAll(
            '.stMultiSelect > div > div'
        ).forEach(function (el) {
            if (el.closest('[data-testid="stSidebar"]')) return;
            el.style.setProperty('background', '#FFFFFF', 'important');
            el.style.setProperty('border', '1.5px solid #CBD5E1', 'important');
            el.style.setProperty('color', '#1B4DB0', 'important');
        });
        document.querySelectorAll(
            '.stMultiSelect [data-baseweb="tag"]'
        ).forEach(function (el) {
            if (el.closest('[data-testid="stSidebar"]')) return;
            el.style.setProperty('background', '#DBEAFE', 'important');
            el.style.setProperty('border', '1px solid #93C5FD', 'important');
        });
        document.querySelectorAll(
            '.stMultiSelect [data-baseweb="tag"] span'
        ).forEach(function (el) {
            if (el.closest('[data-testid="stSidebar"]')) return;
            el.style.setProperty('color', '#1B4DB0', 'important');
        });
    }
    function paintAll() {
        paintSidebarSelects();
        paintMainMultiselect();
    }
    paintAll();
    new MutationObserver(paintAll)
        .observe(document.body, {childList: true, subtree: true});
})();
</script>
""", unsafe_allow_html=True)
