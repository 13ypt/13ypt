#!/usr/bin/env python3
"""Search ColBase (national museums of Japan) via its public web-frontend API.
Usage: colbase.py <free_word> [limit]"""
import json, sys, urllib.parse, requests
kw = sys.argv[1]; lim = sys.argv[2] if len(sys.argv) > 2 else "100"
url = "https://colbase.nich.go.jp/colbaseapi/v2/collection_items?locale=ja&free_word=" + urllib.parse.quote(kw) + "&limit=" + lim
d = requests.get(url, headers={"x-api-key": "aaa"}, timeout=60).json()
print("URL:", url, "COUNT:", d["resultset"]["count"])
for it in d.get("results", []):
    print("-", it.get("organization_path_name"), it.get("organization_item_key"), "|", it.get("title"), "|", it.get("shutudochi"), "|", it.get("bunrui"), "|", it.get("kizousha"))
if not d.get("results"):
    print(list(d.keys()))
