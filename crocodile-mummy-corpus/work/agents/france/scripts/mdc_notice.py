#!/usr/bin/env python3
"""Fetch Musée des Confluences portal notices and parse label/value fields.
Usage: mdc_notice.py noticeIDs_file out.jsonl   (one 'noticeNNN' per line, first column)
Politeness: 1.2 s between requests."""
import re, html, sys, subprocess, time, json
LABELS = ["Numéro d'inventaire", "Origine", "Domaine", "Parcours", "Identification", "Appellation", "Dénomination",
          "Préparation", "Identification scientifique", "Découverte", "Provenance géographique", "Lieu de découverte",
          "Lieu de collecte", "Description", "Époque - Datation", "Précision sur la datation", "Matières", "Techniques",
          "Dimensions", "Historique", "Acquisition", "Mode d'acquisition", "Date d'acquisition", "Ancienne appartenance",
          "Collecteur", "Donateur", "Ancien propriétaire", "Inscriptions", "Bibliographie", "Expositions", "Mention obligatoire",
          "Date de découverte", "Commentaire", "Auteur", "Aire culturelle", "Typologie", "Nom scientifique", "Sexe", "Âge",
          "Etat de conservation", "Remarques", "Personnes et institutions liées", "Observations", "Exposition"]
done = set()
try:
    for l in open(sys.argv[2]): done.add(json.loads(l)["notice"])
except FileNotFoundError: pass
out = open(sys.argv[2], "a")
ids = [l.split("\t")[0].strip() for l in open(sys.argv[1]) if l.startswith("notice")]
for nid in ids:
    if nid in done: continue
    url = f"https://portail.museedesconfluences.fr/{nid}"
    t = subprocess.run(["curl", "-sSL", "-A", "Mozilla/5.0", url], capture_output=True, text=True).stdout
    img = re.findall(r'https://portail\.museedesconfluences\.fr/IMG/base/notices/[^"\']+\.jpg', t)
    title = re.search(r'<title>([^<]*)', t)
    t2 = re.sub(r'<script.*?</script>', '', t, flags=re.S); t2 = re.sub(r'<style.*?</style>', '', t2, flags=re.S)
    t2 = re.sub(r'<[^>]+>', '\n', t2)
    lines = [html.unescape(l.strip()) for l in t2.split('\n') if l.strip()]
    s = next((n for n, l in enumerate(lines) if l == "Numéro d'inventaire"), None)
    e = next((n for n, l in enumerate(lines) if l.startswith("Télécharger la photo") or l.startswith("Vous avez des informations") or l.startswith("Have information")), len(lines))
    rec = {"notice": nid, "url": url, "title": html.unescape(title.group(1)) if title else "", "images": sorted(set(img)), "fields": {}, "unparsed": []}
    cur = None
    for l in lines[s:e] if s is not None else []:
        if l in LABELS: cur = l; rec["fields"].setdefault(cur, []); continue
        if cur: rec["fields"][cur].append(l)
        else: rec["unparsed"].append(l)
    if s is None: rec["unparsed"] = lines[:40]
    out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
    time.sleep(1.2)
