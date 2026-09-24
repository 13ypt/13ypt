#!/usr/bin/env python3
"""Extract text from a PDF (PyMuPDF) and print keyword contexts.
Usage: pdfgrep.py file.pdf [regex] [context_chars]"""
import re, sys, fitz
path = sys.argv[1]
pat = re.compile(sys.argv[2] if len(sys.argv) > 2 else r'(?i)crocod|cocodril|tims[aā]h|تمساح|sobek|suchos', re.I)
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 400
doc = fitz.open(path)
print(f"pages: {doc.page_count}")
for i, page in enumerate(doc, 1):
    t = page.get_text()
    t1 = re.sub(r'\s+', ' ', t)
    for m in pat.finditer(t1):
        print(f"--- p.{i}: ...{t1[max(0,m.start()-ctx):m.end()+ctx]}...")
