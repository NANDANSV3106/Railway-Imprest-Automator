"""
Annexure-1 (master imprest bill) generation engine.

Populates the ANNEXURE_TEMPLATE.docx by locating specific anchor text
in its paragraphs/tables and replacing/appending runs — see
core/validation.py for the anchor list this template must contain.
"""
import copy
import docx

from config import STATION_DEFAULT
from core.dates import get_days_in_month
from core.num_to_words import amount_in_words
from docx_engine import xml_helpers as xh
from io import BytesIO


def generate_annexure_1(template_path, month, year,
                        op_bal, atm_recoup, cash_total,
                        dev_total, tha_total, tot_exp, cl_bal,
                        sanc_amt, v1_amt, v2_amt, v1_date, v2_date,
                        v1_items=0, v2_items=0, num_vouchers=3,
                        has_stationery=False, station=None):

    if station is None:
        station = STATION_DEFAULT
    stn_name   = station["name"]
    stn_div    = station["division"]
    officer    = station["officer_name"]
    auto_phone = station["auto_phone"]
    mobile     = station["mobile"]
    atm_no     = station.get("atm_no", "")
    workers    = station["workers"]

    doc = docx.Document(template_path)
    days, m_idx = get_days_in_month(month, year)
    s_date   = f"01/{m_idx:02d}/{year}"
    e_date   = f"{days}/{m_idx:02d}/{year}"
    next_m   = 1 if m_idx == 12 else m_idx + 1
    next_y   = int(year) + 1 if m_idx == 12 else year
    next_date = f"01/{next_m:02d}/{next_y}"
    l_total  = dev_total + tha_total

    # ── 1. PARAGRAPH REPLACEMENTS ────────────────────────────
    # The template has TWO separate paragraphs starting with "SMR/" —
    # one near the officer signature block (bold, no trailing period)
    # and one near the document footer (plain, with a trailing period).
    # Both need the station's division substituted in for genericity
    # across stations, but with DIFFERENT formatting each. Track which
    # occurrence we're on positionally, same principle used for the
    # Labour Annexure's worker slots.
    smr_line_idx = 0
    for p in doc.paragraphs:
        txt = p.text

        if "No. Station Imprest" in txt:
            # The original template has no month/year here at all — see
            # docx_engine module notes; this used to inject "{month}
            # {year}" into a spot the real template design never had
            # it, producing a line the reference documents don't match.
            # The month is already carried by the "Sub: Recoupment ...
            # period {s_date} to {e_date}" line elsewhere.
            # Reference documents show this line at explicit 10pt —
            # a plain p.text reassignment leaves it at Word's default
            # instead, so build it with append_run(size=20) (20
            # half-points = 10pt) rather than a bare p.text= assignment.
            xh.clear_para_runs(p)
            xh.append_run(p, " No. Station Imprest /", size=20)
            xh.append_run(
                p,
                "                                                                                                        "
                f"Station: {stn_name}", size=20)

        elif "Date:" in txt and "THROUGH" not in txt and "Dated:" not in txt:
            p.text = ("\t\t\t\t\t\t\t\t\t\t\t  Date:" + e_date)

        elif "Sub : Recoupment" in txt or ("Sub:" in txt and "Recoupment" in txt):
            p.text = f"\t\tSub: Recoupment of imprest bill for the period {s_date} to {e_date}"

        # ── Item 14: Vr. No. line ──
        elif ("14. Vr. No." in txt) or ("Vr. No.01" in txt) or \
             ("14." in txt and "Vr. No." in txt and "Date" in txt):
            xh.clear_para_runs(p)
            xh.append_run(p, "14. ",    bold=False, size=16)
            xh.append_run(p, "Vr. No.", bold=False, size=20)
            xh.append_run(p, "01",      bold=True,  size=20)
            xh.append_run(p, " ",       bold=True,  size=20)
            xh.append_run(p, "Date ",   bold=False, size=20)
            xh.append_run(p, v1_date,   bold=True,  size=20)
            xh.append_run(p, ",",       bold=True,  size=20)
            xh.append_run(p, "Vr. No.", bold=False, size=20)
            xh.append_run(p, "02",      bold=True,  size=20)
            xh.append_run(p, " ",       bold=True,  size=20)
            xh.append_run(p, "Date",    bold=False, size=20)
            xh.append_run(p, f" {v2_date if (v2_amt and v2_date) else e_date}", bold=True, size=20)
            xh.append_run(p, " ,Vr.No ", bold=False, size=20)
            xh.append_run(p, "03",      bold=True,  size=20)
            xh.append_run(p, " Date ",  bold=False, size=20)
            xh.append_run(p, e_date,    bold=True,  size=20)
            if num_vouchers == 4:
                xh.append_run(p, " ,Vr.No ", bold=False, size=20)
                xh.append_run(p, "04",       bold=True,  size=20)
                xh.append_run(p, " Date ",   bold=False, size=20)
                xh.append_run(p, e_date,     bold=True,  size=20)

        # ── "Accepted for Rs. /-(...)" paragraph ──
        elif "Accepted for Rs." in txt and "14." not in txt:
            xh.clear_para_runs(p)
            words = amount_in_words(tot_exp)
            xh.append_run(p, "Accepted for Rs. ", bold=False, size=20)
            xh.append_run(p, f"{tot_exp}/-",      bold=True,  size=20)
            xh.append_run(p, words,               bold=True,  size=20)

        elif "For the month of" in txt:
            p.text = f"For the month of  {month}  {year}"

        elif "Imprest Account Of" in txt:
            # The station name portion is bold + underlined in the
            # original template; the rest of the sentence is plain.
            # A plain p.text = "..." reassignment collapses everything
            # to a single run and loses that distinction, so build the
            # three segments as separate runs instead. The original
            # template also has no month/year in this sentence at all
            # (see the "No. Station Imprest" fix above for the same
            # issue) — don't reintroduce it here. Reference documents
            # show this whole line at explicit 14pt (28 half-points) —
            # bigger than the 10pt used elsewhere in the header block.
            xh.clear_para_runs(p)
            xh.append_run(p, "Imprest Account Of    ", size=28)
            p._p.append(xh.make_run(stn_name, bold=True, underline=True, size=28))
            xh.append_run(p, "    का   अग्रदाय   लेखा   महिन     के   लिए", size=28)

        elif "Controlling Officer" in txt:
            # Bold in the original template — preserve it (see note
            # above; a plain p.text reassignment would silently drop
            # it), and reference documents show this at explicit 10pt.
            xh.clear_para_runs(p)
            xh.append_run(p, f"\tControlling Officer\t\t\t\t\t\t ({officer})", bold=True, size=20)

        elif txt.strip().startswith("SMR/") and len(txt.strip()) < 12:
            xh.clear_para_runs(p)
            if smr_line_idx == 0:
                # First occurrence — bold, no trailing period, 10pt
                # (matches the officer-signature block's original
                # formatting).
                xh.append_run(p, f"\t\t\t\t\t\t\t\t                          {stn_div} ", bold=True, size=20)
            else:
                # Second+ occurrence — plain, with a trailing period
                # (matches the footer line's original formatting; the
                # footer line has no explicit-size mismatch in the
                # reference, so it's left at Word's default here).
                xh.append_run(p, f"                                               {stn_div}.           ", bold=False)
            smr_line_idx += 1

        elif "AUTO PHONE:" in txt:
            xh.clear_para_runs(p)
            xh.append_run(p, f"\t\t\t\t\t\t\t\t              AUTO PHONE: {auto_phone}\t", bold=True, size=20)

        elif "MOBILE NO." in txt:
            xh.clear_para_runs(p)
            xh.append_run(p, f"\t\t\t\t\t\t\t                          MOBILE NO. {mobile}", bold=True, size=20)

    # ── 2. DYNAMIC ROW MANAGEMENT (single template → 3V or 4V) ──────
    # BUG FIXED: this used to compute current_data_rows as
    # len(table.rows) - 1, which only excludes the TOTAL row and
    # forgets the table ALSO has a header row (Sl. No. / Date /
    # Voucher reference / ...). The real template ships with
    # 1 header + 3 data rows (Sl 01/02/03) + 1 TOTAL = 5 rows total,
    # i.e. 3 real data rows — but the old math computed 4, which
    # wrongly triggered the "trim down to 3-voucher mode" branch and
    # deleted the legitimate 3rd voucher row (the second worker's
    # labour voucher). That's why generated Annexure-1 documents were
    # missing a voucher line and the itemized rows didn't sum to the
    # TOTAL cell. Subtracting 2 (header + TOTAL) fixes both directions:
    # 3-voucher mode now correctly leaves all 3 rows alone, and
    # 4-voucher mode correctly detects 3 base rows and adds a 4th.
    for t_idx, table in enumerate(doc.tables):
        if len(table.columns) == 7 and len(table.rows) in (4, 5, 6):
            current_data_rows = len(table.rows) - 2  # exclude header row + TOTAL row
            if num_vouchers == 4 and current_data_rows == 3:
                src_tr = table.rows[3]._tr
                new_tr = copy.deepcopy(src_tr)
                src_tr.addnext(new_tr)
                # BUG FIXED: the clone is an exact copy of row 3 (Sl.No
                # "03"), including its Sl.No and Voucher-reference cell
                # text. Left as-is, BOTH the original and the new row
                # are labeled "03" — the TABLE ENGINE below matches
                # rows by their Sl.No text, so it can't tell them apart:
                # every "sl == 03" check matches twice, the second
                # worker's wage (meant for a genuine "04" row) never
                # gets filled in, and the document shows two identical
                # "03" rows instead of "03" + "04". Relabel the new row
                # to "04" immediately so the table engine can address
                # it independently.
                new_row = table.rows[4]
                new_row.cells[0].text = "04"
                if "Voucher No" in new_row.cells[2].text:
                    new_row.cells[2].text = new_row.cells[2].text.replace("03", "04").replace("- 3", "- 4")
            elif num_vouchers == 3 and current_data_rows == 4:
                tr = table.rows[3]._tr
                tr.getparent().remove(tr)
            break  # only fix first matching table

    # ── 3. TABLE ENGINE ──────────────────────────────────────
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            texts    = [c.text.strip() for c in row.cells]
            full_txt = " ".join(texts)

            # TABLE 0: Balance matrix
            if "Opening Balance" in full_txt and "Now recoupment" in full_txt \
                    and len(row.cells) >= 4:
                row.cells[0].text = f"Opening Balance as on {s_date}"
                xh.set_bold_right_cell(row.cells[1], str(op_bal), size_pt=10)
                row.cells[2].text = f"Now recoupment Bill No. NIL,\nDated: {e_date}"
                xh.set_bold_right_cell(row.cells[3], str(tot_exp), size_pt=10)

            elif "Last recoupment" in full_txt and "Closing" not in full_txt \
                    and len(row.cells) >= 2:
                row.cells[0].text = f"Last recoupment Bill No.NIL Dated {month} {year}"
                xh.set_bold_right_cell(row.cells[1], str(atm_recoup), size_pt=10)

            elif "Closing Balance" in full_txt and len(row.cells) >= 4:
                row.cells[2].text = f"Closing Balance as on {e_date}"
                xh.set_bold_right_cell(row.cells[3], str(cl_bal), size_pt=10)

            elif "Sanctioned Amount" in full_txt and len(row.cells) >= 4:
                xh.set_bold_right_cell(row.cells[1], str(sanc_amt), size_pt=10)
                xh.set_bold_right_cell(row.cells[3], str(sanc_amt), size_pt=10)

            # TABLE 2: 7-column summary — match by Sl.No (works for 3V & 4V)
            elif "09.295" in full_txt and len(row.cells) == 7:
                sl = texts[0]

                # Date cells here start empty in the template (no
                # formatting to inherit) but the reference documents
                # show them bold, matching the Items/Amount cells in
                # the same row — set bold explicitly rather than a
                # plain .text= assignment.
                if sl in ("01", "1"):
                    xh.set_summary_table_cell(row.cells[1], v1_date, bold=True)
                    xh.set_summary_table_cell(row.cells[5], xh.fmt_items(v1_items), bold=True)
                    xh.set_summary_table_cell(row.cells[6], str(v1_amt), bold=True)

                elif sl in ("02", "2"):
                    if num_vouchers == 3:
                        xh.set_summary_table_cell(row.cells[1], e_date, bold=True)
                        xh.set_summary_table_cell(row.cells[6], str(dev_total), bold=True)
                    else:
                        xh.set_summary_table_cell(row.cells[1], v2_date, bold=True)
                        xh.set_summary_table_cell(row.cells[5], xh.fmt_items(v2_items), bold=True)
                        xh.set_summary_table_cell(row.cells[6], str(v2_amt), bold=True)

                elif sl in ("03", "3"):
                    if num_vouchers == 3:
                        xh.set_summary_table_cell(row.cells[1], e_date, bold=True)
                        xh.set_summary_table_cell(row.cells[6], str(tha_total), bold=True)
                    else:
                        xh.set_summary_table_cell(row.cells[1], e_date, bold=True)
                        xh.set_summary_table_cell(row.cells[6], str(dev_total), bold=True)

                elif sl in ("04", "4"):
                    xh.set_summary_table_cell(row.cells[1], e_date, bold=True)
                    xh.set_summary_table_cell(row.cells[6], str(tha_total), bold=True)

                # Set 10pt on all non-amount cells in this data row
                for ci, cell in enumerate(row.cells):
                    if ci not in (5, 6):
                        for para in cell.paragraphs:
                            for run in para.runs:
                                run.font.size = docx.shared.Pt(10)

            elif texts[0] == "TOTAL" and len(row.cells) == 7:
                row.cells[6].text = str(tot_exp)
                xh.format_total_row_cells(row, pt_size=12, sz_val='20')
                xh.right_align_cell(row.cells[6])

            # TABLE 3: G.I. Ledger
            elif "OPENING BALANCE" in full_txt and len(row.cells) >= 6:
                xh.set_plain_cell(row.cells[0], s_date, size_pt=12, align="center")
                # Amount cell starts empty with no formatting to
                # inherit, but the reference documents show it bold —
                # set_bold_right_cell both bolds and right-aligns in
                # one call instead of a plain .text= assignment.
                xh.set_bold_right_cell(row.cells[3], str(op_bal), size_pt=12)

            elif "Amount received through ATM" in full_txt and len(row.cells) >= 4:
                xh.set_bold_right_cell(row.cells[3], str(atm_recoup), size_pt=12)
                if atm_no and len(row.cells) > 4:
                    for ci, cell in enumerate(row.cells):
                        if "ATM" in cell.text and "CARD" in cell.text.upper():
                            cell.text = f"ATM CARD NO: {atm_no}"
                            break

            elif "Consumable Items" in full_txt and len(row.cells) >= 6:
                vno = texts[1]
                if vno in ("1", "01"):
                    xh.set_plain_cell(row.cells[0], v1_date, size_pt=12, align="center")
                    xh.set_ledger_amount_cell(row.cells[5], str(v1_amt))
                elif vno in ("2", "02") and num_vouchers == 4:
                    xh.set_plain_cell(row.cells[0], v2_date, size_pt=12, align="center")
                    xh.set_ledger_amount_cell(row.cells[5], str(v2_amt))

            # TABLE 3 Labour rows — 3V: vouchers 2&3; 4V: vouchers 3&4
            elif "Amount paid to cleaning labour" in full_txt and len(row.cells) >= 6:
                vno = texts[1]
                if num_vouchers == 3:
                    if vno in ("2", "02"):
                        xh.set_plain_cell(row.cells[0], e_date, size_pt=12, align="center")
                        xh.set_ledger_amount_cell(row.cells[5], str(dev_total))
                    elif vno in ("3", "03"):
                        xh.set_plain_cell(row.cells[0], e_date, size_pt=12, align="center")
                        xh.set_ledger_amount_cell(row.cells[5], str(tha_total))
                else:
                    if vno in ("3", "03"):
                        xh.set_plain_cell(row.cells[0], e_date, size_pt=12, align="center")
                        xh.set_ledger_amount_cell(row.cells[5], str(dev_total))
                    elif vno in ("4", "04"):
                        xh.set_plain_cell(row.cells[0], e_date, size_pt=12, align="center")
                        xh.set_ledger_amount_cell(row.cells[5], str(tha_total))

            elif "TOTAL" in full_txt and "OPENING" not in full_txt \
                    and len(row.cells) == 8:
                row.cells[3].text = str(sanc_amt)
                row.cells[5].text = str(tot_exp)
                xh.format_total_row_cells(row, pt_size=14, sz_val='22')
                xh.right_align_cell(row.cells[3])
                xh.right_align_cell(row.cells[5])

            # TABLE 4: Certified section
            elif "BALANCE AMOUNT ON HAND" in full_txt:
                xh.set_cell_run(
                    row.cells[0],
                    f"BALANCE AMOUNT ON HAND AS ON {e_date} IS RS. {cl_bal}/-",
                    size=28, spacing_after="0", spacing_line="240"
                )

            elif "2. Certified that the amount paid" in full_txt:
                cell = row.cells[0]
                para = cell.paragraphs[0]
                xh.clear_para_runs(para)
                xh.set_para_spacing(para, after="0", line="240")
                xh.append_run(para, "2. Certified that the amount paid and voucher accepted for Rs. ",
                            bold=False, size=28)
                xh.append_run(para, f"{tot_exp}/-", bold=True, size=28)

            elif "3. Certified that the amount on hand" in full_txt:
                cell = row.cells[0]
                para = cell.paragraphs[0]
                xh.clear_para_runs(para)
                xh.set_para_spacing(para, after="0", line="240")
                xh.append_run(para, f"3. Certified that the amount on hand as on {next_date} is Rs. ",
                            bold=False, size=28)
                xh.append_run(para, f"{cl_bal}/-", bold=True, size=28)

    # ── TABLE 4 — words rows (rows 3 and 5) ─────────────────
    if len(doc.tables) >= 5:
        t4 = doc.tables[4]
        if len(t4.rows) > 5:
            xh.set_cell_run(
                t4.rows[3].cells[0],
                amount_in_words(tot_exp),
                size=28, bold=True, spacing_after="0", spacing_line="240"
            )
            xh.set_cell_run(
                t4.rows[5].cells[0],
                amount_in_words(cl_bal),
                size=28, bold=True, spacing_after="0", spacing_line="240"
            )

    # ── 3. NESTED ALLOCATION TABLE ───────────────────────────
    if len(doc.tables) > 1:
        alloc_wrapper = doc.tables[1]
        if alloc_wrapper.rows and alloc_wrapper.rows[0].cells:
            cell = alloc_wrapper.rows[0].cells[0]
            if cell.tables:
                nested = cell.tables[0]
                for row in nested.rows:
                    texts    = [c.text.strip() for c in row.cells]
                    full_txt = " ".join(texts)
                    if texts[0] in ("01", "1") and "09.295" in full_txt:
                        xh.set_alloc_amount_cell(row.cells[2], str(cash_total))
                        if has_stationery:
                            row.cells[4].text = "Consumable items bills & Stationery item bills"
                        else:
                            row.cells[4].text = "Consumable items bills"
                    elif texts[0] in ("02", "2") and "09.295" in full_txt:
                        xh.set_alloc_amount_cell(row.cells[2], str(l_total))
                        row.cells[4].text = "Cleaning labour bills"

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio


# ─────────────────────────────────────────────────────────────
# ANNEXURE 2  ENGINE
# ─────────────────────────────────────────────────────────────

