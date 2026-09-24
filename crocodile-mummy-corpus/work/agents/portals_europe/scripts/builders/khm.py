#!/usr/bin/env python3
"""Build KHM Vienna crocodile-mummy object records from raw/khm_pages.json + raw/europeana_records.json."""
import json, os, re
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "raw")
k = json.load(open(os.path.join(RAW, "khm_pages.json")))
e = json.load(open(os.path.join(RAW, "europeana_records.json")))
OBJ = {  # khm id: (europeana id or None, english title, class, whole, wrap, basis/notes)
 "324028": ("/15502/AE_INV_264", "Crocodile", "C", "WHOLE", "NO", "image viewed (portals_europe): unwrapped adult crocodile, head, body and tail present; type 'Tiermumie'"),
 "324029": ("/15502/AE_INV_265", "Crocodile", "A", "WHOLE", "PARTIAL", "image viewed (portals_europe): complete crocodile with linen remains over body, head exposed; type 'Tiermumie'"),
 "316270": ("/15502/AE_INV_266", "Great crocodile", "A", "WHOLE", "YES", "image viewed (portals_europe): complete crocodile wrapped with criss-cross linen bands, snout exposed; type 'Tiermumie'"),
 "324030": (None, "Small crocodile mummy", "A", "WHOLE", "YES", "image viewed (portals_europe): wrapped crocodile-shaped bundle (label '266a'); contents not stated"),
 "324031": (None, "Small crocodile mummy", "A", "WHOLE", "YES", "image viewed (portals_europe): wrapped crocodile-shaped bundle with modelled head (label '266b'); contents not stated"),
 "319134": ("/15502/AE_INV_266c", "Crocodile eggs", "F", "UNKNOWN", "PARTIAL", "EGG: title 'Krokodilseier', material 'Leinen, Krokodilseier'; image viewed: many egg shells on/in linen"),
 "324057": ("/15502/AE_INV_290", "Mummified body of a small crocodile", "C", "WHOLE", "NO", "image viewed (portals_europe): unwrapped small crocodile, head-body-tail present; material 'Mumie'"),
 "324059": ("/15502/AE_INV_292", "Mummy of a small crocodile", "A", "WHOLE", "YES", "image viewed (portals_europe): linen-wrapped small crocodile-shaped mummy; material 'Mumie, Leinen'"),
}
for kid, (eid, en, cl, wh, wr, basis) in OBJ.items():
    v = k[kid]; L = v["lines"]
    after = lambda lab: L[L.index(lab)+1] if lab in L else "UNKNOWN"
    i = L.index("Inv. Nr.")
    inv = L[i+1]
    acq = L[i+2] if ("erworben" in L[i+2] or "Bestand" in L[i+2]) else "UNKNOWN"
    mat = after("Material/Technik:")
    if mat == "Maße:": mat = "UNKNOWN"
    dims = after("Maße:")
    length = "UNKNOWN"
    m = re.search(r"(?:^|, )L (ca\. )?([\d,]+ cm)", dims)
    if m: length = (m.group(1) or "") + m.group(2)
    urls = [v["url"]]
    if eid: urls.append("https://www.europeana.eu/item" + eid)
    imgs = [x for x in v["images"] if "/pics/" in x]
    rec = {
      "museum": "Kunsthistorisches Museum Vienna", "city": "Vienna", "country": "AT",
      "inventory_number": inv.replace("Ägyptische Sammlung, ", ""),
      "other_numbers": f"as printed on KHM page: '{inv}'" + (f"; Europeana dc:identifier {eid.split('/')[-1]}" if eid else "") + f"; KHM object id {kid}",
      "object_title_original": v["h1"], "object_title_english": en,
      "classification": cl, "classification_basis": basis,
      "provenance": after("Fundort:"),
      "acquisition": acq,
      "date_period": L[3],
      "length": length, "other_dimensions": dims,
      "description": f"Objekttyp: Tiermumie; Material/Technik: {mat}",
      "whole_or_partial": wh, "wrapping_present": wr,
      "online_record_url": " ; ".join(urls),
      "image_urls": " ; ".join(imgs) or "UNKNOWN",
      "image_count": "UNKNOWN",
      "image_license": "KHM page 'Bildrecht: Kunsthistorisches Museum, Ägyptisch - Orientalische Sammlung'" + ("; Europeana edm:rights http://creativecommons.org/licenses/by-nc-sa/4.0/ (dc:rights 'CC BY-NC-SA 4.0')" if eid else "; not in Europeana"),
      "api_or_iiif": (f"Europeana Record API https://api.europeana.eu/record/v2{eid}.json ; IIIF (Europeana-generated) https://iiif.europeana.eu/presentation{eid}/manifest" if eid else "none found (not in Europeana)"),
      "source_of_identification": ("Europeana Search API sweep (Kulturpool dataset 15502) confirmed on KHM online collection" if eid else "KHM online collection 'related objects' list on INV 292 page (found while verifying Europeana hit); not in Europeana"),
      "evidence_type": "OFFICIAL_DB;NATIONAL_PORTAL;IIIF" if eid else "OFFICIAL_DB",
      "confidence": "CONFIRMED",
      "notes": "Old Europeana link http://www.khm.at/de/objektdb/detail/%s/ redirects to %s." % (kid, v["url"]),
    }
    print(json.dumps(rec, ensure_ascii=False))
