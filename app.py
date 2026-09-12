"""
Railway Imprest Automator — entrypoint.

This file only wires modules together: page config, CSS, sidebar,
tabs, footer. All actual logic lives in core/, docx_engine/, and ui/.

CSS classes used in the header/footer below (page-header, ph-icon,
ph-title, ph-sub, ph-badge, page-footer) come from the reference
app's styles.py — see ui/styles.py's docstring.
"""
import streamlit as st

from core.state import init_app_defaults
from ui.styles import inject_css
from ui.sidebar import render_sidebar
from ui.tab_expenses import render_tab_expenses
from ui.tab_labour import render_tab_labour
from ui.tab_generate import render_tab_generate
from ui.tab_station import render_tab_station
from core.sanitize import esc

st.set_page_config(
    page_title="Railway Imprest Automator",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_app_defaults()
inject_css()

# ── Fix browser autocomplete warnings ────────────────────────
st.markdown("""
<script>
(function fixAutocomplete() {
    function patch() {
        document.querySelectorAll('input').forEach(function(el) {
            if (!el.hasAttribute('autocomplete')) el.setAttribute('autocomplete', 'off');
        });
    }
    patch();
    new MutationObserver(patch).observe(document.body, {childList: true, subtree: true});
})();
</script>
""", unsafe_allow_html=True)

station = st.session_state.station

sel_month, sel_year, days_in_month, month_idx = render_sidebar(station)
st.session_state.selected_month = sel_month
st.session_state.selected_year  = sel_year

# ── Page header ──
stn_display = esc(station["name"]) if station["name"] else "STATION NAME"
st.markdown(f"""
<div class="page-header">
    <div class="ph-icon">🚆</div>
    <div>
        <p class="ph-title">Railway Imprest Automator</p>
        <p class="ph-sub">Generate Annexure I &amp; Labour Annexure for {stn_display} Station</p>
    </div>
    <div class="ph-badge">📅 {sel_month} {sel_year}</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🛒  Consumables",
    "👷  Labour",
    "📊  Generate & Download",
    "⚙️  Station Details",
])

with tab1:
    expenses = render_tab_expenses(station, sel_month, sel_year, days_in_month, month_idx)

with tab2:
    worker_inputs, leave_invalid = render_tab_labour(station, sel_month, sel_year, days_in_month)

with tab3:
    render_tab_generate(station, expenses, worker_inputs, leave_invalid,
                         sel_month, sel_year, days_in_month, month_idx)

with tab4:
    render_tab_station(station)

# ═══════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="page-footer">
    🚆 Railway Imprest Automator &nbsp;·&nbsp; {stn_display} Station &nbsp;·&nbsp;
    {sel_month} {sel_year} &nbsp;·&nbsp; Indian Railways
</div>
""", unsafe_allow_html=True)
