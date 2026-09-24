#!/usr/bin/env python3
"""Fetch URL(s) politely and print HTTP status, title, and keyword contexts.
Usage: pagegrep.py REGEX URL [URL ...]"""
import re, sys, time, requests
from bs4 import BeautifulSoup
pat = re.compile(sys.argv[1], re.I)
for url in sys.argv[2:]:
    try:
        r = requests.get(url, timeout=45, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'})
    except Exception as e:
        print(f"### {url} ERROR {type(e).__name__}: {str(e)[:120]}"); continue
    s = BeautifulSoup(r.content, 'lxml')
    for tag in s(['script', 'style', 'noscript']): tag.decompose()
    t = re.sub(r'\s+', ' ', s.get_text(' ', strip=True))
    title = s.title.get_text(strip=True) if s.title else ''
    hits = list(pat.finditer(t))
    print(f"### {url} -> {r.status_code} len={len(t)} title={title[:80]!r} hits={len(hits)}")
    last = -1000
    for m in hits[:12]:
        if m.start() - last < 250: continue
        last = m.start()
        print('   ..', t[max(0, m.start()-220):m.end()+220])
    time.sleep(1)
