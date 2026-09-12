"""
Labour Annexure generation engine.

Populates the LABOUR_TEMPLATE.docx. Worker "slots" in the template
(each a LABOUR NAME:/signature/Payment-to block) are filled
POSITIONALLY — the Nth "LABOUR NAME:" block found in the document is
always assigned station["workers"][N-1] — rather than by searching the
template text for a name match. Matching by name only ever worked for
whichever station's real worker names happened to already appear as
placeholder text in the template; for any other station it silently
left the placeholder names in the generated document. See
core/validation.py:count_labour_template_worker_slots for the related
capacity check the UI runs before generation.
"""
import docx

from config import STATION_DEFAULT
from core.dates import get_days_in_month
from core.num_to_words import amount_in_words_title
from docx_engine import xml_helpers as xh
from io import BytesIO

def generate_labour_annexure(template_path, month, year,
                             worker_days, wage, station=None, num_vouchers=3,
                             leave_days=None):
    """
    Generate the Labour Annexure document.

    Parameters
    ----------
    worker_days : list[int]
        Days worked for each worker, in the same order as station["workers"].
    wage : int
        Daily wage rate.
    station : dict | None
        Station configuration dict. Defaults to STATION_DEFAULT.
    num_vouchers : int
        3 or 4 — total voucher count for the month (matches Annexure-1's
        num_vouchers), used to number the "Voucher-N" labels on each
        worker's calendar page. Must be passed explicitly by the caller —
        this used to silently fall back to a same-named module-level
        global set elsewhere in the app, which only worked by accident.
    leave_days : list[set[int]] | None
        Optional explicit leave-day sets, one per worker, same order as
        station["workers"]. Each set holds the calendar day numbers
        (1-31) that worker was on leave. When given, these exact days
        are used instead of the auto-computed "last N days of the
        month" default — this is how the UI's manual leave-date picker
        (ui/tab_labour.py) overrides the automatic assignment to match
        real recorded attendance rather than an algorithmic guess. Each
        set's size MUST equal (days_in_month - worker_days[i]) and sets
        must not overlap between workers — the caller (ui/tab_labour.py)
        is responsible for validating this before calling; this function
        does not re-validate it.
    """
    if station is None:
        station = STATION_DEFAULT
    workers  = station["workers"]
    stn_div  = station["division"]
    officer  = station["officer_name"]

    # Build totals map by iterating over all workers
    totals_map = {
        workers[i]["name"].upper(): worker_days[i] * wage
        for i in range(len(workers))
        if i < len(worker_days)
    }

    doc = docx.Document(template_path)
    days, m_idx = get_days_in_month(month, year)
    s_date = f"01/{m_idx:02d}/{year}"
    e_date = f"{days}/{m_idx:02d}/{year}"

    all_month_days = list(range(1, days + 1))

    if leave_days is not None:
        # Explicit leave dates supplied by the caller (manual entry in
        # the UI) — use them exactly as given.
        leave_days_list = [set(leave_days[i]) if i < len(leave_days) else set()
                            for i in range(len(workers))]
    else:
        # Leave logic: sequential non-overlapping assignment for N
        # workers. IMPORTANT: this must exactly match the deterministic
        # algorithm used for the on-screen leave-day preview in Tab 2
        # (Worker Attendance) when it's ALSO not overridden manually
        # there, otherwise the generated document can show different
        # leave dates than what the user reviewed before generating. Do
        # NOT use random.sample() here — leave days are taken from the
        # end of the month, in order, per worker, with no overlap.
        remaining       = list(all_month_days)
        leave_days_list = []
        for i, worker in enumerate(workers):
            wd     = worker_days[i] if i < len(worker_days) else days
            leaves = days - wd
            ld     = set(remaining[-leaves:]) if leaves > 0 else set()
            leave_days_list.append(ld)
            remaining = [d for d in remaining if d not in ld]

    # Worked days map for each worker
    worked_days_map = {
        workers[i]["name"].upper(): sorted(d for d in all_month_days if d not in leave_days_list[i])
        for i in range(len(workers))
    }

    # ── 1. PARAGRAPH REPLACEMENTS ────────────────────────────
    worker_order     = []
    total_paid_paras = []
    and_paid_paras   = []
    date_paras       = []

    # Positional worker tracking. The template has a fixed number of
    # worker "slots" (each a LABOUR NAME:/signature/Payment-to block
    # baked in with placeholder names, e.g. THAYAMMA, DEVAMMA). We can't
    # rely on matching the station's worker NAMES against that
    # placeholder text — that only worked historically because the
    # original single station's real worker happened to be named
    # THAYAMMA/DEVAMMA. For any other station those names never appear
    # in the template, so nothing would match and the placeholder text
    # would leak into the generated document unchanged. Instead, assign
    # workers to slots by the order the slots appear in the document.
    current_worker = {"idx": -1}  # mutable box so the closure below can update it

    n_template_slots = sum(
        1 for p in xh.iter_all_paragraphs(doc) if "LABOUR NAME:" in p.text
    )
    if len(workers) > n_template_slots:
        # Template can't hold this many workers — the extra ones are
        # silently skipped rather than corrupting/duplicating a slot.
        # Surface this to the caller so the UI can warn the user.
        pass  # handled by the truncation below; see generate_labour_annexure's caller

    for p in xh.iter_all_paragraphs(doc):
        txt = p.text

        if "LABOUR NAME:" in txt:
            current_worker["idx"] += 1
            idx = current_worker["idx"]
            if idx < len(workers):
                w = workers[idx]
                worker_order.append(w["name"].upper())
                p.text = (f"         LABOUR NAME: {w['full_name']}"
                          f"                                                              PERIOD: FROM {s_date} TO {e_date}")
            # else: more template slots than configured workers — leave
            # this slot's placeholder text as-is (unused blank slot).

        elif "Payment to Smt" in txt:
            idx = current_worker["idx"]
            if 0 <= idx < len(workers):
                w = workers[idx]
                p.text = (f"\t Payment to {w['full_name']} has been made to and "
                           "received by the payee identified ")

        elif txt.strip().startswith("SMR/") and len(txt.strip()) < 12 and "DATE" not in txt:
            # The template has this line once per worker page, and (per
            # the original template authoring) the first occurrence ends
            # with a period and the second doesn't — a plain
            # `p.text = stn_div` used to overwrite both identically and
            # silently drop whichever trailing punctuation was there.
            # Preserve it instead of guessing a single "correct" form.
            trailing = "." if txt.strip().endswith(".") else ""
            p.text = f"{stn_div}{trailing}"

        elif "(" in txt and ")" in txt and len(txt.strip()) < 30:
            stripped = txt.strip()
            if "for station" in stripped.lower():
                pass  # fixed label, e.g. "(For station cleaning labour)" — leave as-is
            elif officer.split()[-1] in txt or "VENUPRASAD" in txt:
                p.text = f"({officer})"  # officer's own signature line
            else:
                idx = current_worker["idx"]
                if 0 <= idx < len(workers):
                    p.text = f"({workers[idx]['name'].upper()})"

        elif "Total amount paid" in txt:
            total_paid_paras.append(p)

        elif "And paid Rs" in txt or "and paid Rs" in txt:
            and_paid_paras.append(p)

        elif "DATE:" in txt and (
                "Signature" in txt or "labourer" in txt.lower()
                or txt.strip().startswith("DATE:")):
            date_paras.append(p)

    # Build worker_order fallback: ensure all workers are represented
    if not worker_order:
        worker_order = [w["name"].upper() for w in workers]
    else:
        all_worker_names = [w["name"].upper() for w in workers]
        for wname in all_worker_names:
            if wname not in worker_order:
                worker_order.append(wname)

    # Fill "And paid Rs" paragraphs
    for idx, p in enumerate(and_paid_paras):
        cw      = worker_order[idx] if idx < len(worker_order) else worker_order[-1]
        w_total = totals_map.get(cw, worker_days[0] * wage if worker_days else 0)
        p.text  = f"\t    And paid Rs {w_total}/- in presence of the following witness."

    # Fix DATE paragraphs
    for p in date_paras:
        txt       = p.text
        colon_pos = txt.find("DATE:")
        if colon_pos >= 0:
            prefix = txt[:colon_pos + 5]
            suffix = ""
            if "Signature" in txt:
                sig_pos = txt.find("Signature")
                suffix  = "\t\t\t\t\t" + txt[sig_pos:]
            p.text = f"{prefix} {e_date}{suffix}"

    # Fill "Total amount paid" paragraphs — 10pt font (size=20)
    for idx, p in enumerate(total_paid_paras):
        cw      = worker_order[idx] if idx < len(worker_order) else worker_order[-1]
        w_total = totals_map.get(cw, worker_days[0] * wage if worker_days else 0)
        words   = amount_in_words_title(w_total)
        xh.clear_para_runs(p)
        xh.append_run(p, "Total amount paid (in figures and words) = ", bold=True, size=20)
        xh.append_run(p, f"{w_total}/- ",                               bold=True, size=20)
        xh.append_run(p, words,                                          bold=True, size=20)

    # ── 2. FILL CALENDAR TABLES ──────────────────────────────
    # Voucher number map — generalized for N workers
    n_workers  = len(workers)
    vr_num_map = {
        workers[i]["name"].upper(): num_vouchers - n_workers + 1 + i
        for i in range(n_workers)
    }
    # Positional, not name-search: the heading text ("Voucher-N
    # Annexure-2") never contains a worker's name to match against, so
    # a "does this worker's name appear in the heading" check can never
    # legitimately succeed — that's not what selects which heading
    # belongs to which worker. Assign the Nth "Voucher-" heading
    # encountered in document order to the Nth worker, exactly like the
    # LABOUR NAME:/signature blocks above. A previous version of this
    # loop used `if wkey in txt.upper() or True:`, where `or True`
    # short-circuited the condition to always match on the FIRST dict
    # entry — so every heading in the document, regardless of section,
    # was overwritten with worker[0]'s voucher number. That's why both
    # workers' pages showed the same "Voucher-2" label instead of
    # "Voucher-2" / "Voucher-3".
    #
    # Only the "Voucher-N" portion is bold in the template — "Annexure-2"
    # and the surrounding whitespace runs are not. Rewriting p.text
    # directly (as an earlier version did) collapses the whole paragraph
    # into one plain run and silently drops that bold formatting. Instead,
    # find the specific run holding the digit and edit only its text —
    # every other run, and its formatting, is left completely alone.
    heading_idx = 0
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt.startswith("Voucher-") and "Annexure-2" in txt:
            if heading_idx < n_workers:
                vnum = vr_num_map[workers[heading_idx]["name"].upper()]
                for run in p.runs:
                    if run.text.strip() in ("2", "3", "4"):
                        run.text = str(vnum)
                        break
            heading_idx += 1

    table_calendar_idx = 0
    for table in doc.tables:
        if len(table.rows) > 15:
            current_worker = worker_order[table_calendar_idx % len(worker_order)]
            w_total        = totals_map.get(current_worker, worker_days[0] * wage if worker_days else 0)
            worked_days    = worked_days_map.get(current_worker, [])

            work_ptr = 0
            for row in table.rows:
                cells = row.cells
                if len(cells) > 12 and "08" in cells[1].text:
                    if work_ptr < len(worked_days):
                        cells[0].text  = f"{worked_days[work_ptr]:02d}/{m_idx:02d}/{year}"
                        cells[12].text = str(wage)
                        work_ptr += 1
                    else:
                        cells[0].text  = ""
                        cells[12].text = ""

                elif "TOTAL" in cells[0].text or (
                        len(cells) > 2 and "TOTAL" in cells[2].text):
                    cells[12].text = str(w_total)

            table_calendar_idx += 1

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio
