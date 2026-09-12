"""
Central configuration: month list, template paths, settings-file path,
and the blank-station default. Nothing here talks to Streamlit — this
module is imported by both the docx engine and the UI layer, so it has
to stay dependency-free.
"""
import os

MONTHS = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
]

# Directory this file lives in — used to build absolute paths so the app
# works regardless of the process's current working directory.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATES_DIR = os.path.join(_BASE_DIR, "templates")
ANNEXURE_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "ANNEXURE_TEMPLATE.docx")
LABOUR_TEMPLATE_PATH   = os.path.join(TEMPLATES_DIR, "LABOUR_TEMPLATE.docx")

SETTINGS_PATH = os.path.join(_BASE_DIR, "settings.ini")

# Blank default station. Used for first-run initialisation, form resets,
# and as the fallback if settings.ini is missing or corrupt.
STATION_DEFAULT = {
    "name":              "",
    "division":          "",
    "officer_name":      "",
    "auto_phone":        "",
    "mobile":            "",
    "atm_no":            "",
    "sanctioned_amount": 25000,
    "daily_wage":        380,
    "workers": [
        {"name": "", "full_name": ""},
        {"name": "", "full_name": ""},
    ],
}
