"""
Template structural validation.

The docx engine populates templates by searching for specific anchor
text (e.g. "LABOUR NAME:"), not by filling named placeholders. That
means a wrong or swapped template file (say, ANNEXURE_TEMPLATE.docx
accidentally containing the Labour Annexure's content) doesn't raise
an error — it just silently produces a document with none of the
expected fields filled in. This module lets the UI check a template's
shape *before* generation and fail loudly with a specific, actionable
message instead.
"""
import docx


# Text fragments that MUST appear somewhere in a valid Annexure-1
# (master bill) template. If any are missing, the file is either the
# wrong template entirely (e.g. the Labour Annexure by mistake) or has
# been edited in a way that will break the substring-matching engine.
ANNEX1_ANCHORS = [
    "No. Station Imprest",
    "Sub: Recoupment",
    "BALANCE AMOUNT ON HAND",
    "Certified that the amount paid",
]

# Same idea for the Labour Annexure template.
LABOUR_ANCHORS = [
    "LABOUR NAME:",
    "Payment to Smt",
    "Total amount paid",
]


def _all_text(template_path):
    """Concatenate every paragraph's text (body + tables) into one string
    for a simple substring search."""
    doc = docx.Document(template_path)
    chunks = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                chunks.extend(p.text for p in cell.paragraphs)
    return "\n".join(chunks)


def validate_template(template_path, anchors):
    """
    Check that `template_path` contains every string in `anchors`.

    Returns a list of the anchors that were NOT found (empty list means
    the template is structurally valid). Returns a single-item list
    describing the error if the file can't even be opened as a .docx —
    callers should treat any non-empty return as "do not generate".
    """
    try:
        text = _all_text(template_path)
    except Exception as e:
        return [f"Could not open template as a .docx file: {e}"]

    return [anchor for anchor in anchors if anchor not in text]


def validate_annexure1_template(template_path):
    return validate_template(template_path, ANNEX1_ANCHORS)


def validate_labour_template(template_path):
    return validate_template(template_path, LABOUR_ANCHORS)


def count_labour_template_worker_slots(template_path):
    """
    Return how many worker 'slots' the Labour Annexure template supports
    (i.e. how many 'LABOUR NAME:' blocks it contains). Workers beyond
    this count cannot be placed in the generated document — the caller
    should warn the user before generating rather than silently
    dropping workers. Returns 0 if the template can't be opened.
    """
    try:
        text = _all_text(template_path)
    except Exception:
        return 0
    return text.count("LABOUR NAME:")
