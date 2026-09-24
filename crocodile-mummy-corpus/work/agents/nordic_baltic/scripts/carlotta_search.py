#!/usr/bin/env python3
"""Free-text search in a Carlotta instance (Medelhavsmuseet etc.); prints object ids + titles.
Usage: carlotta_search.py <base e.g. https://collections.smvk.se/carlotta-mhm> <term>"""
import sys, re, time, requests, warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
base, term = sys.argv[1], sys.argv[2]
s = requests.Session()
s.headers['User-Agent'] = 'Mozilla/5.0 (research; crocodile mummy corpus)'
s.get(base + '/web/EasySearch', timeout=60)
r = s.post(base + '/web/perform/free_search', data={'FreeSearch_TEXT_OPERAND': '<default>', 'FreeSearch_TEXT_VALUE': term}, timeout=60)
html = r.text
pages = [html]
# follow pagination
seen = set()
while True:
    soup = BeautifulSoup(pages[-1], 'lxml')
    nxt = None
    for a in soup.find_all('a'):
        t = a.get_text(strip=True).lower()
        if t in ('next', 'nästa', '>', 'next page', '»') and a.get('href') and a['href'] not in seen:
            nxt = a['href']; break
    if not nxt: break
    seen.add(nxt)
    time.sleep(1)
    url = nxt if nxt.startswith('http') else 'https://' + base.split('/')[2] + nxt
    pages.append(s.get(url, timeout=60).text)
ids = {}
for p in pages:
    soup = BeautifulSoup(p, 'lxml')
    for a in soup.find_all('a', href=re.compile(r'/web/object/\d+')):
        oid = re.search(r'/web/object/(\d+)', a['href']).group(1)
        txt = a.get_text(' ', strip=True)
        if txt: ids.setdefault(oid, set()).add(txt)
m = re.search(r'(\d+)\s*(hits|träffar|objects|objekt)', BeautifulSoup(pages[0],'lxml').get_text(' '), re.I)
print('STATUS', r.status_code, 'pages', len(pages), 'hitcount-text', m.group(0) if m else None)
for k, v in ids.items():
    print(k, '|', ' / '.join(sorted(v))[:150])
