#!/usr/bin/env python3
"""Query Smithsonian Open Access API (DEMO_KEY) and print compact summaries.
Usage: si_query.py "<q>" [rows] [start]
"""
import json, sys, time, urllib.parse, os, requests
q = sys.argv[1]; rows = int(sys.argv[2]) if len(sys.argv)>2 else 100; start=int(sys.argv[3]) if len(sys.argv)>3 else 0
url = "https://api.si.edu/openaccess/api/v1.0/search?" + urllib.parse.urlencode({"q": q, "rows": rows, "start": start, "api_key": "DEMO_KEY"})
r = requests.get(url, timeout=60)
d = r.json()
out = os.path.join(os.path.dirname(__file__), '..', 'raw', 'si_' + ''.join(c if c.isalnum() else '_' for c in q)[:60] + f'_{start}.json')
json.dump(d, open(out, 'w'))
resp = d.get('response', {})
print("Q:", q, "status", r.status_code, "rowCount", resp.get('rowCount'))
for row in resp.get('rows', []):
    c = row.get('content', {})
    ft = c.get('freetext', {})
    ids = [x.get('content') for x in ft.get('identifier', [])]
    ot = [x.get('content') for x in ft.get('objectType', [])]
    pl = [x.get('content') for x in ft.get('place', [])]
    print(' ', row.get('unitCode'), '|', row.get('title'), '|', ids[:3], '|', ot[:2], '|', pl[:1], '|', c.get('descriptiveNonRepeating', {}).get('record_ID'))
