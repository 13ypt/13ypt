#!/usr/bin/env python3
"""pdf2txt.py in.pdf out.txt : extract text with page markers (PyMuPDF)."""
import sys, pymupdf
doc = pymupdf.open(sys.argv[1])
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    for i, p in enumerate(doc, 1):
        fh.write(f"\n=====PAGE {i}=====\n")
        fh.write(p.get_text())
print(len(doc), "pages")
