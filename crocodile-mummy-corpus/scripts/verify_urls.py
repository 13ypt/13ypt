#!/usr/bin/env python3
"""Mechanical check of object evidence: does each online_record_url resolve, and does
the fetched page (HTML/JSON) contain the recorded inventory number?

Output: work/url_check.csv (object_id, url, http_status, inventory_found, note), written
incrementally so an interrupted run can resume. This is a screening aid only: many
museum sites render records with JavaScript or block automated clients (403/429), and
catalogue PDFs/scans may not contain the number as text, so "NO" or an error is a prompt
for manual checking, not evidence against a record.
"""
import csv
import os
import re
import sys
import time
import unicodedata

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = {"User-Agent": "Mozilla/5.0 (research corpus verification)",
           "Accept": "text/html,application/json;q=0.9,*/*;q=0.8"}
FIELDS = ["object_id", "url", "http_status", "inventory_found", "note"]


def squash(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[\s.\-_/,:;()]+", "", s.lower())


def main():
    out_path = os.path.join(ROOT, "work", "url_check.csv")
    done = set()
    if os.path.exists(out_path):
        done = {(r["object_id"], r["url"]) for r in csv.DictReader(open(out_path, encoding="utf-8"))}
    new_file = not os.path.exists(out_path)
    fh = open(out_path, "a", encoding="utf-8", newline="")
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    if new_file:
        w.writeheader()
    rows = list(csv.DictReader(open(os.path.join(ROOT, "objects_master.csv"), encoding="utf-8")))
    cache, last_host_hit = {}, {}
    for o in rows:
        inv = o["inventory_number"]
        urls = [u.strip() for u in re.split(r";|\|", o["online_record_url"]) if u.strip().startswith("http")]
        for url in urls:
            if (o["object_id"], url) in done:
                continue
            if url not in cache:
                host = re.sub(r"^https?://([^/]+).*", r"\1", url)
                wait = 1.5 - (time.time() - last_host_hit.get(host, 0))
                if wait > 0:
                    time.sleep(wait)
                last_host_hit[host] = time.time()
                try:
                    resp = requests.get(url, headers=HEADERS, timeout=20)
                    body = resp.text if resp.ok and len(resp.content) < 5_000_000 else ""
                    cache[url] = (str(resp.status_code), body, "")
                except requests.RequestException as exc:
                    cache[url] = ("ERROR", "", type(exc).__name__)
            status, text, note = cache[url]
            if not inv or inv == "UNKNOWN":
                found = "N/A"
            elif text:
                found = "YES" if squash(inv) in squash(text) else "NO"
            else:
                found = ""
            w.writerow({"object_id": o["object_id"], "url": url, "http_status": status,
                        "inventory_found": found, "note": note})
            fh.flush()
            print(o["object_id"], status, found, url[:90], file=sys.stderr)
    fh.close()


if __name__ == "__main__":
    main()
