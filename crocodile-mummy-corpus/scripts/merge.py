#!/usr/bin/env python3
"""Merge the agents' JSONL working files into the corpus master tables.

Inputs : work/agents/<agent>/{institutions,objects,search_log,no_confirmation,
         bibliography,leads}.jsonl
         work/institution_aliases.csv   (curated: alias -> canonical institution)
         work/object_merges.csv         (curated: object records judged identical)
         work/overrides.csv             (curated: field corrections after verification)
         work/ids.json                  (persistent identifier registry)
Outputs: institutions_master.csv, objects_master.csv, search_log.csv,
         searched_no_confirmation.csv, bibliography.csv, work/leads_status.csv,
         work/merge_qa.txt

Rules (see README.md):
- Institutions are keyed by normalised name + country after alias mapping.
- Objects are keyed by institution + normalised inventory number. Records without an
  inventory number are never merged automatically; possible duplicates are flagged.
- When several records describe one object, non-UNKNOWN values are combined; differing
  values are all kept and marked "CONFLICT" in x_conflicts.
- Institution confidence = highest level supported by institution or object records.
- minimum_confirmed_objects = max(number of CONFIRMED object rows, largest numeric
  stated_count from a CONFIRMED-level institution record).
"""
import csv
import glob
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
RANK = {"CONFIRMED": 3, "PROBABLE": 2, "UNVERIFIED": 1}
U = "UNKNOWN"

INST_COLS = [
    "institution_id", "museum", "city", "country", "official_collection_url",
    "crocodile_mummies_confirmed", "minimum_confirmed_objects",
    "possible_additional_holdings", "inventory_numbers_known", "evidence_type",
    "evidence_urls", "scholarly_catalogue", "online_images", "image_license",
    "api_available", "iiif_available", "confidence", "date_checked", "notes",
    # extra columns (not in the original specification) for traceability
    "x_museum_original_name", "x_object_rows", "x_object_rows_confirmed",
    "x_stated_counts", "x_api_url", "x_iiif_url", "x_agents",
]
OBJ_COLS = [
    "object_id", "institution_id", "museum", "inventory_number",
    "object_title_original", "object_title_english", "classification",
    "species_if_given", "provenance", "date_period", "length", "width",
    "other_dimensions", "description", "whole_or_partial", "wrapping_present",
    "head_visible", "dorsal_visible", "tail_visible", "online_record_url",
    "image_urls", "image_count", "image_license", "api_or_iiif", "bibliography",
    "source_of_identification", "confidence", "notes",
    "x_country", "x_city", "x_other_numbers", "x_classification_basis",
    "x_acquisition", "x_evidence_type", "x_possible_duplicate_of", "x_conflicts",
    "x_date_checked", "x_agents",
]
LOG_COLS = ["date", "country", "language", "database_or_search_engine", "query",
            "institution_checked", "result", "notes", "x_agent"]
NOCONF_COLS = ["museum", "city", "country", "official_collection_url", "result_category",
               "result_detail", "sources_checked", "queries", "date_checked", "notes",
               "x_agents"]
BIB_COLS = ["citation", "year", "type", "doi_or_url", "access", "institutions_mentioned",
            "objects_mentioned", "relevance", "notes", "x_agents"]
LEAD_COLS = ["museum", "city", "country", "lead_source", "lead_detail",
             "source_reliability", "resolution", "x_agents"]


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm_name(s):
    s = strip_accents(s or "").lower()
    s = s.replace("&", " and ").replace("’", "'")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^a-z0-9؀-ۿ぀-ヿ一-鿿]+", " ", s)
    s = re.sub(r"^(the|le|la|les|il|lo|el|het|de|der|die|das)\s+", "", s.strip())
    return re.sub(r"\s+", " ", s).strip()


def norm_inv(s):
    s = strip_accents(s or "").lower().strip()
    if s in ("", "unknown", "none", "n/a", "unnumbered"):
        return ""
    s = re.sub(r"^(inv(entory)?|acc(ession)?|no|nr|n°|cat)\.?\s*(no\.?|nr\.?|number)?\s*[:.]?\s*", "", s)
    return re.sub(r"[\s.\-_/,:;]+", "", s)


def load_jsonl(kind):
    rows = []
    for path in sorted(glob.glob(os.path.join(WORK, "agents", "*", f"{kind}.jsonl"))):
        with open(path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"WARN bad JSON {path}:{n}", file=sys.stderr)
    return rows


def load_csv(name):
    path = os.path.join(WORK, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if not (r.get(next(iter(r)), "") or "").startswith("#")]


def split_multi(v):
    if not v or v == U:
        return []
    return [p.strip() for p in re.split(r"\s*(?:;|\|)\s+|\s*;\s*", v) if p.strip() and p.strip() != U]


def union(values, sep="; "):
    seen, out = set(), []
    for v in values:
        for p in split_multi(v):
            k = p.lower()
            if k not in seen:
                seen.add(k)
                out.append(p)
    return sep.join(out) if out else U


def join_text(values, sep=" | "):
    seen, out = set(), []
    for v in values:
        if v and v != U and v.strip().lower() not in seen:
            seen.add(v.strip().lower())
            out.append(v.strip())
    return sep.join(out) if out else U


class Aliases:
    def __init__(self):
        self.map = {}
        for r in load_csv("institution_aliases.csv"):
            key = (norm_name(r["alias"]), r["country"].strip())
            self.map[key] = (r["canonical"].strip(), r.get("canonical_city", "").strip(),
                             r.get("canonical_country", "").strip() or r["country"].strip())

    def resolve(self, museum, city, country):
        hit = self.map.get((norm_name(museum), country))
        if hit:
            name, ccity, ccountry = hit
            return name, (ccity or city), ccountry
        return museum.strip(), city, country


def inst_key(name, country):
    return f"{country}|{norm_name(name)}"


def main():
    aliases = Aliases()
    ids_path = os.path.join(WORK, "ids.json")
    ids = json.load(open(ids_path)) if os.path.exists(ids_path) else {"inst": {}, "obj": {}}
    overrides = load_csv("overrides.csv")  # object_key_or_id, field, value, reason
    merges = load_csv("object_merges.csv")  # keep_key, drop_key, reason
    qa = []

    inst_recs = load_jsonl("institutions")
    obj_recs = load_jsonl("objects")

    # ---------- institutions ----------
    inst_groups = defaultdict(list)
    names_seen = defaultdict(Counter)
    cities_seen = defaultdict(Counter)
    for r in inst_recs:
        name, city, country = aliases.resolve(r["museum"], r["city"], r["country"])
        k = inst_key(name, country)
        r["_name"], r["_city"], r["_country"] = name, city, country
        inst_groups[k].append(r)
        names_seen[k][name] += 1
        if city != U:
            cities_seen[k][city] += 1
    for r in obj_recs:
        name, city, country = aliases.resolve(r["museum"], r["city"], r["country"])
        k = inst_key(name, country)
        r["_name"], r["_city"], r["_country"], r["_ikey"] = name, city, country, k
        names_seen[k][name] += 1
        if city != U:
            cities_seen[k][city] += 1
        inst_groups.setdefault(k, [])

    # ---------- objects ----------
    merge_map = {m["drop_key"].strip(): m["keep_key"].strip() for m in merges}
    obj_groups = defaultdict(list)
    for r in obj_recs:
        inv = norm_inv(r["inventory_number"])
        if inv:
            ok = f"{r['_ikey']}#{inv}"
        else:
            # no inventory number: never auto-merged; key must stay stable between runs
            basis = "|".join([r.get("_agent", ""), r.get("_recorded", ""),
                              r.get("online_record_url", ""), r.get("object_title_original", ""),
                              r.get("provenance", ""), r.get("length", ""),
                              r.get("description", "")[:200]])
            ok = f"{r['_ikey']}#~" + stable_digest(basis)
        ok = merge_map.get(ok, ok)
        r["_okey"] = ok
        obj_groups[ok].append(r)

    obj_rows = []
    for ok, recs in obj_groups.items():
        recs.sort(key=lambda x: (-RANK[x["confidence"]], x.get("_agent", "")))
        row, conflicts = {}, []

        def pick(field, multi=False):
            vals = [x.get(field, U) for x in recs]
            if multi:
                return union(vals)
            distinct = []
            for v in vals:
                if v and v != U and v.strip().lower() not in [d.lower() for d in distinct]:
                    distinct.append(v.strip())
            if len(distinct) > 1 and field in {"length", "width", "classification", "provenance",
                                                "date_period", "species_if_given", "image_license",
                                                "whole_or_partial", "wrapping_present"}:
                conflicts.append(f"{field}: " + " / ".join(
                    f"{x.get(field)} [{x.get('_agent')}]" for x in recs if x.get(field, U) != U))
            return distinct[0] if distinct else U

        ikey = recs[0]["_ikey"]
        row["museum"] = names_seen[ikey].most_common(1)[0][0]
        row["inventory_number"] = pick("inventory_number")
        for f in ["object_title_original", "object_title_english", "classification",
                  "species_if_given", "provenance", "date_period", "length", "width",
                  "other_dimensions", "description", "whole_or_partial", "wrapping_present",
                  "head_visible", "dorsal_visible", "tail_visible", "image_count",
                  "image_license"]:
            row[f] = pick(f)
        if row["classification"] == U:
            row["classification"] = "F"
        row["online_record_url"] = union([x.get("online_record_url", U) for x in recs])
        row["image_urls"] = union([x.get("image_urls", U) for x in recs])
        row["api_or_iiif"] = union([x.get("api_or_iiif", U) for x in recs])
        row["bibliography"] = join_text([x.get("bibliography", U) for x in recs])
        row["source_of_identification"] = join_text(
            [f"{x.get('source_of_identification')} [{x.get('_agent')}]" for x in recs])
        row["confidence"] = recs[0]["confidence"]
        row["notes"] = join_text([x.get("notes", U) for x in recs])
        row["x_country"] = recs[0]["_country"]
        row["x_city"] = cities_seen[ikey].most_common(1)[0][0] if cities_seen[ikey] else U
        row["x_other_numbers"] = union([x.get("other_numbers", U) for x in recs])
        row["x_classification_basis"] = join_text([x.get("classification_basis", U) for x in recs])
        row["x_acquisition"] = join_text([x.get("acquisition", U) for x in recs])
        row["x_evidence_type"] = union([x.get("evidence_type", U) for x in recs])
        row["x_possible_duplicate_of"] = join_text([x.get("possible_duplicate_of", U) for x in recs])
        row["x_conflicts"] = " || ".join(conflicts) if conflicts else ""
        row["x_date_checked"] = max(x.get("date_checked", U) for x in recs)
        row["x_agents"] = ";".join(sorted({x.get("_agent", "") for x in recs}))
        row["_okey"], row["_ikey"] = ok, ikey
        obj_rows.append(row)

    # ---------- build institution rows ----------
    inst_rows = []
    objs_by_inst = defaultdict(list)
    for o in obj_rows:
        objs_by_inst[o["_ikey"]].append(o)
    for k, recs in inst_groups.items():
        objs = objs_by_inst.get(k, [])
        levels = [RANK[r["confidence"]] for r in recs] + [RANK[o["confidence"]] for o in objs]
        if not levels:
            continue
        conf = {3: "CONFIRMED", 2: "PROBABLE", 1: "UNVERIFIED"}[max(levels)]
        n_conf = sum(1 for o in objs if o["confidence"] == "CONFIRMED")
        stated = []
        for r in recs:
            sc = str(r.get("stated_count", U)).strip()
            if sc != U:
                stated.append(f"{sc} ({r.get('stated_count_source', U)}) [{r['_agent']}]")
        stated_conf = [int(m.group()) for r in recs if r["confidence"] == "CONFIRMED"
                       for m in [re.match(r"^\d+", str(r.get("stated_count", "")).strip())] if m]
        minimum = max([n_conf] + stated_conf) if conf == "CONFIRMED" else 0
        if conf == "CONFIRMED" and minimum == 0:
            qa.append(f"CONFIRMED institution without confirmed object rows or stated count: {k}")
            minimum = 1

        def ynu(field):
            vals = {r.get(field, U) for r in recs}
            if field == "online_images" and any(o.get("image_urls", U) != U for o in objs):
                vals.add("YES")
            return "YES" if "YES" in vals else ("NO" if "NO" in vals else U)

        inv_known = union([r.get("inventory_numbers_known", U) for r in recs] +
                          [o["inventory_number"] for o in objs])
        row = {
            "museum": names_seen[k].most_common(1)[0][0],
            "city": cities_seen[k].most_common(1)[0][0] if cities_seen[k] else U,
            "country": k.split("|")[0],
            "official_collection_url": union([r.get("official_collection_url", U) for r in recs]),
            "crocodile_mummies_confirmed": "YES" if conf == "CONFIRMED" else "NO",
            "minimum_confirmed_objects": minimum,
            "possible_additional_holdings": join_text(
                [r.get("possible_additional_holdings", U) for r in recs]),
            "inventory_numbers_known": inv_known,
            "evidence_type": union([r.get("evidence_type", U) for r in recs] +
                                   [o["x_evidence_type"] for o in objs]),
            "evidence_urls": union([r.get("evidence_urls", U) for r in recs] +
                                   [o["online_record_url"] for o in objs if o["confidence"] == "CONFIRMED"]),
            "scholarly_catalogue": join_text([r.get("scholarly_catalogue", U) for r in recs]),
            "online_images": ynu("online_images"),
            "image_license": join_text([r.get("image_license", U) for r in recs] +
                                       [o["image_license"] for o in objs]),
            "api_available": ynu("api_available"),
            "iiif_available": ynu("iiif_available"),
            "confidence": conf,
            "date_checked": max([r.get("date_checked", U) for r in recs] +
                                [o["x_date_checked"] for o in objs]),
            "notes": join_text([r.get("notes", U) for r in recs]),
            "x_museum_original_name": union([r.get("museum_original_name", U) for r in recs]),
            "x_object_rows": len(objs),
            "x_object_rows_confirmed": n_conf,
            "x_stated_counts": " | ".join(stated) if stated else U,
            "x_api_url": union([r.get("api_url", U) for r in recs]),
            "x_iiif_url": union([r.get("iiif_url", U) for r in recs]),
            "x_agents": ";".join(sorted({r["_agent"] for r in recs} |
                                        {a for o in objs for a in o["x_agents"].split(";")})),
            "_key": k,
        }
        inst_rows.append(row)

    # ---------- persistent IDs ----------
    inst_rows.sort(key=lambda r: (r["country"], norm_name(r["museum"])))
    counters = Counter()
    for iid in ids["inst"].values():
        cc = iid.split("-")[1]
        counters[cc] = max(counters[cc], int(iid.split("-")[2]))
    for r in inst_rows:
        if r["_key"] not in ids["inst"]:
            cc = r["country"]
            counters[cc] += 1
            ids["inst"][r["_key"]] = f"INST-{cc}-{counters[cc]:03d}"
        r["institution_id"] = ids["inst"][r["_key"]]
    inst_id = {r["_key"]: r["institution_id"] for r in inst_rows}
    obj_counter = Counter()
    for oid in ids["obj"].values():
        base, n = oid.rsplit("-O", 1)
        obj_counter[base] = max(obj_counter[base], int(n))
    obj_rows.sort(key=lambda r: (inst_id[r["_ikey"]], r["inventory_number"]))
    for r in obj_rows:
        iid = inst_id[r["_ikey"]]
        if r["_okey"] not in ids["obj"]:
            obj_counter[iid] += 1
            ids["obj"][r["_okey"]] = f"{iid}-O{obj_counter[iid]:03d}"
        r["object_id"] = ids["obj"][r["_okey"]]
        r["institution_id"] = iid

    # ---------- curated overrides ----------
    by_oid = {r["object_id"]: r for r in obj_rows}
    by_iid = {r["institution_id"]: r for r in inst_rows}
    for ov in overrides:
        target = by_oid.get(ov["id"]) or by_iid.get(ov["id"])
        if target is None:
            qa.append(f"override target not found: {ov['id']}")
            continue
        target[ov["field"]] = ov["value"]
        tag = f"[corrected {ov['field']}: {ov['reason']}]"
        target["notes"] = tag if target.get("notes", U) == U else f"{target['notes']} {tag}"

    # ---------- QA: possible duplicates / near-duplicate institution names ----------
    by_inst = defaultdict(list)
    for r in obj_rows:
        by_inst[r["institution_id"]].append(r)
    for iid, objs in by_inst.items():
        unnum = [o for o in objs if norm_inv(o["inventory_number"]) == ""]
        if unnum and len(objs) > 1:
            qa.append(f"{iid}: {len(unnum)} object(s) without inventory number among {len(objs)} "
                      f"— check duplicates: {[o['object_id'] for o in unnum]}")
    keys = sorted(inst_groups)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a.split("|")[0] != b.split("|")[0]:
                continue
            na, nb = a.split("|")[1], b.split("|")[1]
            if SequenceMatcher(None, na, nb).ratio() > 0.82 or (len(na) > 6 and (na in nb or nb in na)):
                qa.append(f"POSSIBLE SAME INSTITUTION: '{a}' ~ '{b}'")

    # ---------- no-confirmation (exclude institutions that are in the master) ----------
    master_keys = set(inst_id)
    nc_groups = defaultdict(list)
    for r in load_jsonl("no_confirmation"):
        name, city, country = aliases.resolve(r["museum"], r["city"], r["country"])
        nc_groups[inst_key(name, country)].append((name, city, country, r))
    nc_rows = []
    for k, items in sorted(nc_groups.items()):
        if k in master_keys:
            iid = inst_id[k]
            note = (f"Also checked without confirmation by {sorted({x[3]['_agent'] for x in items})}; "
                    f"see {iid}")
            qa.append(f"no_confirmation superseded by master: {k} -> {iid}")
            continue
        name, city, country, _ = items[0]
        recs = [x[3] for x in items]
        nc_rows.append({
            "museum": name, "city": city, "country": country,
            "official_collection_url": union([r.get("official_collection_url", U) for r in recs]),
            "result_category": union([r["result_category"] for r in recs]),
            "result_detail": join_text([r["result_detail"] for r in recs]),
            "sources_checked": union([r["sources_checked"] for r in recs]),
            "queries": join_text([r["queries"] for r in recs]),
            "date_checked": max(r.get("date_checked", U) for r in recs),
            "notes": join_text([r.get("notes", U) for r in recs]),
            "x_agents": ";".join(sorted({r["_agent"] for r in recs})),
        })

    # ---------- bibliography ----------
    bib = {}
    for r in load_jsonl("bibliography"):
        doi = re.search(r"10\.\d{4,9}/[^\s;|]+", r.get("doi_or_url", "") or "")
        k = doi.group().lower().rstrip(".") if doi else norm_name(r["citation"])[:120]
        if k in bib:
            b = bib[k]
            for f in ("institutions_mentioned", "objects_mentioned", "relevance", "notes"):
                b[f] = join_text([b[f], r.get(f, U)])
            order = ["CITATION_ONLY", "ABSTRACT", "PARTIAL_TEXT", "FULL_TEXT"]
            if order.index(r["access"]) > order.index(b["access"]):
                b["access"] = r["access"]
            b["x_agents"] = ";".join(sorted(set(b["x_agents"].split(";")) | {r["_agent"]}))
        else:
            bib[k] = {c: r.get(c, U) for c in BIB_COLS if c != "x_agents"}
            bib[k]["x_agents"] = r["_agent"]
    bib_rows = sorted(bib.values(), key=lambda b: (b["year"], b["citation"]))

    # ---------- leads ----------
    nc_keys = set(nc_groups)
    lead_rows = []
    lead_groups = defaultdict(list)
    for r in load_jsonl("leads"):
        name, city, country = aliases.resolve(r["museum"], r.get("city", U), r["country"])
        lead_groups[inst_key(name, country)].append((name, city, country, r))
    for k, items in sorted(lead_groups.items()):
        name, city, country, _ = items[0]
        recs = [x[3] for x in items]
        if k in master_keys:
            res = f"IN_MASTER {inst_id[k]}"
        elif k in nc_keys:
            res = "CHECKED_NO_CONFIRMATION"
        else:
            res = "OPEN"
        lead_rows.append({
            "museum": name, "city": city, "country": country,
            "lead_source": union([r["lead_source"] for r in recs]),
            "lead_detail": join_text([r["lead_detail"] for r in recs]),
            "source_reliability": union([r["source_reliability"] for r in recs]),
            "resolution": res,
            "x_agents": ";".join(sorted({r["_agent"] for r in recs})),
        })

    # ---------- search log ----------
    log_rows = []
    for r in load_jsonl("search_log"):
        row = {c: r.get(c, U) for c in LOG_COLS if c != "x_agent"}
        row["x_agent"] = r.get("_agent", U)
        row["_t"] = r.get("_recorded", "")
        log_rows.append(row)
    log_rows.sort(key=lambda r: (r["x_agent"], r["_t"]))

    # ---------- write ----------
    def write(path, cols, rows):
        with open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({c: r.get(c, U) for c in cols})

    write("institutions_master.csv", INST_COLS, inst_rows)
    write("objects_master.csv", OBJ_COLS, obj_rows)
    write("search_log.csv", LOG_COLS, log_rows)
    write("searched_no_confirmation.csv", NOCONF_COLS, nc_rows)
    write("bibliography.csv", BIB_COLS, bib_rows)
    write("work/leads_status.csv", LEAD_COLS, lead_rows)
    json.dump(ids, open(ids_path, "w"), indent=1, ensure_ascii=False, sort_keys=True)
    with open(os.path.join(WORK, "merge_qa.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(qa) + "\n")

    c = Counter(r["confidence"] for r in inst_rows)
    print(f"institutions: {len(inst_rows)} {dict(c)}")
    print(f"objects: {len(obj_rows)} {dict(Counter(r['confidence'] for r in obj_rows))}")
    print(f"no_confirmation: {len(nc_rows)}; bibliography: {len(bib_rows)}; "
          f"search_log: {len(log_rows)}; leads: {len(lead_rows)} "
          f"(open {sum(1 for l in lead_rows if l['resolution'] == 'OPEN')})")
    print(f"QA notes: {len(qa)} -> work/merge_qa.txt")


def stable_digest(s):
    import hashlib
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


if __name__ == "__main__":
    main()
