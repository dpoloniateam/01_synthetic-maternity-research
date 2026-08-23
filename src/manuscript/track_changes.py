"""
track_changes.py — minimal helper to inject Word tracked-change *insertions* into a .docx.

python-docx has no native support for revision markup, so we build the OOXML `w:ins`
elements directly. Every paragraph/run added through this helper appears in Word as a
tracked insertion attributed to the given author, so the recipient can Accept/Reject each.

Only insertions are needed for the Paper 1 revision (we add content; we do not delete the
author's prose). Where a paragraph mark itself is inserted, we also mark it via w:pPr/w:rPr/w:ins
so Word treats the whole new paragraph as inserted.
"""
from __future__ import annotations
import copy
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


class TrackedEditor:
    def __init__(self, path, author="Claude", date="2026-06-02T00:00:00Z"):
        self.path = path
        self.author = author
        self.date = date
        self.doc = Document(path)
        self._id = 1000

    # -- helpers -----------------------------------------------------------
    def _next_id(self):
        self._id += 1
        return str(self._id)

    def _ins_attrs(self, el):
        el.set(qn("w:id"), self._next_id())
        el.set(qn("w:author"), self.author)
        el.set(qn("w:date"), self.date)
        return el

    def _run(self, text, bold=False, italic=False):
        r = OxmlElement("w:r")
        if bold or italic:
            rpr = OxmlElement("w:rPr")
            if bold:
                rpr.append(OxmlElement("w:b"))
            if italic:
                rpr.append(OxmlElement("w:i"))
            r.append(rpr)
        t = OxmlElement("w:t")
        t.set(qn("xml:space"), "preserve")
        t.text = text
        r.append(t)
        return r

    def _ins_wrap(self, *runs):
        ins = self._ins_attrs(OxmlElement("w:ins"))
        for r in runs:
            ins.append(r)
        return ins

    def _tracked_paragraph(self, segments, style=None):
        """segments: list of (text, bold, italic). Returns a <w:p> fully marked inserted."""
        p = OxmlElement("w:p")
        ppr = OxmlElement("w:pPr")
        if style:
            ps = OxmlElement("w:pStyle")
            ps.set(qn("w:val"), style)
            ppr.append(ps)
        rpr = OxmlElement("w:rPr")
        rpr.append(self._ins_attrs(OxmlElement("w:ins")))  # mark paragraph mark inserted
        ppr.append(rpr)
        p.append(ppr)
        runs = [self._run(t, b, i) for (t, b, i) in segments]
        p.append(self._ins_wrap(*runs))
        return p

    # -- public API --------------------------------------------------------
    def find(self, needle):
        for para in self.doc.paragraphs:
            if needle.lower() in para.text.strip().lower():
                return para
        raise ValueError(f"anchor not found: {needle!r}")

    def insert_after(self, anchor_para, segments, style=None):
        """Insert one tracked paragraph after anchor_para. `segments` is a list of
        (text, bold, italic) tuples (single string allowed). Returns the new paragraph element."""
        if isinstance(segments, str):
            segments = [(segments, False, False)]
        new_p = self._tracked_paragraph(segments, style=style)
        anchor_para._p.addnext(new_p)
        return new_p

    def insert_block_after(self, anchor_needle, paragraphs):
        """Insert several tracked paragraphs (in order) after the anchor paragraph found by text.
        `paragraphs` is a list where each item is either a string or a list of (text,bold,italic).
        Returns the last inserted <w:p> element so a table can be chained after it."""
        anchor = self.find(anchor_needle)
        prev = anchor._p
        for seg in paragraphs:
            segs = [(seg, False, False)] if isinstance(seg, str) else seg
            new_p = self._tracked_paragraph(segs)
            prev.addnext(new_p)
            prev = new_p
        return prev

    def insert_block_before(self, anchor_needle, paragraphs):
        """Insert several tracked paragraphs (in order) immediately before the anchor paragraph."""
        anchor = self.find(anchor_needle)
        ref = anchor._p
        # build then insert in order so they end up directly above the anchor
        new_ps = []
        for seg in paragraphs:
            segs = [(seg, False, False)] if isinstance(seg, str) else seg
            new_ps.append(self._tracked_paragraph(segs))
        for p in new_ps:
            ref.addprevious(p)
        return new_ps[-1] if new_ps else None

    def insert_table_after_element(self, prev_element, headers, rows, style="Table Grid"):
        """Insert a tracked table immediately after a given XML element (e.g. a paragraph
        returned by insert_block_after). Each cell's run is wrapped in w:ins."""
        tbl = self._build_table(headers, rows, style)
        prev_element.addnext(tbl)

    def insert_table_after(self, anchor_needle, headers, rows, style="Table Grid"):
        """Insert a tracked table after the anchor paragraph found by text."""
        anchor = self.find(anchor_needle)
        anchor._p.addnext(self._build_table(headers, rows, style))

    def _build_table(self, headers, rows, style="Table Grid"):
        tbl = OxmlElement("w:tbl")
        tblpr = OxmlElement("w:tblPr")
        st = OxmlElement("w:tblStyle"); st.set(qn("w:val"), style); tblpr.append(st)
        w = OxmlElement("w:tblW"); w.set(qn("w:w"), "0"); w.set(qn("w:type"), "auto"); tblpr.append(w)
        # basic borders
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{edge}")
            e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4")
            e.set(qn("w:space"), "0"); e.set(qn("w:color"), "auto")
            borders.append(e)
        tblpr.append(borders)
        tbl.append(tblpr)
        grid = OxmlElement("w:tblGrid")
        for _ in headers:
            grid.append(OxmlElement("w:gridCol"))
        tbl.append(grid)
        for cells, is_header in [(headers, True)] + [(r, False) for r in rows]:
            tr = OxmlElement("w:tr")
            for cell in cells:
                tc = OxmlElement("w:tc")
                tcpr = OxmlElement("w:tcPr")
                cw = OxmlElement("w:tcW"); cw.set(qn("w:w"), "0"); cw.set(qn("w:type"), "auto")
                tcpr.append(cw); tc.append(tcpr)
                p = OxmlElement("w:p")
                ppr = OxmlElement("w:pPr")
                rpr = OxmlElement("w:rPr")
                rpr.append(self._ins_attrs(OxmlElement("w:ins")))
                ppr.append(rpr); p.append(ppr)
                p.append(self._ins_wrap(self._run(str(cell), bold=is_header)))
                tc.append(p)
                tr.append(tc)
            tbl.append(tr)
        return tbl

    def save(self, path=None):
        self.doc.save(path or self.path)
