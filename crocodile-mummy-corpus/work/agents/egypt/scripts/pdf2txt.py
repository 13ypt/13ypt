#!/usr/bin/env python3
"""Extract text from a PDF with PyMuPDF: pdf2txt.py in.pdf [out.txt]"""
import sys, pymupdf
doc = pymupdf.open(sys.argv[1])
out = "\n".join(f"=== page {i+1} ===\n" + p.get_text() for i, p in enumerate(doc))
if len(sys.argv) > 2:
    open(sys.argv[2], "w", encoding="utf-8").write(out)
else:
    print(out)
