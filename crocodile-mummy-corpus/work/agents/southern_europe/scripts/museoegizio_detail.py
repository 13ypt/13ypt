#!/usr/bin/env python3
"""Fetch Museo Egizio object detail pages and extract text fields + main image URLs.
Usage: museoegizio_detail.py Cat_2351_01 Provv_1443 ...   (lang it-IT by default; set LANG_ME=en-GB)
Outputs JSON lines."""
import sys, re, html, json, time, os, requests
lang = os.environ.get("LANG_ME", "it-IT")
for slug in sys.argv[1:]:
    url = f"https://collezioni.museoegizio.it/{lang}/material/{slug}/"
    h = requests.get(url, timeout=60).text
    t = re.sub(r'<script.*?</script>', '', h, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '\n', t); t = html.unescape(t)
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    s = '\n'.join(lines)
    i = s.find('Torna alla ricerca') if lang == 'it-IT' else s.find('Back to search')
    body = s[i:i+2500] if i >= 0 else s[:2500]
    rec = {"slug": slug, "url": url}
    keys = ["Nr. inv.:", "Materiale:", "Dimensioni:", "Datazione:", "Periodo:", "Provenienza:", "Acquisizione:", "Collocazione:", "Bibliografia scelta:",
            "Inv. no.:", "Material:", "Dimensions:", "Dating:", "Period:", "Provenance:", "Acquisition:", "Location:", "Selected bibliography:"]
    bl = body.split('\n')
    rec["title"] = bl[1] if len(bl) > 1 else ""
    rec["description"] = bl[2] if len(bl) > 2 else ""
    for k in keys:
        if k in bl:
            j = bl.index(k)
            val = bl[j+1]
            if k.startswith("Bibliografia") or k.startswith("Selected"):
                val = " ".join(bl[j+1:j+5])
            rec[k.rstrip(':')] = val
    ogi = re.findall(r'(/public/objects/images/[^"\'\s)]+_(?:full|big)\.jpg)', h)
    rec["images"] = sorted(set("https://collezioni.museoegizio.it" + x for x in ogi))
    print(json.dumps(rec, ensure_ascii=False))
    time.sleep(1)
