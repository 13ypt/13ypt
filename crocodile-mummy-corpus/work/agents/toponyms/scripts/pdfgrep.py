#!/usr/bin/env python3
"""pdfgrep.py file.pdf regex [context_chars] - extract text with pymupdf and print regex matches with context."""
import sys, re
import pymupdf
doc = pymupdf.open(sys.argv[1])
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 250
text = "\n".join(f"[p{i+1}] " + p.get_text() for i, p in enumerate(doc))
text = re.sub(r"[ \t]+", " ", text)
if sys.argv[2] == "--dump":
    print(text)
    sys.exit()
seen = set()
for m in re.finditer(sys.argv[2], text, re.I):
    s = max(0, m.start() - ctx)
    if any(abs(s - x) < ctx for x in seen):
        continue
    seen.add(s)
    pg = text.rfind("[p", 0, m.start())
    print("---", text[pg:pg+5], text[s:m.end() + ctx].replace("\n", " "))
