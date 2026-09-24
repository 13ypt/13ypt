#!/usr/bin/env python3
"""Fetch KHM (Kunsthistorisches Museum Wien) object pages /kunstwerke/<id> (following
redirects) and print lines with inventory number, dating, material, dimensions,
acquisition, rights. Usage: python3 khm_extract.py ID [ID ...]"""
import re, sys, time, json, os
import requests
from bs4 import BeautifulSoup
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
out = {}
for oid in sys.argv[1:]:
    url = f"https://www.khm.at/kunstwerke/{oid}"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}, timeout=120)
    except Exception as exc:
        print("FAIL", oid, exc); continue
    s = BeautifulSoup(r.text, "lxml")
    for t in s(["script", "style"]): t.decompose()
    L = [re.sub(r"\s+", " ", l).strip() for l in s.get_text("\n").split("\n")]
    L = [l for l in L if l]
    h1 = s.find("h1")
    keep = [l for l in L if re.search(r"Inv|INV|ÄS|Krokod|Mumie|Tiermumie| cm|erworben|Fundort|Datierung|Jh\.|Chr\.|Material|Maße|Rechte|Lizenz|CC |Creative|Bildrecht|©", l)]
    out[oid] = {"url": r.url, "status": r.status_code, "h1": h1.get_text(" ", strip=True) if h1 else None, "lines": keep[:40],
                "images": sorted(set(re.findall(r'https?://[^"\s]+?\.jpg', r.text)))[:6]}
    print(json.dumps(out[oid], ensure_ascii=False, indent=0))
    time.sleep(1)
p = os.path.join(RAW, "khm_pages.json")
old = json.load(open(p)) if os.path.exists(p) else {}
old.update(out); json.dump(old, open(p, "w"), ensure_ascii=False, indent=1)
