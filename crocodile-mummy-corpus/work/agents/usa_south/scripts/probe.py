#!/usr/bin/env python3
"""Fetch URLs and print HTTP status, title, and context around crocodile/mummy/Sobek mentions, plus links matching.
Usage: probe.py URL [URL...]"""
import sys, re, time, requests
from bs4 import BeautifulSoup
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
PAT = re.compile(r'(?i)crocodil|mummif|mummy|mummies|sobek|souchos')
for u in sys.argv[1:]:
    try:
        r = requests.get(u, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-US,en"}, timeout=60, allow_redirects=True)
    except Exception as e:
        print("ERR", u, e); continue
    s = BeautifulSoup(r.text, 'lxml')
    for x in s(['script', 'style', 'noscript']): x.decompose()
    t = s.get_text(' ', strip=True)
    title = s.title.get_text(strip=True) if s.title else ''
    hits = list(PAT.finditer(t))
    print(f"== {r.status_code} {r.url} | {title[:80]} | {len(t)} chars | {len(hits)} hits")
    shown = 0; last = -1000
    for k in hits:
        if k.start() - last < 200: continue
        last = k.start(); shown += 1
        print('   ...', t[max(0, k.start()-150):k.start()+180].replace('\n', ' '))
        if shown >= 10: break
    links = set()
    for a in s.find_all('a'):
        h = a.get('href') or ''; tx = a.get_text(' ', strip=True)
        if PAT.search(tx) or PAT.search(h): links.add((h, tx[:80]))
    for h, tx in list(links)[:25]: print('   L', h, '|', tx)
    time.sleep(1)
