#!/usr/bin/env python3
"""Extract text from a PDF with PyMuPDF. Usage: pdf2txt.py in.pdf out.txt"""
import sys, pymupdf
doc = pymupdf.open(sys.argv[1])
with open(sys.argv[2], "w") as f:
    for i, p in enumerate(doc, 1):
        f.write(f"\n=== PAGE {i} ===\n" + p.get_text())
print(len(doc), "pages")
