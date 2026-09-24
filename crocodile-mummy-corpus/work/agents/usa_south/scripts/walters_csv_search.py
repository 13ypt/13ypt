#!/usr/bin/env python3
"""Search the Walters Art Museum open-data art.csv (https://raw.githubusercontent.com/WaltersArtMuseum/api-thewalters-org/main/art.csv)
for crocodile / Sobek / mummy records. Usage: walters_csv_search.py path/to/art.csv"""
import csv, re, sys, json
csv.field_size_limit(10**9)
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
out = {"n_rows": len(rows), "croc_or_sobek_mummy": [], "mummy_objects": []}
for r in rows:
    allt = ' '.join(str(v) for v in r.values())
    t = r['Title'] + ' ' + r['ObjectName'] + ' ' + r['Medium']
    if re.search(r'mumm', t, re.I):
        out["mummy_objects"].append({k: r[k] for k in ('ObjectID', 'AccessionNumber', 'Title', 'ObjectName', 'ResourceURL')})
        if re.search(r'crocodil|sobek|souchos|suchos', allt, re.I):
            out["croc_or_sobek_mummy"].append(r['AccessionNumber'])
print(json.dumps(out, indent=1))
