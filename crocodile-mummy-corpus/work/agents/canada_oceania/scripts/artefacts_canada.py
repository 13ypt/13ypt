#!/usr/bin/env python3
"""Keyword search of Artefacts Canada - Humanities (JSF form POST). ~1 req/s.
Usage: python3 artefacts_canada.py "<term>" [lang]"""
import re, sys, time, requests
from bs4 import BeautifulSoup
URL = "https://app.pch.gc.ca/application/artefacts_hum/indice_index.app"
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0"
term = sys.argv[1]; lang = sys.argv[2] if len(sys.argv) > 2 else "en"
f = "searchform-" + lang
r = S.get(URL, params={"lang": lang}, timeout=60)
s = BeautifulSoup(r.text, "lxml")
vs = s.find("input", {"name": "jakarta.faces.ViewState"})["value"]
btn = [i["name"] for i in s.find_all("input", {"type": "submit"}) if i.get("name", "").startswith(f)][0]
time.sleep(1)
r = S.post(URL + f"?lang={lang}", data={f: f, f + "-term": term, btn: "Search", "jakarta.faces.ViewState": vs}, timeout=60)
print("URL", r.url, r.status_code)
s = BeautifulSoup(r.text, "lxml")
for x in s(["script", "style"]): x.decompose()
t = s.get_text(" | ", strip=True)
i = t.find("result")
print(t[:200]); print("....")
print(t[max(0, i - 300): i + 6000])
