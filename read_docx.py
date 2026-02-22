import docx

doc = docx.Document("docs/Repository/Paper Designing Sharper User Research_v0.docx")
with open("temp_paper.txt", "w", encoding="utf-8") as f:
    for i, p in enumerate(doc.paragraphs):
        f.write(f"[{i}] {p.text}\n")
