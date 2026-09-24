#!/usr/bin/env python3
"""Query collezioni.museoegizio.it search (HTML page embeds JSON 'listaRisultati').
Usage: museoegizio_search.py FIELD=VALUE [FIELD=VALUE...]  (fields: description,title,provenance,inventoryNumber,...)
Prints total and one line per hit: Label | Title | Description | Link
"""
import sys, re, json, time, urllib.parse, requests
params = {"action": "s"}
for a in sys.argv[1:]:
    k, v = a.split("=", 1); params[k] = v
allhits = []
page = 1
while True:
    p = dict(params); p["searchPage"] = str(page)
    url = "https://collezioni.museoegizio.it/it-IT/search?" + urllib.parse.urlencode(p)
    r = requests.get(url, timeout=60)
    h = r.text
    m = re.search(r'"listaRisultati":\s*(\[.*?\])\s*,\s*"', h, re.S)
    tot = re.search(r'class="value">(\d+)', h)
    if not m:
        break
    try:
        hits = json.loads(m.group(1))
    except Exception as e:
        # fallback: bracket matching
        s = h.find('"listaRisultati"'); s = h.find('[', s); depth = 0
        for i in range(s, len(h)):
            if h[i] == '[': depth += 1
            elif h[i] == ']':
                depth -= 1
                if depth == 0: break
        hits = json.loads(h[s:i+1])
    if not hits: break
    new = [x for x in hits if x["Uid"] not in {y["Uid"] for y in allhits}]
    if not new: break
    allhits += new
    total = int(tot.group(1)) if tot else 0
    if len(allhits) >= total: break
    page += 1; time.sleep(1)
print("TOTAL", tot.group(1) if tot else "?", "retrieved", len(allhits))
for x in allhits:
    print(x.get("Label"), "|", x.get("Title"), "|", x.get("Description"), "|", x.get("Link", "").split("?")[0])
