#!/usr/bin/env python3
"""Make a labelled contact sheet PNG from images (PyMuPDF). Usage: montage.py out.png cols img1 img2 ..."""
import sys, pymupdf
out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
W, H, pad = 400, 300, 18
rows = (len(files) + cols - 1) // cols
doc = pymupdf.open(); page = doc.new_page(width=cols * W, height=rows * (H + pad))
for k, f in enumerate(files):
    r, c = divmod(k, cols)
    rect = pymupdf.Rect(c * W + 4, r * (H + pad) + pad, (c + 1) * W - 4, (r + 1) * (H + pad))
    try:
        page.insert_image(rect, filename=f, keep_proportion=True)
    except Exception as e:
        page.insert_text((c * W + 10, r * (H + pad) + 60), f"ERR {e}")
    page.insert_text((c * W + 6, r * (H + pad) + 13), f.split('/')[-1][:60], fontsize=11)
page.get_pixmap(dpi=72).save(out)
print(out)
