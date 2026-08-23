"""pandoc 3 writes tables with tblW pct 0 and no tblGrid; LibreOffice then renders zero-width tables. Give every table
100% width, an autofit layout and an equal-width grid; set cell widths to match."""
import re, sys, zipfile, shutil, os
def fix(path):
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                x = data.decode("utf8")
                def fix_tbl(m):
                    t = m.group(0)
                    rows = re.findall(r"<w:tr[ >].*?</w:tr>", t, re.S)
                    ncols = max((len(re.findall(r"<w:tc>", r)) for r in rows), default=1)
                    total = 9360
                    # column widths proportional to text length per column (floor 12%), so narrative columns get room
                    lens = [0.0] * ncols
                    for r in rows:
                        cells = re.findall(r"<w:tc>.*?</w:tc>", r, re.S)
                        for i, c in enumerate(cells[:ncols]):
                            lens[i] += len(re.sub(r"<[^>]+>", "", c))
                    tot = sum(lens) or 1.0
                    shares = [max(0.12, l / tot) for l in lens]; ssum = sum(shares)
                    widths = [int(total * sh / ssum) for sh in shares]
                    t = re.sub(r'<w:tblW[^>]*/>', '<w:tblW w:type="pct" w:w="5000"/>', t, count=1)
                    if "<w:tblLayout" not in t:
                        t = t.replace("</w:tblPr>", '<w:tblLayout w:type="autofit"/></w:tblPr>', 1)
                    grid = "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{wd}"/>' for wd in widths) + "</w:tblGrid>"
                    t = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", "", t, flags=re.S)
                    t = t.replace("</w:tblPr>", "</w:tblPr>" + grid, 1)
                    def fix_row(rm):
                        row = rm.group(0); i = [0]
                        def fix_cell(cm):
                            wd = widths[min(i[0], ncols - 1)]; i[0] += 1
                            return re.sub(r'<w:tcW[^>]*/>', f'<w:tcW w:type="dxa" w:w="{wd}"/>', cm.group(0), count=1)
                        return re.sub(r"<w:tc>.*?</w:tc>", fix_cell, row, flags=re.S)
                    t = re.sub(r"<w:tr[ >].*?</w:tr>", fix_row, t, flags=re.S)
                    return t
                x = re.sub(r"<w:tbl>.*?</w:tbl>", fix_tbl, x, flags=re.S)
                data = x.encode("utf8")
            zout.writestr(item, data)
    shutil.move(tmp, path)
for p in sys.argv[1:]:
    fix(p); print("fixed tables:", os.path.basename(p))
