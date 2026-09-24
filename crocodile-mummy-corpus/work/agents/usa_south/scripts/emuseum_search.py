#!/usr/bin/env python3
"""Page through an eMuseum (Gallery Systems) keyword search and list object links/titles.
Usage: emuseum_search.py <base_url> <term> [maxpages]
e.g. emuseum_search.py https://collections.carlos.emory.edu crocodile"""
import sys, time, re, urllib.parse, requests
from bs4 import BeautifulSoup
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
base, term = sys.argv[1].rstrip('/'), sys.argv[2]
maxpages = int(sys.argv[3]) if len(sys.argv) > 3 else 20
seen = []
sess = requests.Session()
for p in range(1, maxpages + 1):
    url = f"{base}/search/{urllib.parse.quote(term)}/objects/images?page={p}"
    r = sess.get(url, headers={"User-Agent": UA, "Accept": "text/html"}, timeout=60)
    s = BeautifulSoup(r.text, 'lxml')
    if p == 1:
        t = s.get_text(' ', strip=True)
        m = re.search(r'(\d[\d,]*)\s+results', t, re.I)
        print("TERM", term, "status", r.status_code, "count:", m.group(1) if m else '0/none')
    new = 0
    for a in s.select('a[href*="/objects/"]'):
        h = a.get('href').split('?')[0]
        if re.search(r'/objects/\d+', h) and h not in seen:
            seen.append(h); new += 1
    if not new or not any('Next' in a.get_text() for a in s.find_all('a')):
        break
    time.sleep(1)
for h in seen:
    print(' ', h)
