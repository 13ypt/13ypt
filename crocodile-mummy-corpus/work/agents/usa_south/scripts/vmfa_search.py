#!/usr/bin/env python3
"""Search VMFA collection (server-rendered https://www.vmfa.museum/collection/search?q=...). Usage: vmfa_search.py term [maxpages]"""
import sys, re, time, requests
from bs4 import BeautifulSoup
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
term = sys.argv[1]; maxp = int(sys.argv[2]) if len(sys.argv) > 2 else 10
seen = []
for p in range(1, maxp + 1):
    r = requests.get("https://www.vmfa.museum/collection/search", params={"q": term, "page": p}, headers={"User-Agent": UA}, timeout=60)
    s = BeautifulSoup(r.text, 'lxml')
    new = 0
    for a in s.select('a[href*="/artworks/"]'):
        h = a['href']; t = a.get_text(' ', strip=True)
        if h not in [x[0] for x in seen] and t:
            seen.append((h, t[:100])); new += 1
    if p == 1:
        m = re.search(r'([\d,]+)\s+(results|works|artworks)', s.get_text(' ', strip=True), re.I)
        print("TERM", term, "status", r.status_code, "count", m.group(1) if m else '?')
    if not new: break
    time.sleep(1)
for h, t in seen: print(' ', h, '|', t)
