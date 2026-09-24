#!/usr/bin/env python3
"""Search the Musée des Confluences portal (portail.museedesconfluences.fr, Alphamosa) and list results.
Usage: mdc_search.py "query" [famille] [max_pages]"""
import re, html, sys, subprocess, time, urllib.parse
q = sys.argv[1]; fam = sys.argv[2] if len(sys.argv) > 2 else ""; maxp = int(sys.argv[3]) if len(sys.argv) > 3 else 10
seen = []
for page in range(1, maxp + 1):
    params = {"collection": "biens", "recherche_libre": q, "biens_famille": fam, "vue": "liste", "par_page": "80"}
    if page > 1: params["debut_notices"] = str((page - 1) * 80)
    url = "https://portail.museedesconfluences.fr/fr/collections/search?" + urllib.parse.urlencode(params)
    t = subprocess.run(["curl", "-sSL", "-A", "Mozilla/5.0", url], capture_output=True, text=True).stdout
    total = re.search(r'data-total="(\d+)"', t)
    if page == 1: print("URL:", url, "\nTOTAL:", total.group(1) if total else "?")
    # result blocks: notice link then text until 'Inv. n°'
    t2 = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    blocks = re.split(r'(?=href="[^"]*notice\d+)', t2)
    new = 0
    for b in blocks[1:]:
        m = re.match(r'href="([^"]*notice(\d+)[^"]*)"', b)
        if not m or m.group(2) in [s[0] for s in seen]: continue
        txt = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' | ', b[:3000])))
        inv = re.search(r'Inv\. n°\s*([^|]+)', txt)
        seen.append((m.group(2), txt[:250].strip(), inv.group(1).strip() if inv else ""))
        new += 1
    if new == 0: break
    time.sleep(1.5)
for s in seen: print(f"notice{s[0]}\t{s[2]}\t{s[1]}")
