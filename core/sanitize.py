"""HTML-escaping helper for anything user-supplied that gets f-string'd
into an st.markdown(..., unsafe_allow_html=True) block."""
import html


def esc(value):
    """HTML-escape a value for safe interpolation into unsafe_allow_html
    markdown. Use this for ANY user-supplied field (station/officer/
    worker names, etc.) — never for values passed to the docx engine,
    which needs the raw, unescaped text."""
    return html.escape(str(value), quote=True)
