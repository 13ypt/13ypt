#!/usr/bin/env python3
"""Helper: python3 w.py <kind> <file.py-with-RECS-list>  or pass JSON list on stdin. Pipes each dict to rec.py."""
import json, subprocess, sys
kind = sys.argv[1]
recs = json.load(sys.stdin)
data = "\n".join(json.dumps(r, ensure_ascii=False) for r in recs)
p = subprocess.run(["python3", "/home/user/13ypt/crocodile-mummy-corpus/scripts/rec.py", "literature", kind], input=data, text=True, capture_output=True)
print(p.stdout.strip(), p.stderr.strip())
