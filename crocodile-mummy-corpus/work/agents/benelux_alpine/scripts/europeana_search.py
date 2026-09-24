#!/usr/bin/env python3
"""Europeana search helper: europeana_search.py '<query>' [qf ...]  (prints id | title | provider)."""
import sys, json, time, urllib.parse, subprocess
q = sys.argv[1]
params = [("wskey", "api2demo"), ("query", q), ("rows", "100"), ("profile", "standard")]
for qf in sys.argv[2:]:
    params.append(("qf", qf))
url = "https://api.europeana.eu/record/v2/search.json?" + urllib.parse.urlencode(params)
out = subprocess.run(["curl", "-sS", url], capture_output=True, text=True).stdout
d = json.loads(out)
print("total", d.get("totalResults"), d.get("error", ""))
for it in d.get("items", []):
    print(it.get("id"), "|", (it.get("title") or [""])[0][:90], "|", (it.get("dataProvider") or [""])[0][:50], "|", (it.get("country") or [""])[0])
time.sleep(1)
