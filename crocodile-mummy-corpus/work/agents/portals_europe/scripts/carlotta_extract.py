#!/usr/bin/env python3
"""Extract key fields from Carlotta museum-database object pages (used by
Medelhavsmuseet/SMVK, Malmö museer, Göteborg etc.).  Prints JSON per object and
stores it in ../raw/carlotta_<host>.json.

Usage: python3 carlotta_extract.py BASE_URL OBJID [OBJID ...]
  e.g. python3 carlotta_extract.py https://collections.smvk.se/carlotta-mhm 3016253
"""
import json
import os
import re
import sys
import time
import warnings

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")
UA = "Mozilla/5.0 crocodile-mummy-corpus research (polite)"
LABELS = ["Inventory number", "Inventarienummer", "Object", "Sakord", "Object description",
          "Description", "Beskrivning", "Acquisition", "Förvärv", "Dimensions", "Mått",
          "Condition", "Comments", "Kommentar", "Country - Findspot", "Land - Fyndort",
          "Dating", "Datering", "Length / Längd", "Width / Bredd", "Place - Findspot",
          "Name - Acquired from", "Antal", "Number of objects", "Material", "Längd", "Bredd",
          "Höjd", "Anskaffning", "Förvärvsdatum", "Fyndort", "Benämning", "Inv.nr"]


def extract(base, oid):
    url = f"{base}/web/object/{oid}"
    r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
    html = r.text
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    lines = [re.sub(r"\s+", " ", l).strip() for l in soup.get_text("\n").split("\n")]
    lines = [l for l in lines if l and "%20" not in l]
    rec = {"url": url, "status": r.status_code}
    # heading after "Go back"
    if "Go back" in lines:
        i = lines.index("Go back")
        rec["heading"] = lines[i + 1:i + 4]
    for lab in LABELS:
        if lab in lines:
            idx = [i for i, l in enumerate(lines) if l == lab]
            vals = []
            for i in idx:
                if i + 1 < len(lines):
                    vals.append(lines[i + 1])
            rec[lab] = vals
    imgs = sorted(set(re.findall(r'/web/image/(?:zoom|tn)/(\d+)/([^";]+?)\.jpg', html)))
    rec["images"] = [f"{base}/web/image/zoom/{a}/{b}.jpg" for a, b in imgs
                     if "thumbnail" not in b]
    lic = sorted(set(re.findall(r'(https?://creativecommons\.org/[a-z/.0-9-]+)', html)))
    rec["licence_links"] = lic
    return rec


def main():
    base = sys.argv[1].rstrip("/")
    host = re.sub(r"\W+", "_", base.split("//")[1])
    path = os.path.join(RAW, f"carlotta_{host}.json")
    store = json.load(open(path)) if os.path.exists(path) else {}
    for oid in sys.argv[2:]:
        try:
            rec = extract(base, oid)
            store[oid] = rec
            print(json.dumps(rec, ensure_ascii=False))
        except Exception as exc:  # noqa
            print("FAIL", oid, exc)
        time.sleep(1)
    json.dump(store, open(path, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
