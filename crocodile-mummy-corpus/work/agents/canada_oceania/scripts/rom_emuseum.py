#!/usr/bin/env python3
"""Query the ROM eMuseum (collections.rom.on.ca) for crocodile mummies.

JSON export is disabled on this eMuseum instance, so result pages and object
pages are parsed from HTML. Requests are throttled to ~1/s.
Usage: python3 rom_emuseum.py search <term> [<term> ...]
       python3 rom_emuseum.py object <id> [<id> ...]
"""
import re
import sys
import time
import json
import requests
from bs4 import BeautifulSoup

BASE = "https://collections.rom.on.ca"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
S = requests.Session()
S.headers["User-Agent"] = UA


def get(url):
    time.sleep(1.0)
    r = S.get(url, timeout=60)
    r.raise_for_status()
    return r.text


def search(term):
    out = {}
    page = 1
    total = None
    while True:
        url = f"{BASE}/search/{requests.utils.quote(term)}/objects/list?page={page}"
        h = get(url)
        s = BeautifulSoup(h, "lxml")
        if total is None:
            m = re.search(r"of ([\d,]+) results", s.get_text(" ", strip=True))
            total = int(m.group(1).replace(",", "")) if m else 0
        n_before = len(out)
        for a in s.find_all("a", href=True):
            m = re.match(r"/objects/(\d+)/", a["href"])
            if m:
                t = a.get_text(" ", strip=True)
                if t:
                    out.setdefault(m.group(1), t)
        if len(out) == n_before or len(out) >= total:
            break
        page += 1
    return total, out


def obj(oid):
    url = f"{BASE}/objects/{oid}"
    h = get(url)
    s = BeautifulSoup(h, "lxml")
    rec = {"id": oid, "url": url}
    t = s.find("h1") or s.find("title")
    rec["title"] = t.get_text(" ", strip=True) if t else ""
    for div in s.select("div.detailField"):
        lab = div.find(class_="detailFieldLabel")
        val = div.find(class_="detailFieldValue")
        if lab and val:
            rec[lab.get_text(" ", strip=True).rstrip(":")] = val.get_text(" | ", strip=True)
        elif not lab:
            cls = [c for c in div.get("class", []) if c != "detailField"]
            rec[";".join(cls) or "field"] = div.get_text(" | ", strip=True)
    m = s.find("main") or s.body
    txt = m.get_text(" | ", strip=True)
    i = txt.find(rec["title"])
    j = txt.find("| Expand |", i)
    rec["fulltext"] = txt[i:j if j > 0 else i + 4000]
    imgs = []
    for im in s.find_all("img", src=True):
        if "/internal/media/" in im["src"]:
            imgs.append(BASE + im["src"] if im["src"].startswith("/") else im["src"])
    rec["images"] = sorted(set(imgs))
    return rec


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "search":
        for term in sys.argv[2:]:
            total, res = search(term)
            print(json.dumps({"term": term, "total": total, "results": res}, ensure_ascii=False))
    else:
        for oid in sys.argv[2:]:
            print(json.dumps(obj(oid), ensure_ascii=False))
