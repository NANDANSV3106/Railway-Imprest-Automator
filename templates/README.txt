This folder must contain exactly two files:

  ANNEXURE_TEMPLATE.docx   — the Annexure-1 master imprest bill template
  LABOUR_TEMPLATE.docx     — the Labour Annexure template

IMPORTANT — a real incident that happened during development:
These two files were once uploaded with their names accidentally
swapped (ANNEXURE_TEMPLATE.docx contained the Labour Annexure's
content, and vice versa). Because the docx engine fills templates by
searching for anchor text rather than named placeholders, a swapped
file doesn't raise an error — it just silently generates a document
with none of its fields populated.

The app now checks this automatically: core/validation.py's
validate_annexure1_template() / validate_labour_template() scan each
file for required anchor text (e.g. "No. Station Imprest" for
Annexure-1, "LABOUR NAME:" for Labour) and the Generate tab will
refuse to run and show a specific error if either file is missing its
required anchors — including telling you if it looks like the two
files are swapped.

If you replace either template, keep the anchor text intact:

  ANNEXURE_TEMPLATE.docx must contain:
    "No. Station Imprest", "Sub : Recoupment",
    "BALANCE AMOUNT ON HAND", "Certified that the amount paid"

  LABOUR_TEMPLATE.docx must contain:
    "LABOUR NAME:", "Payment to Smt", "Total amount paid"

Worker slots in LABOUR_TEMPLATE.docx: the template currently supports
2 workers (2 "LABOUR NAME:" blocks). Stations configured with 3 or 4
workers will have the extra worker(s) blocked from generation with a
warning — the UI checks this via
core/validation.py:count_labour_template_worker_slots() before
allowing Generate. To support more workers, duplicate an existing
worker block (LABOUR NAME → calendar table → signature → Payment-to
paragraph → Total-amount-paid paragraph) inside the .docx, keeping the
same anchor text in each new block.
