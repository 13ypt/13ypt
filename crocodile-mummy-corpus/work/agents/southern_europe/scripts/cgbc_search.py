#!/usr/bin/env python3
"""Search catalogo.beniculturali.it (Catalogo generale dei Beni Culturali, ICCD) HTML search.
usage: cgbc_search.py "query" [key=value filters e.g. typology=Reperti archeologici] ; paginates via &page=
"""
import sys, re, html, time, urllib.parse, requests
q = sys.argv[1]; filt = dict(a.split('=', 1) for a in sys.argv[2:])
seen = []
for page in range(1, 30):
    p = {"query": q, **filt}
    if page > 1: p["startPage"] = (page-1)*12; p["paging"] = "true"
    url = "https://catalogo.beniculturali.it/search?" + urllib.parse.urlencode(p)
    for att in range(4):
        try:
            h = requests.get(url, timeout=60).text; break
        except Exception as e:
            time.sleep(3)
    else:
        print("FAILED", url); break
    if page == 1:
        m = re.search(r'esito ricerca.*?([\d\.]+)\s*(?:&nbsp;|\xa0| )risultati', html.unescape(re.sub(r'<[^>]+>', ' ', h)), re.S)
        print("TOTAL", m.group(1) if m else "?", url)
    hits = re.findall(r'href="(/detail/[^"]+)"[^>]*>(.*?)</a>', h, re.S)
    new = [(u, ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', t)).split())) for u, t in hits if u not in [s[0] for s in seen]]
    if not new: break
    seen += new
    time.sleep(1)
for u, t in seen:
    print("https://catalogo.beniculturali.it" + u, "|", t[:200])
