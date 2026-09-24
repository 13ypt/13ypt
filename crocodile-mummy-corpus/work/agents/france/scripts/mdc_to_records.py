#!/usr/bin/env python3
"""Convert parsed MdC notices (raw/mdc_notices.jsonl) to objects records (JSON lines on stdout) for rec.py.
Classification is from the official title (Appellation) unless noted; no photo inspection unless listed in PHOTO dict."""
import json, re, sys, os
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
SUB = ["Découvreur - Inventeur - Collecteur", "Date de collecte", "Informations", "Documentation", "Bibliothèque du musée",
       "Collection", "Numéro d'inventaire", "Origine", "Domaine", "Parcours", "Identification", "Appellation", "Dénomination",
       "Préparation", "Découverte", "Provenance géographique", "Description", "Époque - Datation", "Précision sur la datation",
       "Matières", "Dimensions", "Mention obligatoire", "Techniques", "Identification scientifique", "Lieu de découverte"]
PHOTO = {}  # inv -> (classification, basis, whole, wrapping) filled after visual checks
try:
    PHOTO = json.load(open(os.path.join(RAW, "mdc_photo_checks.json")))
except FileNotFoundError:
    pass

def resplit(fields):
    seq = []
    for k, v in fields.items():
        seq.append(k); seq.extend(v)
    out, cur = {}, None
    for x in seq:
        if x in SUB:
            cur = x; out.setdefault(cur, []); continue
        if cur: out[cur].append(x)
    return out

def classify(title):
    t = title.upper().replace("É", "E").replace("Ê", "E")
    if "SIMULACRE" in t: return "F", "WHOLE", "Official title 'SIMULACRE DE CROCODILE' (imitation) – possible pseudo-mummy", "PSEUDO-MUMMY? (title 'simulacre')"
    if "OEUF" in t and "AVEC" not in t: return "F", "UNKNOWN", "Official title (egg)", "EGG"
    if "EMBRYON" in t: return "F", "UNKNOWN", "Official title (embryo)", "EMBRYO"
    if "AMAS" in t: return "B", "UNKNOWN", "Official title 'amas de bébés crocodiles' (cluster of several hatchlings)", ""
    if any(w in t for w in ("TETE", "CRANE", "QUEUE", "FRAG", "PATTE", "DENT")):
        return "D", "PARTIAL", "Official title (body part / fragment)", ("TOOTH only" if "DENT" in t else "")
    return "F", "UNKNOWN", "Official title only (no description; photo not inspected)", ""

recs = [json.loads(l) for l in open(os.path.join(RAW, "mdc_notices.jsonl"))]
for r in recs:
    f = resplit(r["fields"])
    j = lambda k, sep=" ": sep.join(f.get(k, [])).strip()
    inv = j("Numéro d'inventaire")
    title = j("Appellation")
    if not inv or inv.startswith("42"): continue  # 42xxxxxx = modern herpetology specimens
    cls, whole, basis, flag = classify(title)
    wrapping = "UNKNOWN"
    if inv in PHOTO:
        p = PHOTO[inv]; cls, basis, whole, wrapping = p["classification"], p["basis"], p["whole"], p["wrapping"]
    prov = " / ".join(x for x in f.get("Provenance géographique", []) if x != "/")
    collector = j("Découvreur - Inventeur - Collecteur"); dcol = j("Date de collecte")
    if collector: prov += f"; collector: {collector}"
    if dcol: prov += f"; date de collecte: {dcol}"
    acq = j("Origine", "; "); coll = j("Collection", "; ")
    if coll: acq += f"; Collection: {coll}"
    date = j("Époque - Datation", "; ")
    if j("Précision sur la datation"): date += "; " + j("Précision sur la datation", "; ")
    dims = j("Dimensions", "; ")
    L = re.search(r"L\.\s*([\d.,]+ ?cm)", dims); P = re.search(r"P\.\s*([\d.,]+ ?cm)", dims)
    info = j("Informations", " ")
    desc_parts = [f"Dénomination: {j('Dénomination')}", f"Préparation: {j('Préparation')}"]
    if j("Matières", ", "): desc_parts.append("Matières: " + j("Matières", ", "))
    if j("Parcours"): desc_parts.append("Parcours (on display): " + " ".join(x for x in f["Parcours"] if x != "/"))
    if info: desc_parts.append("Informations: " + info)
    bib = j("Bibliothèque du musée", " ") or j("Documentation", " ")
    notes = []
    if flag: notes.append(flag)
    notes.append("MdC dimension convention is 'H. x L. x P.'; for elongated crocodiles the long axis may be given as P. (e.g. 90001391 'H. 25 cm x L. 266 cm x P. 32 cm' vs 90001372 'H. 6 cm x L. 9 cm x P. 85 cm'), so 'length' is left as printed in other_dimensions")
    rec = {
        "museum": "Musée des Confluences", "city": "Lyon", "country": "FR",
        "inventory_number": inv, "other_numbers": "MHNL " + inv + " (form used in publications)",
        "object_title_original": title, "classification": cls, "classification_basis": basis,
        "species_if_given": "UNKNOWN", "provenance": prov or "UNKNOWN", "acquisition": acq or "UNKNOWN",
        "date_period": date or "UNKNOWN", "other_dimensions": dims or "UNKNOWN",
        "description": "; ".join(desc_parts), "whole_or_partial": whole, "wrapping_present": wrapping,
        "online_record_url": r["url"], "image_urls": " ; ".join(r["images"]) or "UNKNOWN",
        "image_count": str(len(r["images"])), "image_license": j("Mention obligatoire") + " (portal: download for private non-commercial use; site links CC BY-NC-ND 4.0)" if r["images"] else "UNKNOWN",
        "api_or_iiif": "NO (HTML portal only)", "bibliography": bib or "UNKNOWN",
        "source_of_identification": "Musée des Confluences official collections portal (portail.museedesconfluences.fr)",
        "evidence_type": "OFFICIAL_DB", "confidence": "CONFIRMED", "notes": " | ".join(notes)}
    m = re.search(r"Crocodilus [Nn]iloticus", info)
    if m: rec["species_if_given"] = "Crocodilus niloticus (old label transcription)"
    if inv in PHOTO and cls in ("A", "C"):
        rec["head_visible"] = "YES"; rec["tail_visible"] = "YES"; rec["dorsal_visible"] = "UNKNOWN"
    EXTRA_BIB = {"90001591": "Porcier, Berruyer, Pasquali, Ikram, Berthet & Tafforeau 2019, J. Archaeological Science 110:105009 (synchrotron; Roman period, Kom Ombo; wild-hunted crocodile)",
                 "90001850": "Berruyer, Porcier & Tafforeau 2020, PLOS ONE 15(2):e0229140 (synchrotron; head 21.1 cm + body 40.4 cm, preserved length 55 cm; Esna or Kom Ombo per Lortet & Gaillard)"}
    if inv in EXTRA_BIB:
        rec["bibliography"] = (rec["bibliography"] + "; " if rec["bibliography"] != "UNKNOWN" else "") + EXTRA_BIB[inv]
        rec["evidence_type"] = "OFFICIAL_DB;PEER_REVIEWED"
    print(json.dumps(rec, ensure_ascii=False))
