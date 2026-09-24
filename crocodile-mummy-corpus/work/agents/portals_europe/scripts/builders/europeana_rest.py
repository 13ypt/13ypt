#!/usr/bin/env python3
"""Build object records for remaining Europeana-found institutions (portal evidence only;
provider pages not individually verified due to budget) + RMO AMM 16h from Collectie Nederland."""
import json, os
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "raw")
e = json.load(open(os.path.join(RAW, "europeana_records.json")))
def v(r, k):
    return " | ".join(x.split("] ", 1)[1] for x in r.get(k, []) or []) or "UNKNOWN"
M = {  # id: (museum, city, cc, inv, title_en, class, whole, wrap, basis, extra notes)
 "/2021606/resource_document_rijksmuseum_van_oudheden_AMM16a": ("National Museum of Antiquities (Rijksmuseum van Oudheden)", "Leiden", "NL", "AMM 16a", "mummy; reptile; crocodile; animal mummy", "A", "WHOLE", "YES", "portal description: wrapped large crocodile reinforced with plant stalks and wooden stick, 314 cm", ""),
 "/2021606/resource_document_rijksmuseum_van_oudheden_AMM16g": ("National Museum of Antiquities (Rijksmuseum van Oudheden)", "Leiden", "NL", "AMM 16g", "mummy; reptile; crocodile; animal mummy", "F", "UNKNOWN", "PARTIAL", "portal description (central body wrapped in linen; head much damaged) - completeness unclear", ""),
 "/2021606/resource_document_rijksmuseum_van_oudheden_AMM16i": ("National Museum of Antiquities (Rijksmuseum van Oudheden)", "Leiden", "NL", "AMM 16i", "mummy; reptile; crocodile; animal mummy", "A", "UNKNOWN", "PARTIAL", "portal description of gridded linen strips over back; wrapped crocodile", ""),
 "/2021606/resource_document_rijksmuseum_van_oudheden_AMM16k": ("National Museum of Antiquities (Rijksmuseum van Oudheden)", "Leiden", "NL", "AMM 16k", "mummy; reptile; crocodile; animal mummy", "A", "WHOLE", "YES", "portal description: animal wrapped in concentric bandages, tail curved left", ""),
 "/2021606/resource_document_rijksmuseum_van_oudheden_CI260": ("National Museum of Antiquities (Rijksmuseum van Oudheden)", "Leiden", "NL", "CI 260", "mummy; reptile; animal mummy; crocodile", "A", "UNKNOWN", "YES", "portal description: animal wrapped in cloth with papyrus-rind reinforcement", ""),
 "/2021606/resource_document_rijksmuseum_van_oudheden_F1998_11_3": ("National Museum of Antiquities (Rijksmuseum van Oudheden)", "Leiden", "NL", "F 1998/11.3", "mummy of a young crocodile", "A", "WHOLE", "YES", "portal description: young crocodile wrapped in unpainted linen, traces of painted eye", ""),
 "/2021657/resource_document_museon_8258": ("Museon-Omniversum", "The Hague", "NL", "8258", "crocodile mummy", "F", "UNKNOWN", "UNKNOWN", "portal description 'Een mummie van een jonge krokodil' only", ""),
 "/2022703/pages_Main_idt_51_inventary_15123_table_FMUS_museum_MAN": ("National Archaeological Museum of Spain", "Madrid", "ES", "15123", "Crocodile mummy", "A", "WHOLE", "YES", "CERES description: bandaged in lozenge pattern; X-ray shows remains of a small Nile crocodile, skull partly preserved", ""),
 "/2048047/Clasate_64ef45de9f2e40aeb9f6f79e2f231e85": ("National Museum of Transylvanian History", "Cluj-Napoca", "RO", "V 1681", "zoomorphic mummy (mummified crocodile hatchling)", "C", "WHOLE", "PARTIAL", "Clasate description: eviscerated hatchling, bandages removed, two linen strips remain", "Second Clasate record (8062b87c...) carries the SAME inventory number V 1681 but different length/description - possibly a second individual; see notes"),
 "/322/Museu_ProvidedCHO_Mus_es_Royaux_d_Art_et_d_Histoire_75238": ("Royal Museums of Art and History", "Brussels", "BE", "E.00453", "Mummy of a young crocodile", "F", "UNKNOWN", "YES", "PSEUDO-MUMMY: record says radiological studies show it is an ancient forgery made of an unidentified material", "Excavation Grenfell & Hunt 1901-1902, Fayum"),
 "/322/Museu_ProvidedCHO_Mus_es_Royaux_d_Art_et_d_Histoire_84095": ("Royal Museums of Art and History", "Brussels", "BE", "E.07092a", "Mummy of a young crocodile", "F", "UNKNOWN", "UNKNOWN", "title only", ""),
 "/322/Museu_ProvidedCHO_Mus_es_Royaux_d_Art_et_d_Histoire_84096": ("Royal Museums of Art and History", "Brussels", "BE", "E.07092b", "Mummy of a young crocodile", "F", "UNKNOWN", "UNKNOWN", "title only", ""),
 "/669/item_PAKHUFNRIOZHSSTBLWAQV37HLJHU5HXL": ("Dresden State Art Collections, Skulpturensammlung", "Dresden", "DE", "Aeg 736", "Crocodile mummy", "F", "UNKNOWN", "UNKNOWN", "title 'Krokodilmumie' + dimensions only", ""),
 "/714/item_COB2KDAXTU4JNOPGI4E2A226XPP2NW6D": ("Museum August Kestner", "Hanover", "DE", "2010 und 2911", "Two crocodile mummies", "F", "UNKNOWN", "UNKNOWN", "title 'Zwei Krokodilsmumien' (two objects a/b under one record)", "Record covers two mummies: a) L 19,6 cm, b) L 12,6 cm; inventory printed as '2010 und 2911' - split may be needed"),
}
for rid, (mus, city, cc, inv, en, cl, wh, wr, basis, extra) in M.items():
    r = e[rid]
    rec = {"museum": mus, "city": city, "country": cc, "inventory_number": inv,
      "other_numbers": "Europeana dc:identifier: " + v(r, "dcIdentifier"),
      "object_title_original": v(r, "dcTitle"), "object_title_english": en,
      "classification": cl, "classification_basis": basis,
      "provenance": v(r, "dctermsSpatial") if "Museon" not in mus else "Krokodilopolis (Arsinoë), Fayum (per description)",
      "date_period": v(r, "dctermsCreated") if r.get("dctermsCreated") else v(r, "dcDate"),
      "other_dimensions": v(r, "dctermsExtent"),
      "description": v(r, "dcDescription")[:1500],
      "whole_or_partial": wh, "wrapping_present": wr,
      "online_record_url": f"https://www.europeana.eu/item{rid} ; provider: {r.get('edmIsShownAt')}",
      "image_urls": r.get("edmIsShownBy") or "UNKNOWN",
      "image_license": "Europeana edm:rights " + v(r, "edmRights") + ("; dc:rights " + v(r, "dcRights") if r.get("dcRights") else ""),
      "api_or_iiif": f"Europeana Record API https://api.europeana.eu/record/v2{rid}.json ; IIIF (Europeana-generated) " + "; ".join(r.get("iiif", [])),
      "source_of_identification": "Europeana Search API sweep (portals_europe)",
      "evidence_type": "NATIONAL_PORTAL;IIIF", "confidence": "CONFIRMED",
      "notes": ("Provider page NOT individually verified (budget); values from Europeana Record API. " + extra).strip()}
    if "AMM16a" in rid: rec["length"] = "314 cm (extent 314 x 28,5 x 20,5 cm)"
    print(json.dumps(rec, ensure_ascii=False))
# Cluj second record, RMO AMM 16h from Collectie Nederland
r2 = e["/2048047/Clasate_8062b87c49e34ec5a883a119839c4e75"]
print(json.dumps({"museum": "National Museum of Transylvanian History", "city": "Cluj-Napoca", "country": "RO", "inventory_number": "V 1681 (second record)", "other_numbers": "Clasate k=8062b87c49e34ec5a883a119839c4e75; printed inventory 'V 1681 (număr de inventar)'", "object_title_original": "mumie zoomorfă", "object_title_english": "zoomorphic mummy (mummified crocodile hatchling)", "classification": "F", "classification_basis": "Clasate description: hatchling, eviscerated, 'Bandajele sunt degradate' (bandages degraded)", "date_period": v(r2, "dctermsCreated"), "length": "50 cm", "description": v(r2, "dcDescription"), "whole_or_partial": "UNKNOWN", "wrapping_present": "PARTIAL", "online_record_url": "https://www.europeana.eu/item/2048047/Clasate_8062b87c49e34ec5a883a119839c4e75 ; provider: https://clasate.cimec.ro/detaliu.asp?k=8062b87c49e34ec5a883a119839c4e75", "image_urls": r2.get("edmIsShownBy"), "image_license": "Europeana edm:rights http://creativecommons.org/licenses/by-sa/4.0/", "api_or_iiif": "IIIF (Europeana-generated) https://iiif.europeana.eu/presentation/2048047/Clasate_8062b87c49e34ec5a883a119839c4e75/manifest", "source_of_identification": "Europeana Search API ('crocodil AND mumie')", "evidence_type": "NATIONAL_PORTAL;IIIF", "confidence": "CONFIRMED", "possible_duplicate_of": "V 1681 (Clasate 64ef45de...) - same inventory number, length 508 mm vs 50 cm; may be same object classified twice or two individuals", "notes": "Provider page not individually verified (budget)."}, ensure_ascii=False))
cn = [it for f in ["cn_q_krokodil_mummie.json"] for it in json.load(open(os.path.join(RAW, f)))["items"] if it["identifier"][:1] == ["AMM 16h"]][0]
print(json.dumps({"museum": "National Museum of Antiquities (Rijksmuseum van Oudheden)", "city": "Leiden", "country": "NL", "inventory_number": "AMM 16h", "object_title_original": " | ".join(cn["type"]), "object_title_english": "mummy; reptile; crocodile; animal mummy", "classification": "F", "classification_basis": "portal type/description only", "other_dimensions": " | ".join(cn["extent"]) or "UNKNOWN", "description": " | ".join(cn["desc"])[:1000] or "UNKNOWN", "online_record_url": "Collectie Nederland doc " + cn["doc_id"] + " ; " + " ".join(cn["isShownAt"]), "image_urls": " ".join(cn["isShownBy"]) or "UNKNOWN", "image_license": " | ".join(cn["rights"]) or "UNKNOWN", "source_of_identification": "Collectie Nederland API query 'krokodil mummie' / 'krokodillenmummie' (not found in Europeana sweep)", "evidence_type": "NATIONAL_PORTAL", "confidence": "CONFIRMED", "notes": "RMO website returned 403 to curl and WebFetch; not verified on rmo.nl."}, ensure_ascii=False))
