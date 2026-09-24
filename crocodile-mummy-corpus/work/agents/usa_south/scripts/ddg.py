#!/usr/bin/env python3
"""Minimal DuckDuckGo HTML search (candidate discovery only). Usage: ddg.py "<query>" [n]"""
import sys, requests, urllib.parse, re
from bs4 import BeautifulSoup
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
r = requests.post("https://html.duckduckgo.com/html/", data={"q": q}, headers={"User-Agent": UA}, timeout=60)
s = BeautifulSoup(r.text, 'lxml')
print("Q:", q, "status", r.status_code)
res = s.select('.result')
for x in res[:n]:
    a = x.select_one('a.result__a'); sn = x.select_one('.result__snippet')
    if not a: continue
    href = a.get('href')
    m = re.search(r'uddg=([^&]+)', href or '')
    if m: href = urllib.parse.unquote(m.group(1))
    print('-', a.get_text(' ', strip=True)[:120], '|', href)
    if sn: print('   ', sn.get_text(' ', strip=True)[:300])
