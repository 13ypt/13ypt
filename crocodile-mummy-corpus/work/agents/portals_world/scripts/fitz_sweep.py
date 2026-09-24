"""Fitzwilliam Museum data portal sweep (data.fitzmuseum.cam.ac.uk).

Search pages (HTML, operator=AND, all pages) -> object ids; JSON per object via
/id/object/<priref>?format=json (empty User-Agent works). Flags crocodile + mummy records.
"""
import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

from common import save_raw

S = requests.Session()
S.headers.update({"User-Agent": ""})
BASE = "https://data.fitzmuseum.cam.ac.uk"
QUERIES = ["crocodile mummy", "mummified crocodile", "reptile mummy", "animal mummy", "crocodile",
           "Sobek", "crocodile egg", "Kom Ombo"]
PM = re.compile(r"mumm", re.I)
PC = re.compile(r"crocod|sobek", re.I)


def search(q):
    ids, titles, page, total = [], {}, 1, None
    while True:
        time.sleep(1.1)
        r = S.get(f"{BASE}/search/results", params={"query": q, "operator": "AND", "sort": "desc", "page": page}, timeout=90)
        s = BeautifulSoup(r.text, "lxml")
        t = s.get_text(" ", strip=True)
        m = re.search(r"([0-9,]+) results?", t)
        total = int(m.group(1).replace(",", "")) if m else 0
        new = 0
        for a in s.find_all("a", href=True):
            mm = re.search(r"/id/object/(\d+)$", a["href"])
            if mm:
                i = mm.group(1)
                if i not in titles:
                    ids.append(i)
                    new += 1
                if a.get_text(strip=True):
                    titles[i] = a.get_text(" ", strip=True)
        if not new or len(ids) >= total or page >= 20:
            break
        page += 1
    return total, ids, titles


def main():
    out, objs = {}, {}
    for q in QUERIES:
        total, ids, titles = search(q)
        flagged = []
        for i in ids:
            if q == "crocodile" and not (PM.search(titles.get(i, "")) or PC.search(titles.get(i, ""))):
                continue
            if i not in objs:
                time.sleep(1.1)
                try:
                    objs[i] = S.get(f"{BASE}/id/object/{i}", params={"format": "json"}, timeout=90).json()
                except Exception as exc:
                    objs[i] = {"error": str(exc)}
            blob = json.dumps(objs[i], ensure_ascii=False)
            if PM.search(blob) and PC.search(blob):
                flagged.append(i)
        out[q] = {"total": total, "retrieved_ids": len(ids), "titles": titles, "flagged": flagged}
        print(q, total, len(ids), flagged, file=sys.stderr)
    save_raw("fitz_results.json", out)
    fl = sorted({i for v in out.values() for i in v["flagged"]}, key=int)
    save_raw("fitz_flagged_objects.json", {i: objs[i] for i in fl})
    for i in fl:
        o = objs[i]
        acc = [x.get("value") for x in o.get("identifier", []) if x.get("type") == "accession number"]
        print(i, acc, o.get("summary_title"), "|", [d.get("value") for d in o.get("description", [])])


if __name__ == "__main__":
    main()
