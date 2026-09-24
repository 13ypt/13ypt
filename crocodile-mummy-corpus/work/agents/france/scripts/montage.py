#!/usr/bin/env python3
"""montage.py out.png cols cellw cellh img1 [img2 ...]  - labelled contact sheet via pymupdf (for visual checks only)"""
import sys, os, pymupdf
out, cols, cw, ch = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
imgs = sys.argv[5:]
rows = (len(imgs) + cols - 1) // cols
doc = pymupdf.open(); page = doc.new_page(width=cols * cw, height=rows * (ch + 14))
for i, f in enumerate(imgs):
    x, y = (i % cols) * cw, (i // cols) * (ch + 14)
    try: page.insert_image(pymupdf.Rect(x + 2, y + 14, x + cw - 2, y + ch + 12), filename=f, keep_proportion=True)
    except Exception as e: pass
    page.insert_text((x + 3, y + 11), os.path.basename(f)[:40], fontsize=9)
page.get_pixmap(dpi=72).save(out)
