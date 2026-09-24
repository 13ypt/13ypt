#!/usr/bin/env python3
"""Fetch Louvre ark JSON records (collections.louvre.fr/ark:/53355/<id>.json) politely and print key fields.
Usage: louvre_ark.py cl0100xxxxx [cl0100yyyyy ...]  -> saves raw JSON to ../raw/louvre_<id>.json"""
import json, sys, time, os, subprocess
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
for ark in sys.argv[1:]:
    path = os.path.join(RAW, f"louvre_{ark}.json")
    if not os.path.exists(path):
        url = f"https://collections.louvre.fr/ark:/53355/{ark}.json"
        r = subprocess.run(["curl", "-sS", "-A", "Mozilla/5.0", "-o", path, "-w", "%{http_code}", url], capture_output=True, text=True)
        time.sleep(2)
        if r.stdout != "200":
            print(ark, "HTTP", r.stdout); os.remove(path); continue
    d = json.load(open(path))
    def g(k): return d.get(k)
    print("=" * 80)
    print(ark, "|", g("title"), "|", g("titleComplement"), "|", [o["value"] + " (" + o["type"] + ")" for o in g("objectNumber") or []])
    print(" denom:", [x["value"] for x in g("denominationTitle") or []])
    print(" date:", g("displayDateCreated"), "| loc:", g("currentLocation"), "| heldBy:", g("heldBy"), "| loan:", g("longTermLoanTo"))
    print(" dims:", [x["displayDimension"] + " " + x["type"] for x in g("dimension") or []])
    print(" mat:", g("materialsAndTechniques"), "| place:", g("placeOfCreation"), "| disc:", g("placeOfDiscovery"), g("dateOfDiscovery"))
    print(" desc:", (g("description") or "")[:500])
    print(" hist:", (g("objectHistory") or "")[:300], "| prov:", g("provenance"))
    print(" prev:", [p["value"] + p.get("role", "") for p in g("previousOwner") or []])
    print(" acq:", [(a["mode"], [x["value"] for x in a["dates"]]) for a in g("acquisitionDetails") or []])
    print(" biblio:", [b["bibliographyRef"][:120] + " " + b.get("bibliographyDetail", "") for b in g("bibliography") or []][:6])
    print(" images:", len(g("image") or []), (g("image") or [{}])[0].get("copyright") if g("image") else "")
    print(" related:", g("relatedWork"))
