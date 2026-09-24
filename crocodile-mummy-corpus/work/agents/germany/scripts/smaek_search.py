#!/usr/bin/env python3
"""Query SMÄK Munich 'Sammlung Online' (sammlung.smaek.de) backend, the Fluxguide EMP3
content API used by the public site (endpoint and public client token are in the site's JS).
Usage: python3 smaek_search.py <term> [term2 ...]   -> prints id | title | inventory | fields
"""
import json, sys, requests
URL = "https://smaek-api.fluxguide.dev/content/v1/query"
HDR = {"Content-Type": "application/json", "Authorization": "Bearer fluxguide_6b5e35e2"}
terms = sys.argv[1:]
body = {"appID": 1, "contentType": ["Object"], "language": ["de"], "limit": 200,
        "includeFileList": True, "fulltextsearch": terms, "fulltextsearchOperator": "AND"}
r = requests.post(URL, headers=HDR, data=json.dumps(body), timeout=90)
d = r.json()
print(f"# terms={terms} countTotal={d.get('countTotal')}", file=sys.stderr)
els = d.get("contentElements", {})
out = []
for k, v in (els.items() if isinstance(els, dict) else enumerate(els)):
    c = v.get("content", v)
    out.append({"key": k, **{kk: c.get(kk) for kk in c if isinstance(c.get(kk), (str, int, float)) and kk not in ()}})
json.dump(out, sys.stdout, ensure_ascii=False, indent=0)
