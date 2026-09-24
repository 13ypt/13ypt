#!/usr/bin/env python3
"""Helper: log one search via rec.py. Usage: log.py COUNTRY LANG DB QUERY INSTITUTION RESULT [NOTES]"""
import json, subprocess, sys
a = sys.argv[1:]
rec = {"country": a[0], "language": a[1], "database_or_search_engine": a[2], "query": a[3],
       "institution_checked": a[4], "result": a[5]}
if len(a) > 6: rec["notes"] = a[6]
p = subprocess.run(["python3", "/home/user/13ypt/crocodile-mummy-corpus/scripts/rec.py", "france", "search_log"],
                   input=json.dumps(rec, ensure_ascii=False), text=True, capture_output=True, cwd="/home/user/13ypt")
print(p.stdout.strip(), p.stderr.strip())
