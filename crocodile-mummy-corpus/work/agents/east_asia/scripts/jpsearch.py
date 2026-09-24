#!/usr/bin/env python3
"""Query Japan Search cross-search API and print compact hit list.
Usage: jpsearch.py "<keyword>" [size] [extra query params]"""
import json, sys, time, urllib.parse, requests
kw = sys.argv[1]
size = int(sys.argv[2]) if len(sys.argv) > 2 else 100
extra = sys.argv[3] if len(sys.argv) > 3 else ""
url = "https://jpsearch.go.jp/api/item/search/jps-cross?keyword=" + urllib.parse.quote(kw) + f"&size={size}" + extra
r = requests.get(url, timeout=60)
d = r.json()
print("URL:", url)
print("HIT:", d.get("hit"))
for f in d.get("facets", []):
    if f["key"] in ("db", "cm"):
        print("FACET", f["key"], f["counts"])
for it in d.get("list", []):
    c = it.get("common", {})
    print("-", c.get("database"), "|", c.get("title"), "|", c.get("ownerOrg"), "|", c.get("linkUrl"), "|", it.get("id"))
