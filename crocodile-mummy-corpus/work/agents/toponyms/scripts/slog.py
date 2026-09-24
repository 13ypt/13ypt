#!/usr/bin/env python3
"""Helper: read pipe-separated lines 'country|language|db|query|institution|result|notes'
and pipe them as JSON to rec.py search_log for agent toponyms."""
import json, subprocess, sys
lines = []
for raw in sys.stdin:
    raw = raw.rstrip("\n")
    if not raw.strip():
        continue
    p = raw.split("|")
    p += [""] * (7 - len(p))
    rec = {"country": p[0] or "UNKNOWN", "language": p[1], "database_or_search_engine": p[2],
           "query": p[3], "institution_checked": p[4], "result": p[5], "notes": p[6]}
    lines.append(json.dumps(rec, ensure_ascii=False))
r = subprocess.run([sys.executable, "/home/user/13ypt/crocodile-mummy-corpus/scripts/rec.py", "toponyms", "search_log"],
                   input="\n".join(lines) + "\n", text=True, capture_output=True, cwd="/home/user/13ypt")
print(r.stdout, r.stderr)
