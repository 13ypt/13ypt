#!/usr/bin/env python3
"""Query UCL Collections Online (Axiell) for one database and a simple-search value; print result rows.
usage: ucl_search.py <db: petrie|zoology|...> "<query>" [maxpages]"""
import sys, re, html, time, requests
db, q = sys.argv[1], sys.argv[2]
maxpages = int(sys.argv[3]) if len(sys.argv) > 3 else 5
dbs = ["collect", "art", "zoology", "jeremybentham", "pathology", "petrie", "science"]
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
params = {}
for i, d in enumerate(dbs):
    params[f"DatabaseChoices[{i}].Name"] = d
    params[f"DatabaseChoices[{i}].Selected"] = "True" if d == db else "False"
params.update({"Fields[0].Value": q, "Fields[0].FieldName": "Search_SearchSimple_FieldLabel", "Fields[0].SearchInField": "False"})
r = s.get("https://collections.ucl.ac.uk/search/simple/repeat", params=params, timeout=60)
out = []
page = 1
while True:
    t = r.text
    m = re.search(r"([0-9]+)\s+Results", re.sub(r"<[^>]+>", " ", t))
    if page == 1:
        print("TOTAL", m.group(1) if m else "?")
    for blk in re.findall(r'href="(/Details/[^"]+)"', t):
        if blk not in out:
            out.append(blk)
    nxt = re.search(r'href="(/results\?page=%d[^"]*)"' % (page + 1), t) or re.search(r'href="([^"]*[?&]page=%d[^"]*)"' % (page + 1), t)
    if not nxt or page >= maxpages:
        break
    page += 1
    time.sleep(1)
    r = s.get("https://collections.ucl.ac.uk" + html.unescape(nxt.group(1)), timeout=60)
for o in out:
    print(o)
