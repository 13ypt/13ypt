#!/usr/bin/env python3
"""Page through museum-digital JSON objects for an arbitrary parameter string, e.g. 'tag_id=5641'."""
import sys, time, requests
param = sys.argv[1]; inst = sys.argv[2] if len(sys.argv) > 2 else "global"
start = 0; rows = []; total = None
while True:
    d = requests.get(f"https://{inst}.museum-digital.org/json/objects?{param}&startwert={start}", timeout=60).json()
    if not isinstance(d, list) or not d: break
    rows += d; total = int(d[0].get("total", 0)); start += len(d)
    if start >= total: break
    time.sleep(1)
print(f"# {param} total={total} fetched={len(rows)}", file=sys.stderr)
for x in rows:
    print(f"{x['objekt_id']} | {x['objekt_name']} | {x.get('objekt_inventarnr')} | {x['institution_name']}")
