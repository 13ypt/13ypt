#!/usr/bin/env python3
"""Query National Museums Liverpool public Solr index (used by www.liverpoolmuseums.org.uk/search).
Usage: nml_solr.py term [term...] -> JSON lines of collection/artifact docs (deduplicated by id)."""
import json, sys, time, requests
BASE = "https://index.liverpoolmuseums.org.uk/select"
seen = {}
for term in sys.argv[1:]:
    q = f"tm_X3b_en_title_2:({term})^2 OR tm_X3b_en_aggregated_field:({term})"
    r = requests.get(BASE, params={"wt": "json", "q": q, "fq": "(ss_type:collection OR ss_type:artifact)", "rows": 500, "start": 0},
                     headers={"User-Agent": "Mozilla/5.0 (research; crocodile mummy corpus)"}, timeout=60)
    d = r.json()["response"]
    print(f"# {term}: numFound={d['numFound']}", file=sys.stderr)
    for doc in d["docs"]:
        if doc["id"] not in seen:
            doc["_term"] = term
            seen[doc["id"]] = doc
    time.sleep(1)
for doc in seen.values():
    print(json.dumps(doc, ensure_ascii=False))
