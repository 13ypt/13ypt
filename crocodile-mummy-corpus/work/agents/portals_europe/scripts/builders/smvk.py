#!/usr/bin/env python3
"""Build object records for Medelhavsmuseet (SMVK) from raw Carlotta + Europeana extracts."""
import json, os
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "raw")
c = json.load(open(os.path.join(RAW, "carlotta_collections_smvk_se_carlotta_mhm.json")))
e = json.load(open(os.path.join(RAW, "europeana_records.json")))
CLS = {  # objid: (classification, whole, wrapping, basis)
 "3011831": ("F","UNKNOWN","UNKNOWN","description only ('Mummified baby crocodile.'); wrapping/completeness not stated; photos not audited"),
 "3011834": ("A","WHOLE","YES","description 'A mummified baby crocodile wrapped in linen.'; photos not audited"),
 "3011845": ("F","UNKNOWN","YES","description 'A mummified baby crocodile wrapped in linen.' but catalogue keyword 'fragment'; photos not audited"),
 "3011846": ("D","PARTIAL","UNKNOWN","description 'Mummified head of a baby crocodile.'"),
 "3011847": ("B","UNKNOWN","YES","description 'A bunch of young crocodiles wrapped in linen.' (multiple individuals)"),
 "3011856": ("A","WHOLE","YES","description 'Mummified and wrapped. Baby crocodile.'; condition 'Head is loose.'"),
 "3011857": ("A","WHOLE","YES","description 'Mummified and wrapped. Baby crocodile.'"),
 "3011859": ("F","UNKNOWN","UNKNOWN","title keywords only ('mummy, crocodile, fragment'); no description"),
 "3015891": ("D","PARTIAL","UNKNOWN","description 'A mummified baby crocodile without head.'; condition 'The head is missing.'"),
 "3015895": ("F","PARTIAL","UNKNOWN","keywords 'mummy, fragment, crocodile'; comment: catalogue says 'pieces of a baby crocodile' but photo shows at least two baby crocodiles"),
 "3016253": ("C","PARTIAL","NO","description 'Mummified crocodile baby.'; linen wrapping removed 1983 (kept separately as MME 1983:013 B); condition 'Tip of the tail is missing.'"),
 "3016254": ("C","UNKNOWN","NO","description 'Mummified baby crocodile without linen wraps.'"),
 "3016255": ("C","UNKNOWN","NO","description 'A mummified baby crocodile. Without linen wrappings.'"),
 "3016256": ("F","UNKNOWN","UNKNOWN","description 'A mummified baby crocodile.' only"),
 "3016257": ("C","UNKNOWN","NO","description 'Mummified baby crocodile. Unwrapped.'"),
 "3016258": ("C","UNKNOWN","NO","description 'A mummified baby crocodile. Unwrapped.'"),
 "3016259": ("C","UNKNOWN","NO","description 'A mummified baby crocodile. Unwrapped.'"),
 "3016260": ("C","UNKNOWN","NO","description 'A mummified baby crocodile. Unwrapped.'"),
 "3016261": ("C","UNKNOWN","NO","description 'A mummified baby crocodile without linen wrappings.'"),
 "3016262": ("A","UNKNOWN","YES","description 'A mummified baby crocodile. Three splints made of palmleaves and linen wrappings.'"),
 "3016263": ("A","UNKNOWN","YES","description 'A mummified baby crocodile. Two splints made of palm leaves and linen wrappings. The head is loose.'"),
 "3016279": ("F","UNKNOWN","UNKNOWN","description 'A mummified baby crocodile.' only"),
}
for oid,(cl,wh,wr,basis) in CLS.items():
    r = c[oid]
    inv = r["Inventory number"][0]
    eu = e.get(f"/91639/SMVK_MM_objekt_{oid}", {})
    other = []
    for i in eu.get("dcIdentifier", []):
        v = i.split("] ",1)[1]
        if v != inv and not v.startswith("http") and v not in other:
            other.append(v)
    if oid == "3016253":
        other.append("linen wrapping kept separately as MME 1983:013 B (carlotta object 3011850)")
    dims = (r.get("Dimensions") or ["UNKNOWN"])[0]
    length = "UNKNOWN"
    if dims.startswith("L. "):
        length = dims.split(",")[0].replace("L. ","").rstrip(".")
    rec = {
      "museum": "Museum of Mediterranean and Near Eastern Antiquities (Medelhavsmuseet)",
      "city": "Stockholm", "country": "SE",
      "inventory_number": inv,
      "other_numbers": "; ".join(other) if other else "UNKNOWN",
      "object_title_original": r["heading"][2] if len(r.get("heading",[]))>2 else "UNKNOWN",
      "object_title_english": r["heading"][2] if len(r.get("heading",[]))>2 else "UNKNOWN",
      "classification": cl, "classification_basis": basis,
      "provenance": "Egypt (Country - Findspot: Egypt); no site given",
      "acquisition": (r.get("Acquisition") or ["UNKNOWN"])[0],
      "date_period": "UNKNOWN",
      "length": length,
      "other_dimensions": dims,
      "description": " | ".join(filter(None, [(r.get("Object description") or [""])[0], (r.get("Condition") or [""])[0], (r.get("Comments") or [""])[0]])) or "UNKNOWN",
      "whole_or_partial": wh, "wrapping_present": wr,
      "online_record_url": r["url"] + " ; " + f"https://www.europeana.eu/item/91639/SMVK_MM_objekt_{oid}",
      "image_urls": " ; ".join(r["images"][:3]) if r["images"] else "UNKNOWN",
      "image_count": str(len(r["images"])) + " image files linked on Carlotta record page",
      "image_license": "CC BY 4.0 (Carlotta record links https://creativecommons.org/licenses/by/4.0/; Europeana edm:rights http://creativecommons.org/licenses/by/4.0/)",
      "api_or_iiif": f"Europeana Record API https://api.europeana.eu/record/v2/91639/SMVK_MM_objekt_{oid}.json ; IIIF (Europeana-generated) https://iiif.europeana.eu/presentation/91639/SMVK_MM_objekt_{oid}/manifest ; K-samsök http://kulturarvsdata.se/SMVK-MM/objekt/{oid}",
      "source_of_identification": "Europeana Search API sweep (queries e.g. 'crocodile mummy', 'krokodilunge', 'mumifierad krokodil'); confirmed on Medelhavsmuseet Carlotta record",
      "evidence_type": "OFFICIAL_DB;NATIONAL_PORTAL;IIIF",
      "confidence": "CONFIRMED",
      "notes": f"Also in Europeana older dataset as /91644/SMVK_MM_Egypt_{oid}. Record states X-rayed at Karolinska Sjukhuset 21 May 2012 where given. Found via portals_europe Europeana sweep.",
    }
    print(json.dumps(rec, ensure_ascii=False))
