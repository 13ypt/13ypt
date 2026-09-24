#!/usr/bin/env python3
"""Given museum homepages, list links that look like online collection databases."""
import sys, re, time, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
for u in sys.argv[1:]:
    try:
        r = requests.get(u, headers={"User-Agent": UA, "Accept": "text/html"}, timeout=45)
    except Exception as e:
        print("ERR", u, str(e)[:100]); continue
    s = BeautifulSoup(r.text, 'lxml')
    out = set()
    for a in s.find_all('a'):
        h = a.get('href') or ''
        full = urljoin(r.url, h)
        if re.search(r'(?i)emuseum|collection|catalogaccess|pastperfect|piction|/art/|artwork|objects|search', full) and not re.search(r'(?i)facebook|twitter|instagram|shop\.|store|youtube|linkedin|google', full):
            out.add(full.split('#')[0][:140])
    print(f"== {r.status_code} {u} -> {r.url}")
    for x in sorted(out)[:15]: print('   ', x)
    time.sleep(1)
