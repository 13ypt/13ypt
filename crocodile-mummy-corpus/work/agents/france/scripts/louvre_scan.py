#!/usr/bin/env python3
"""Polite scan of a small range of Louvre ark IDs (the Egyptian animal-mummy cluster), because
collections.louvre.fr/recherche returns 429 (WADP bot challenge) for search. 1 request / 1.5 s.
Usage: louvre_scan.py START END  (integers, e.g. 10013900 10014200)
Writes raw/louvre_scan_<START>_<END>.tsv (ark, http, number, title) and saves JSON of any record whose
title/denomination/description mentions 'crocodil'."""
import json, sys, time, os, subprocess
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
s, e = int(sys.argv[1]), int(sys.argv[2])
out = open(os.path.join(RAW, f"louvre_scan_{s}_{e}.tsv"), "a")
for n in range(s, e + 1):
    ark = f"cl0{n}"
    r = subprocess.run(["curl", "-sS", "-A", "Mozilla/5.0", "-w", "\n%{http_code}", f"https://collections.louvre.fr/ark:/53355/{ark}.json"], capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n")
    num = title = ""
    if code == "200":
        try:
            d = json.loads(body)
            num = "; ".join(o["value"] for o in d.get("objectNumber") or [])
            title = d.get("title", "")
            blob = json.dumps([d.get("title"), d.get("denominationTitle"), d.get("description"), d.get("index")], ensure_ascii=False).lower()
            if "crocodil" in blob:
                json.dump(d, open(os.path.join(RAW, f"louvre_{ark}.json"), "w"), ensure_ascii=False)
                title = "*CROC* " + title
        except Exception as ex:
            title = f"parse error {ex}"
    out.write(f"{ark}\t{code}\t{num}\t{title}\n"); out.flush()
    if code == "429":
        time.sleep(60)
    time.sleep(1.5)
