#!/usr/bin/env python3
"""Convert a sweep query log (jsonl) into search_log records for rec.py (printed to stdout).
Usage: querylog_to_searchlog.py LOGFILE DBNAME [INSTITUTION]"""
import json, sys
path, db = sys.argv[1], sys.argv[2]
inst = sys.argv[3] if len(sys.argv) > 3 else "ALL (aggregator)"
for line in open(path, encoding="utf-8"):
    e = json.loads(line)
    q = e.get("params") or e.get("rq") or {}
    extra = f" resource_id={e['resource_id']}" if "resource_id" in e else ""
    hits = {k: v for k, v in e.items() if k.endswith("_hits")}
    result = (f"{e.get('count')} records matched, {e.get('fetched')} fetched and scanned; "
              + ", ".join(f"{k}={v}" for k, v in hits.items()))
    print(json.dumps({"date": e.get("ts", "")[:10], "country": "UNKNOWN", "language": "multilingual",
                      "database_or_search_engine": db,
                      "query": f"{e['label']} | {e.get('api')} {json.dumps(q, ensure_ascii=False)}{extra}",
                      "institution_checked": inst, "result": result,
                      "notes": "scripted sweep; hits = records whose text matched mummy regex (and crocodilian); egypt = crocodilian records with Egypt/Egyptian site in locality/country; reviewed manually"},
                     ensure_ascii=False))
