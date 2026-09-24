#!/usr/bin/env python3
"""KHM Wien online collection search (htmx POST endpoint). Usage: khm_search.py <query> [maxpages]"""
import re, sys, time, html, requests
q = sys.argv[1]; maxp = int(sys.argv[2]) if len(sys.argv) > 2 else 5
H = {'User-Agent': 'Mozilla/5.0 (research survey)', 'HX-Request': 'true'}
seen = []
for page in range(1, maxp + 1):
    url = f'https://www.khm.at/kunstwerke/suche?page={page}&tx_theme_objectlist%5Bcontroller%5D=Object&type=686&cHash=11277c9cb58e1eef7193f541418b1370'
    for a in range(3):
        try:
            r = requests.post(url, data={'query': q, 'facet_date_begin': '-5000', 'facet_date_end': '2024'}, headers=H, timeout=60); break
        except Exception as e:
            time.sleep(3); r = None
    if r is None: print('FAILED page', page); break
    links = []
    for m in re.finditer(r'href="(https://www\.khm\.at/kunstwerke/[a-z0-9-]+-(\d+))"', r.text):
        if m.group(1) not in seen and m.group(1) not in links: links.append(m.group(1))
    tot = re.search(r'(\d[\d.]*)\s*(Ergebnisse|Treffer|Objekte)', r.text)
    if page == 1: print('query', q, 'status', r.status_code, 'total', tot.group(0) if tot else '?')
    if not links: break
    seen += links
    time.sleep(1.5)
for l in seen: print(' ', l)
