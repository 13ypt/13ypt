#!/usr/bin/env python3
"""Query the SMB (Staatliche Museen zu Berlin) digital collection search API used by
https://search.smb.museum (endpoint /api/objects/search-expert, found in the site's JS).

Usage: python3 smb_search.py <q> [org_unit or ''] [field=q|title|objectType|freeText]
Prints: id | titel | objekttyp | sammlung | datierung
Polite: 1 request/s.
"""
import sys
import time
import requests

q = sys.argv[1]
org = sys.argv[2] if len(sys.argv) > 2 else ""
field = sys.argv[3] if len(sys.argv) > 3 else "q"
url = "https://search.smb.museum/api/objects/search-expert"
start, limit, rows, total = 0, 100, [], None
while True:
    params = {field: q, "start": start, "limit": limit, "has_images": "false"}
    if org:
        params["org_units"] = org
    d = requests.get(url, params=params, timeout=90).json()
    arts = d.get("artworks", [])
    total = d.get("total")
    rows += arts
    start += limit
    if not arts or start >= (total or 0):
        break
    time.sleep(1)
print(f"# {field}={q!r} org={org!r} total={total} fetched={len(rows)}", file=sys.stderr)
for a in rows:
    print(f"{a['id']} | {a.get('titel')} | {a.get('objekttyp')} | {a.get('sammlung')} | {a.get('datierungLabel')}")
