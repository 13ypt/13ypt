#!/usr/bin/env python3
"""Fetch National Museums Liverpool artifact records by accession number via the public Drupal
JSON:API (content.liverpoolmuseums.org.uk/jsonapi/node/artifact?filter[field_number]=...),
plus image paragraph credit lines. Usage: nml_jsonapi.py NUM [NUM...] -> JSON lines."""
import json, sys, time, requests
H = {"User-Agent": "Mozilla/5.0 (research; crocodile mummy corpus)"}
B = "https://content.liverpoolmuseums.org.uk/jsonapi/node/artifact"
KEEP = ["title", "field_number", "field_itemname", "field_description", "field_measurements", "field_placecollected",
        "field_placemade", "field_date_collected", "field_datecollected", "field_collector", "field_credit_line",
        "field_culture", "field_materials", "field_other_numbers", "field_provenance", "field_publications",
        "field_locationname", "field_on_display", "field_whole_part", "field_legal_status", "path"]
for num in sys.argv[1:]:
    data = None
    for attempt in range(4):
        r = requests.get(B, params={"filter[field_number]": num}, headers=H, timeout=60)
        try:
            data = r.json().get("data", []); break
        except ValueError:
            print(f"# {num}: HTTP {r.status_code}, retry {attempt+1}", file=sys.stderr); time.sleep(5 * (attempt + 1))
    if data is None:
        print(f"# {num}: FAILED", file=sys.stderr); continue
    if not data:
        print(f"# {num}: no record", file=sys.stderr)
    for x in data:
        a = x["attributes"]
        rec = {k: a.get(k) for k in KEEP}
        rec["url"] = "https://www.liverpoolmuseums.org.uk" + (a.get("path") or {}).get("alias", "")
        rec["jsonapi"] = f"{B}?filter[field_number]={num}"
        imgs = []
        rel = x["relationships"].get("field_image_object", {}).get("links", {}).get("related", {}).get("href")
        if rel:
            pdata = []
            for attempt in range(4):
                try:
                    pdata = requests.get(rel, headers=H, timeout=60).json().get("data", []); break
                except ValueError:
                    time.sleep(5 * (attempt + 1))
            for p in pdata:
                pa = p["attributes"]
                u = (pa.get("field_media_image_url") or "").replace("public://", "https://images.liverpoolmuseums.org.uk/")
                imgs.append({"url": u, "credit": pa.get("field_photography_credit_line")})
        rec["images"] = imgs
        print(json.dumps(rec, ensure_ascii=False))
    time.sleep(1)
