#!/usr/bin/env python3
"""Europeana Search API (public demo key). usage: europeana.py "query" [COUNTRY ...]"""
import sys, json, requests, urllib.parse
q = sys.argv[1]; countries = sys.argv[2:]
params = [("wskey", "api2demo"), ("query", q), ("rows", "100"), ("profile", "standard")]
for c in countries: params.append(("qf", f"COUNTRY:{c}"))
r = requests.get("https://api.europeana.eu/record/v2/search.json", params=params, timeout=60)
d = r.json()
print("TOTAL", d.get("totalResults"), r.url)
for it in d.get("items", []):
    print(" |", (it.get("title") or [""])[0][:90], "|", (it.get("dataProvider") or [""])[0], "|", (it.get("country") or [""])[0], "|", it.get("guid"))
