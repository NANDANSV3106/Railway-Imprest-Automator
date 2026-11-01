"""
Low-level OOXML helpers. python-docx doesn't expose paragraph-mark
formatting or some run-level attributes directly, so these build/edit
the underlying <w:r>/<w:pPr> elements by hand.
"""
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def make_run(text, bold=False, size=None, underline=False,
             font_ascii="Calibri", color=None):
    """Build a <w:r> element with optional formatting."""
    r = OxmlElement('w:r')
    rpr = OxmlElement('w:rPr')
    if bold:
        rpr.append(OxmlElement('w:b'))
        rpr.append(OxmlElement('w:bCs'))
    if font_ascii:
        rf = OxmlElement('w:rFonts')
        rf.set(qn('w:ascii'), font_ascii)
        rf.set(qn('w:hAnsi'), font_ascii)
        rf.set(qn('w:cs'), font_ascii)
        rpr.append(rf)
    if color:
        c = OxmlElement('w:color')
        c.set(qn('w:val'), color)
        rpr.append(c)
    if size:
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(size))
        rpr.append(sz)
        szcs = OxmlElement('w:szCs')
        szcs.set(qn('w:val'), str(size))
        rpr.append(szcs)
    if underline:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rpr.append(u)
    r.append(rpr)

    # Tab characters ('\t') embedded in `text` are converted to real
    # OOXML <w:tab/> elements instead of being left as literal tab
    # characters inside <w:t>. This used to only set
    # xml:space="preserve" when the text STARTED or ENDED with a plain
    # space — never for tabs, and never for tabs buried in the middle
    # of the string. Without that attribute, Word's XML whitespace
    # handling strips leading/trailing tabs and can collapse runs of
    # consecutive tabs, so paragraphs built like
    # "\tControlling Officer\t\t\t\t\t\t (NAME)" rendered with the
    # tabs silently gone — "(NAME)" ended up sitting right next to
    # "Controlling Officer" instead of jumping to the intended column
    # on the right of the page, and other tab-prefixed lines (AUTO
    # PHONE, MOBILE NO.) collapsed all the way to the left margin.
    # <w:tab/> is an unambiguous, dedicated element Word always
    # interprets as "advance to the next tab stop" — it sidesteps the
    # whitespace-preservation issue entirely rather than trying to set
    # xml:space correctly for every case.
    segments = text.split('\t')
    for i, segment in enumerate(segments):
        if segment:
            t = OxmlElement('w:t')
            t.text = segment
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            r.append(t)
        if i < len(segments) - 1:
            r.append(OxmlElement('w:tab'))
    return r


def append_run(para, text, bold=False, size=None, font_ascii=None):
    """Append a <w:r> run directly to a paragraph element."""
    para._p.append(make_run(text, bold=bold, size=size, font_ascii=font_ascii))


def clear_para_runs(para):
    """Remove all <w:r> children from a paragraph."""
    for r_elem in para._p.findall(qn('w:r')):
        para._p.remove(r_elem)


def set_para_spacing(para, after="0", line="240", line_rule="auto"):
    """Add/replace <w:spacing> inside <w:pPr>."""
    ppr = para._p.find(qn('w:pPr'))
    if ppr is None:
        ppr = OxmlElement('w:pPr')
        para._p.insert(0, ppr)
    sp = ppr.find(qn('w:spacing'))
    if sp is None:
        sp = OxmlElement('w:spacing')
        ppr.append(sp)
    sp.set(qn('w:after'), after)
    sp.set(qn('w:line'), line)
    sp.set(qn('w:lineRule'), line_rule)


def set_para_mark_bold_size(para, size_val, bold=True):
    """Set bold and font size on the paragraph mark (pPr → rPr)."""
    ppr = para._p.find(qn('w:pPr'))
    if ppr is None:
        ppr = OxmlElement('w:pPr')
        para._p.insert(0, ppr)
    rpr = ppr.find(qn('w:rPr'))
    if rpr is None:
        rpr = OxmlElement('w:rPr')
        ppr.append(rpr)
    b_elem = rpr.find(qn('w:b'))
    if bold and b_elem is None:
        rpr.append(OxmlElement('w:b'))
    elif not bold and b_elem is not None:
        rpr.remove(b_elem)
    sz = rpr.find(qn('w:sz'))
    if sz is None:
        sz = OxmlElement('w:sz')
        rpr.append(sz)
    sz.set(qn('w:val'), str(size_val))


def set_cell_run(cell, text, bold=False, size=None, spacing_after="0",
                  spacing_line="240", font_ascii="Calibri", color="000000"):
    """
    Replace cell content with a single run.
    Applies spacing and font size to both pPr and the run itself
    (matching the exact XML pattern of the correct template).
    """
    para = cell.paragraphs[0]
    clear_para_runs(para)
    set_para_spacing(para, after=spacing_after, line=spacing_line)

    ppr = para._p.find(qn('w:pPr'))
    ppr_rpr = ppr.find(qn('w:rPr'))
    if ppr_rpr is None:
        ppr_rpr = OxmlElement('w:rPr')
        ppr.append(ppr_rpr)
    for child in list(ppr_rpr):
        ppr_rpr.remove(child)
    if font_ascii:
        rf = OxmlElement('w:rFonts')
        rf.set(qn('w:ascii'), font_ascii)
        rf.set(qn('w:eastAsia'), 'Times New Roman')
        rf.set(qn('w:hAnsi'), font_ascii)
        rf.set(qn('w:cs'), font_ascii)
        ppr_rpr.append(rf)
    if color:
        c = OxmlElement('w:color'); c.set(qn('w:val'), color); ppr_rpr.append(c)
    if size:
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(size)); ppr_rpr.append(sz)
        szcs = OxmlElement('w:szCs'); szcs.set(qn('w:val'), str(size)); ppr_rpr.append(szcs)

    run = make_run(text, bold=bold, size=size, font_ascii=font_ascii, color=color)
    para._p.append(run)


def set_alloc_amount_cell(cell, text):
    """
    Set allocation-table amount cell: font 9pt (sz=18), right-aligned.
    """
    para = cell.paragraphs[0]
    clear_para_runs(para)
    ppr = para._p.find(qn('w:pPr'))
    if ppr is None:
        ppr = OxmlElement('w:pPr')
        para._p.insert(0, ppr)
    jc = ppr.find(qn('w:jc'))
    if jc is None:
        jc = OxmlElement('w:jc')
        ppr.append(jc)
    jc.set(qn('w:val'), 'right')
    run = make_run(text, size=18, font_ascii=None)
    para._p.append(run)


def right_align_cell(cell):
    """Add right-alignment to every paragraph of a cell."""
    for para in cell.paragraphs:
        ppr = para._p.find(qn('w:pPr'))
        if ppr is None:
            ppr = OxmlElement('w:pPr')
            para._p.insert(0, ppr)
        jc = ppr.find(qn('w:jc'))
        if jc is None:
            jc = OxmlElement('w:jc')
            ppr.append(jc)
        jc.set(qn('w:val'), 'right')


def set_bold_right_cell(cell, text, size_pt=None):
    """Set cell text, make all runs in the first paragraph bold, then
    right-align. Pass size_pt (e.g. 10 or 12) to also force an explicit
    font size — cells that start empty in the template have no
    existing run to inherit a size from, so leaving size_pt unset can
    silently fall back to Word's own default instead of matching the
    surrounding table's font size."""
    cell.text = text
    for run in cell.paragraphs[0].runs:
        run.bold = True
        if size_pt is not None:
            run.font.size = docx.shared.Pt(size_pt)
    right_align_cell(cell)


def set_plain_cell(cell, text, size_pt=None, bold=False, align=None):
    """Set cell text with an explicit font size (and optional bold),
    for simple cells that start empty in the template and would
    otherwise fall back to Word's default size instead of matching the
    surrounding table. Pass align="center" (or "right") to also force
    paragraph alignment — cells that start empty have no formatting to
    inherit here either, so a caller that needs centered dates (e.g.
    the Page 2 ledger table) must set it explicitly or it silently
    falls back to left alignment instead of matching the reference."""
    cell.text = text
    for run in cell.paragraphs[0].runs:
        run.bold = bold
        if size_pt is not None:
            run.font.size = docx.shared.Pt(size_pt)
    if align is not None:
        para = cell.paragraphs[0]
        ppr = para._p.find(qn('w:pPr'))
        if ppr is None:
            ppr = OxmlElement('w:pPr')
            para._p.insert(0, ppr)
        jc = ppr.find(qn('w:jc'))
        if jc is None:
            jc = OxmlElement('w:jc')
            ppr.append(jc)
        jc.set(qn('w:val'), align)


def format_total_row_cells(row, pt_size, sz_val):
    """Apply bold + font size to all paragraphs/runs in every cell of a TOTAL row."""
    for cell in row.cells:
        for para in cell.paragraphs:
            for run in para.runs:
                run.bold = True
                run.font.size = docx.shared.Pt(pt_size)
            set_para_mark_bold_size(para, sz_val, bold=True)


def set_summary_table_cell(cell, val, bold=True):
    """Write text into a Table-2 summary cell at 10pt (sz=20), right-aligned."""
    cell.text = val
    for para in cell.paragraphs:
        for run in para.runs:
            run.bold = bold
            run.font.size = docx.shared.Pt(10)
        ppr = para._p.find(qn('w:pPr'))
        if ppr is None:
            ppr = OxmlElement('w:pPr'); para._p.insert(0, ppr)
        jc = ppr.find(qn('w:jc'))
        if jc is None:
            jc = OxmlElement('w:jc'); ppr.append(jc)
        jc.set(qn('w:val'), 'right')
        set_para_mark_bold_size(para, '20', bold=bold)


def set_ledger_amount_cell(cell, val):
    """Write a TABLE 3 ledger amount cell: 12pt bold, right-aligned."""
    cell.text = val
    for para in cell.paragraphs:
        for run in para.runs:
            run.bold = True
            run.font.size = docx.shared.Pt(12)
        ppr = para._p.find(qn('w:pPr'))
        if ppr is None:
            ppr = OxmlElement('w:pPr'); para._p.insert(0, ppr)
        jc = ppr.find(qn('w:jc'))
        if jc is None:
            jc = OxmlElement('w:jc'); ppr.append(jc)
        jc.set(qn('w:val'), 'right')
        set_para_mark_bold_size(para, '24', bold=True)


def fmt_items(n):
    """Format item count: single digit gets zero-padded to 2 chars."""
    return f"{int(n):02d}" if n else ""


def iter_all_paragraphs(doc):
    """Yield every paragraph in the document, including those inside table cells."""
    for p in doc.paragraphs:
        yield p
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p
