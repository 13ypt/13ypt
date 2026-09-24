#!/usr/bin/env python3
"""Mechanical check of object evidence: does each online_record_url resolve, and does
the fetched page (HTML/JSON) contain the recorded inventory number?

Output: work/url_check.csv (object_id, url, http_status, inventory_found, note).
This is a screening aid only: many museum sites render records with JavaScript or
block automated clients (403/429), so "not found" is a prompt for manual checking,
not evidence against a record.
"""
import csv
import os
import re
import sys
import time
import unicodedata

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = {"User-Agent": "Mozilla/5.0 (research corpus verification; contact via repository)",
           "Accept": "text/html,application/json;q=0.9,*/*;q=0.8"}


def squash(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[\s.\-_/,:;()]+", "", s.lower())


def main():
    done = {}
    out_path = os.path.join(ROOT, "work", "url_check.csv")
    if os.path.exists(out_path):
        for r in csv.DictReader(open(out_path, encoding="utf-8")):
            done[(r["object_id"], r["url"])] = r
    rows = list(csv.DictReader(open(os.path.join(ROOT, "objects_master.csv"), encoding="utf-8")))
    results = list(done.values())
    last_host_hit = {}
    for o in rows:
        inv = o["inventory_number"]
        for url in [u.strip() for u in o["online_record_url"].split(";") if u.strip().startswith("http")]:
            if (o["object_id"], url) in done:
                continue
            host = re.sub(r"^https?://([^/]+).*", r"\1", url)
            wait = 1.5 - (time.time() - last_host_hit.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            last_host_hit[host] = time.time()
            status, found, note = "", "", ""
            try:
                resp = requests.get(url, headers=HEADERS, timeout=40)
                status = str(resp.status_code)
                if resp.ok and inv and inv != "UNKNOWN":
                    found = "YES" if squash(inv) in squash(resp.text) else "NO"
                elif not inv or inv == "UNKNOWN":
                    found = "N/A"
            except requests.RequestException as exc:
                status, note = "ERROR", type(exc).__name__
            results.append({"object_id": o["object_id"], "url": url, "http_status": status,
                            "inventory_found": found, "note": note})
            print(o["object_id"], status, found, url[:90], file=sys.stderr)
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["object_id", "url", "http_status", "inventory_found", "note"])
        w.writeheader()
        w.writerows(sorted(results, key=lambda r: (r["object_id"], r["url"])))


if __name__ == "__main__":
    main()
