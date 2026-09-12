"""
Persistence layer.

Two separate concerns live here:
  1. Station configuration (name, division, officer, workers, ...) —
     one active station profile, persisted to settings.ini.
  2. Per-station, per-month closing balances — so next month's
     "Opening Balance" can be auto-suggested from last month's closing
     balance instead of the user having to remember/re-type it.
"""
import os
import copy
import configparser

from config import STATION_DEFAULT, SETTINGS_PATH, MONTHS, _BASE_DIR

BALANCES_PATH = os.path.join(_BASE_DIR, "balances.ini")


# ── Station config ──────────────────────────────────────────────────

def save_settings(station_dict, path=SETTINGS_PATH):
    """Write a station dict to settings.ini using configparser."""
    cfg = configparser.ConfigParser()
    cfg["station"] = {
        "name":              station_dict["name"],
        "division":          station_dict["division"],
        "officer_name":      station_dict["officer_name"],
        "auto_phone":        station_dict["auto_phone"],
        "mobile":            station_dict["mobile"],
        "atm_no":            station_dict["atm_no"],
        "sanctioned_amount": str(station_dict["sanctioned_amount"]),
        "daily_wage":        str(station_dict["daily_wage"]),
        "num_workers":       str(len(station_dict["workers"])),
    }
    for i, w in enumerate(station_dict["workers"]):
        cfg[f"worker_{i}"] = {
            "name":      w["name"],
            "full_name": w["full_name"],
        }
    with open(path, "w", encoding="utf-8") as f:
        cfg.write(f)


def load_settings(path=SETTINGS_PATH):
    """Read settings.ini and return a station dict.

    If the file is missing, corrupt, or incomplete the blank default
    config is written to disk and returned instead.
    """
    try:
        if not os.path.isfile(path):
            raise FileNotFoundError
        cfg = configparser.ConfigParser()
        cfg.read(path, encoding="utf-8")
        n_workers = int(cfg.get("station", "num_workers", fallback="0"))
        if n_workers == 0:
            raise ValueError("num_workers missing or zero")
        workers = []
        for i in range(n_workers):
            sec = f"worker_{i}"
            workers.append({
                "name":      cfg.get(sec, "name"),
                "full_name": cfg.get(sec, "full_name"),
            })
        return {
            "name":              cfg.get("station", "name"),
            "division":          cfg.get("station", "division"),
            "officer_name":      cfg.get("station", "officer_name"),
            "auto_phone":        cfg.get("station", "auto_phone"),
            "mobile":            cfg.get("station", "mobile"),
            "atm_no":            cfg.get("station", "atm_no"),
            "sanctioned_amount": int(cfg.get("station", "sanctioned_amount")),
            "daily_wage":        int(cfg.get("station", "daily_wage")),
            "workers":           workers,
        }
    except Exception:
        # File missing / corrupt / incomplete → recreate from defaults
        defaults = copy.deepcopy(STATION_DEFAULT)
        save_settings(defaults, path)
        return defaults


# ── Month-key helpers ───────────────────────────────────────────────

def get_prev_month(month, year):
    """Return (prev_month_name, prev_year_str) for a given MONTHS entry + year."""
    idx = MONTHS.index(month.upper())
    if idx == 0:
        return MONTHS[11], str(int(year) - 1)
    return MONTHS[idx - 1], str(year)


def get_next_month(month, year):
    """Return (next_month_name, next_year_str) for a given MONTHS entry + year."""
    idx = MONTHS.index(month.upper())
    if idx == 11:
        return MONTHS[0], str(int(year) + 1)
    return MONTHS[idx + 1], str(year)


def month_key(station_name, month, year):
    """
    Short string uniquely identifying a (station, month, year) triple,
    e.g. "SETTIHALLI-2026-07". Used to suffix widget keys (see
    core/state.init_default) so each station+month combination gets its
    own session_state slot — switching the sidebar's month, or the
    active station, shouldn't leave a previous selection's typed
    amounts showing up unreset.
    """
    idx = MONTHS.index(month.upper()) + 1
    safe_station = (station_name or "UNSET").strip().upper().replace(" ", "_")
    return f"{safe_station}-{year}-{idx:02d}"


# ── Closing-balance carry-forward ───────────────────────────────────

def _balance_key(station_name, month, year):
    # configparser section names are case-sensitive strings; station
    # names may contain spaces/slashes, so keep the raw text but scope
    # it under a fixed prefix to avoid collisions with other sections.
    return f"balance::{station_name}::{month.upper()}::{year}"


def save_closing_balance(station_name, month, year, closing_balance, path=BALANCES_PATH):
    """Record this station+month's closing balance so it can be offered
    as next month's opening balance."""
    cfg = configparser.ConfigParser()
    if os.path.isfile(path):
        cfg.read(path, encoding="utf-8")
    section = _balance_key(station_name, month, year)
    cfg[section] = {"closing_balance": str(int(closing_balance))}
    with open(path, "w", encoding="utf-8") as f:
        cfg.write(f)


def get_opening_balance(station_name, month, year, default=0, path=BALANCES_PATH):
    """Look up the PREVIOUS month's closing balance for this station, to
    suggest as this month's opening balance. Falls back to `default` if
    nothing is on record (e.g. first month using the app)."""
    if not os.path.isfile(path):
        return default
    prev_month, prev_year = get_prev_month(month, year)
    cfg = configparser.ConfigParser()
    cfg.read(path, encoding="utf-8")
    section = _balance_key(station_name, prev_month, prev_year)
    try:
        return int(cfg.get(section, "closing_balance"))
    except Exception:
        return default
