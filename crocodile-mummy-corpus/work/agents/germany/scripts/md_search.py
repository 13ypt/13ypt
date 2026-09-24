#!/usr/bin/env python3
"""Page through museum-digital (global) JSON object search and print all hits.

Usage: python3 md_search.py <query> [instance]   (instance default: global)
Prints: objekt_id | name | inventory | institution
Polite: 1 request/s.
"""
import json
import sys
import time
import urllib.parse
import requests

q = sys.argv[1]
inst = sys.argv[2] if len(sys.argv) > 2 else "global"
base = f"https://{inst}.museum-digital.org/json/objects"
start = 0
seen = 0
total = None
rows = []
while True:
    url = f"{base}?s={urllib.parse.quote(q)}&startwert={start}"
    r = requests.get(url, timeout=60)
    try:
        d = r.json()
    except Exception:
        print("non-json", r.status_code, r.text[:200], file=sys.stderr)
        break
    if isinstance(d, dict):
        print("msg:", d, file=sys.stderr)
        break
    if not d:
        break
    for x in d:
        total = x.get("total", total)
        rows.append(x)
    start += len(d)
    if total is not None and start >= int(total):
        break
    time.sleep(1)
print(f"# query={q!r} instance={inst} total={total} fetched={len(rows)}", file=sys.stderr)
for x in rows:
    print(f"{x['objekt_id']} | {x['objekt_name']} | {x.get('objekt_inventarnr')} | {x['institution_name']}")
