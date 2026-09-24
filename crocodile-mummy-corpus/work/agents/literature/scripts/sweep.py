#!/usr/bin/env python3
"""Crossref sweep: many queries, keep only items whose TITLE matches crocodile+mummy terms (multilingual).
Usage: python3 sweep.py  -> prints merged unique relevant hits; saves ../raw/crossref_sweep.json"""
import json, os, re, time, requests
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
QUERIES = ["crocodile mummy", "crocodile mummies", "mummified crocodile", "mummified crocodiles", "crocodile mummification",
 "Krokodilmumie", "Krokodilmumien", "mumifiziertes Krokodil", "momie de crocodile", "momies de crocodiles", "crocodiles momifiés",
 "mummia di coccodrillo", "mummie di coccodrillo", "coccodrilli mummificati", "momia de cocodrilo", "momias de cocodrilo",
 "krokodillenmummie", "krokodilmumie", "mumie krokodýla", "mumia krokodyla", "мумия крокодила", "مومياء التمساح", "تماسيح محنطة",
 "Sobek sacred crocodile burial", "crocodile necropolis Egypt", "crocodile cemetery Fayum", "crocodile eggs mummified",
 "crocodile hatchlings mummies", "animal mummies crocodiles CT", "Crocodylus suchus mummy", "Kom Ombo crocodile mummies",
 "Tebtunis crocodile mummies papyrus", "Maabda crocodile cave", "crocodile cave Samoun", "Soknopaiou Nesos crocodile",
 "Theadelphia crocodile", "Medinet Madi crocodile", "Narmouthis crocodile", "Akoris crocodile", "Tuna el-Gebel crocodile",
 "Hawara crocodile", "Gebelein crocodile", "Elkab crocodile", "Esna crocodile", "Qubbet el-Hawa crocodile", "Deir el-Bersha crocodile",
 "crocodile sarcophagus Egypt", "crocodile coffin Egypt", "Souchos crocodile", "Petesouchos", "crocodile cult Fayum", "Sobek cult crocodiles mummified"]
PAT = re.compile(r"(crocod|krokod|coccodr|cocodr|timsa|تمساح|تماسيح|крокод|sobek|souch|suchos|petesouch)", re.I)
PAT2 = re.compile(r"(mumm|momi|mumi|мумі|мумия|مومي|محنط|embalm|burial|necropol|cemet|nécropole|tomb|grave|cave|grott|cult|kult|culte|sarcoph|coffin|egg)", re.I)
hits = {}
for q in QUERIES:
    try:
        r = requests.get("https://api.crossref.org/works", params={"query.bibliographic": q, "rows": 100, "select": "DOI,title,issued,container-title,author,type"}, timeout=60)
        items = r.json()["message"]["items"]
    except Exception as e:
        print("ERR", q, e); continue
    n = 0
    for it in items:
        t = (it.get("title") or [""])[0]
        if PAT.search(t) and PAT2.search(t):
            d = it["DOI"].lower()
            if d not in hits:
                yr = (it.get("issued") or {}).get("date-parts", [[None]])[0][0]
                au = "; ".join(a.get("family", "") for a in (it.get("author") or [])[:4])
                hits[d] = {"doi": d, "year": yr, "title": t, "venue": (it.get("container-title") or [""])[0] if it.get("container-title") else "", "authors": au, "queries": [q]}
                n += 1
            else:
                hits[d]["queries"].append(q)
    print(f"# {q}: {len(items)} items, {n} new relevant")
    time.sleep(1)
json.dump(list(hits.values()), open(os.path.join(RAW, "crossref_sweep.json"), "w"), ensure_ascii=False, indent=1)
for h in sorted(hits.values(), key=lambda x: (x["year"] or 0)):
    print(f"{h['year']} | {h['doi']} | {h['title'][:150]} | {h['venue'][:50]} | {h['authors'][:50]}")
