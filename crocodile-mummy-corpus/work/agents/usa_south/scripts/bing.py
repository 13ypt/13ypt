#!/usr/bin/env python3
"""Minimal Bing HTML search for candidate discovery. Usage: bing.py "<query>" [n]"""
import sys, requests, urllib.parse, re, base64, time
from bs4 import BeautifulSoup
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
r = requests.get("https://www.bing.com/search", params={"q": q, "setlang": "en", "cc": "US"}, headers={"User-Agent": UA, "Accept-Language": "en-US,en"}, timeout=60)
s = BeautifulSoup(r.text, 'lxml')
print("Q:", q, "| status", r.status_code)
for li in s.select('li.b_algo')[:n]:
    a = li.select_one('h2 a')
    if not a: continue
    href = a.get('href', '')
    m = re.search(r'[?&]u=a1([^&]+)', href)
    if m:
        try:
            enc = m.group(1); enc += '=' * (-len(enc) % 4)
            href = base64.urlsafe_b64decode(enc).decode('utf-8', 'ignore')
        except Exception:
            pass
    sn = li.select_one('.b_caption p') or li.select_one('p')
    print('-', a.get_text(' ', strip=True)[:110], '|', href)
    if sn: print('    ', sn.get_text(' ', strip=True)[:280])
