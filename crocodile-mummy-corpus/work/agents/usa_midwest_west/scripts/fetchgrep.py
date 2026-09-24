#!/usr/bin/env python3
"""Fetch a URL (browser UA) and print HTTP status, page title and text snippets
around keywords. Used for quick checks of museum collection-search pages.

Usage: python3 fetchgrep.py <url> [regex] [maxhits]
"""
import re
import sys

import requests
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

url = sys.argv[1]
pat = re.compile(sys.argv[2] if len(sys.argv) > 2 else r"crocod|mumm", re.I)
maxhits = int(sys.argv[3]) if len(sys.argv) > 3 else 25
try:
    r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}, timeout=60)
except Exception as e:  # noqa
    print(f"ERROR {url}: {e}")
    sys.exit(0)
s = BeautifulSoup(r.text, "lxml")
title = s.title.get_text(strip=True) if s.title else ""
for x in s(["script", "style", "noscript"]):
    x.decompose()
t = s.get_text(" ", strip=True)
hits = [m for m in re.finditer(r"[^.!?]{0,200}(" + pat.pattern + r")[^.!?]{0,200}", t, re.I)]
print(f"{r.status_code} {r.url} | title={title[:100]!r} | textlen={len(t)} | hits={len(hits)}")
for m in hits[:maxhits]:
    print("  -", m.group(0).strip()[:400])
