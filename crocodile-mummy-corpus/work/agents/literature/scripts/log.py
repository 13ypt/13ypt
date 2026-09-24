#!/usr/bin/env python3
"""Append search_log rows: python3 log.py 'engine' 'language' 'query' 'result' ['notes']  (country=XX global)"""
import json, subprocess, sys
eng, lang, q, res = sys.argv[1:5]
notes = sys.argv[5] if len(sys.argv) > 5 else ""
rec = {"country": "UNKNOWN", "language": lang, "database_or_search_engine": eng, "query": q, "result": res, "notes": notes or "literature agent (global scope)"}
p = subprocess.run(["python3", "/home/user/13ypt/crocodile-mummy-corpus/scripts/rec.py", "literature", "search_log"], input=json.dumps(rec), text=True, capture_output=True)
print(p.stdout.strip(), p.stderr.strip())
