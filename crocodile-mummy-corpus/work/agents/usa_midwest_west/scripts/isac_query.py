#!/usr/bin/env python3
"""Query the ISAC (Oriental Institute) Integrated Database Solr endpoint (dataset=MC).

Usage: python3 isac_query.py "<solr q>" [out.json]
Prints prefix+registration number, classification, description, site, period.
Polite: paginates with 1 s pauses.
"""
import json
import sys
import time

import requests

URL = "https://isac-idb.uchicago.edu/solr/index.php"
H = {"User-Agent": "Mozilla/5.0 (research survey; crocodile mummy corpus)"}


def search(q, dataset="MC"):
    docs, start = [], 0
    while True:
        r = requests.get(URL, params={"dataset": dataset, "q": q, "rows": 100, "start": start},
                         headers=H, timeout=60)
        r.raise_for_status()
        d = r.json()["response"]
        docs += d["docs"]
        start += 100
        if start >= d["numFound"]:
            return docs, d["numFound"]
        time.sleep(1)


def j(v):
    return "; ".join(v) if isinstance(v, list) else (v or "")


if __name__ == "__main__":
    docs, n = search(sys.argv[1])
    print(f"q={sys.argv[1]!r} numFound={n}")
    for d in docs:
        num = j(d.get("ColPrefix")) + " " + str(d.get("ColRegistrationNumber", ""))
        print(" | ".join([num, j(d.get("ColClassification")), j(d.get("CatDescription"))[:160],
                          j(d.get("ProSiteLevel1")), j(d.get("DatPeriod"))]))
    if len(sys.argv) > 2:
        json.dump(docs, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
