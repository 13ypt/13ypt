#!/usr/bin/env python3
"""Fetch institution homepages and list links that look like online-collection entry points.

Usage: python3 findcoll.py <url> [<url> ...]
"""
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
PAT = re.compile(r"collection|emuseum|search|catalog|database|pastperfect|explore|objects|egypt|mumm", re.I)

for url in sys.argv[1:]:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=45)
    except Exception as e:  # noqa
        print(f"== {url} ERROR {str(e)[:120]}")
        continue
    s = BeautifulSoup(r.text, "lxml")
    links = set()
    for a in s.find_all("a", href=True):
        h = a["href"]
        txt = a.get_text(" ", strip=True)
        if PAT.search(h) or PAT.search(txt):
            links.add((txt[:40], requests.compat.urljoin(r.url, h)))
    print(f"== {url} -> {r.status_code} {r.url} ({len(links)} links)")
    for t, h in sorted(links, key=lambda x: x[1])[:40]:
        print(f"   {t!r} {h}")
    time.sleep(1)
