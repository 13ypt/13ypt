#!/usr/bin/env python3
"""Compute every number quoted in REPORT.md directly from the master CSVs and render
docs/REPORT_template.md -> REPORT.md, so the report can never disagree with the data.

Placeholders: {{NAME}} for scalars, {{TABLE:name}} for generated Markdown tables.
"""
import csv
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = "UNKNOWN"

REGIONS = [
    ("Egypt", {"EG"}),
    ("United Kingdom", {"GB"}),
    ("Ireland", {"IE"}),
    ("France", {"FR", "MC"}),
    ("Germany", {"DE"}),
    ("Italy (incl. Vatican, San Marino, Malta)", {"IT", "VA", "SM", "MT"}),
    ("Austria", {"AT"}),
    ("Switzerland (incl. Liechtenstein)", {"CH", "LI"}),
    ("Netherlands", {"NL"}),
    ("Belgium & Luxembourg", {"BE", "LU"}),
    ("Iberia (Spain, Portugal, Andorra)", {"ES", "PT", "AD"}),
    ("Scandinavia & Nordic (DK, SE, NO, FI, IS)", {"DK", "SE", "NO", "FI", "IS", "FO", "GL"}),
    ("Central / Eastern Europe, Baltics, Balkans, Greece, Cyprus, Turkey, Russia",
     {"PL", "CZ", "SK", "HU", "RO", "MD", "BG", "SI", "HR", "BA", "RS", "ME", "MK", "XK", "AL",
      "GR", "CY", "TR", "UA", "BY", "RU", "GE", "AM", "AZ", "EE", "LV", "LT"}),
    ("United States", {"US", "PR"}),
    ("Canada", {"CA"}),
    ("Australia / New Zealand", {"AU", "NZ"}),
    ("Japan", {"JP"}),
]
OPEN_LICENCE = re.compile(
    r"public\s*domain|\bcc0\b|creativecommons\.org/(publicdomain|licenses/by(-sa)?/)|"
    r"\bcc[\s-]?by(?![\s-]?nc)(?![\s-]?nd)|open access|domaine public|pdm", re.I)


def region_of(cc):
    for name, codes in REGIONS:
        if cc in codes:
            return name
    return "Other countries worldwide"


def load(name):
    path = os.path.join(ROOT, name)
    return list(csv.DictReader(open(path, encoding="utf-8"))) if os.path.exists(path) else []


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def is_open(lic):
    if not lic or lic == U:
        return False
    if re.search(r"\bnc\b|non-?commercial|\bnd\b|no deriv|all rights reserved", lic, re.I):
        return bool(re.search(r"public\s*domain|\bcc0\b", lic, re.I))
    return bool(OPEN_LICENCE.search(lic))


def compute():
    inst = load("institutions_master.csv")
    objs = load("objects_master.csv")
    noconf = load("searched_no_confirmation.csv")
    logs = load("search_log.csv")
    bib = load("bibliography.csv")
    leads = load("work/leads_status.csv")
    S, T = {}, {}

    conf = Counter(r["confidence"] for r in inst)
    S["N_INST"] = len(inst)
    S["N_INST_CONFIRMED"] = conf["CONFIRMED"]
    S["N_INST_PROBABLE"] = conf["PROBABLE"]
    S["N_INST_UNVERIFIED"] = conf["UNVERIFIED"]
    S["N_COUNTRIES_CONFIRMED"] = len({r["country"] for r in inst if r["confidence"] == "CONFIRMED"})
    S["N_NOCONF"] = len(noconf)
    S["N_QUERIES"] = len(logs)
    S["N_BIB"] = len(bib)
    S["N_LEADS_OPEN"] = sum(1 for l in leads if l["resolution"] == "OPEN")

    # A. by region and by country
    reg = defaultdict(Counter)
    for r in inst:
        reg[region_of(r["country"])][r["confidence"]] += 1
    nc_reg = Counter(region_of(r["country"]) for r in noconf)
    obj_reg = defaultdict(Counter)
    for o in objs:
        obj_reg[region_of(o["x_country"])][o["confidence"]] += 1
    rows = []
    for name, _ in REGIONS + [("Other countries worldwide", set())]:
        c = reg.get(name, Counter())
        rows.append([name, c["CONFIRMED"], c["PROBABLE"], c["UNVERIFIED"], nc_reg.get(name, 0),
                     obj_reg[name]["CONFIRMED"], sum(obj_reg[name].values())])
    T["region"] = md_table(["Region", "CONFIRMED inst.", "PROBABLE inst.", "UNVERIFIED inst.",
                            "Checked, not confirmed", "CONFIRMED objects", "All object rows"], rows)
    bycc = defaultdict(Counter)
    for r in inst:
        bycc[r["country"]][r["confidence"]] += 1
    T["country"] = md_table(
        ["Country", "CONFIRMED", "PROBABLE", "UNVERIFIED"],
        [[cc, c["CONFIRMED"], c["PROBABLE"], c["UNVERIFIED"]]
         for cc, c in sorted(bycc.items(), key=lambda kv: (-kv[1]["CONFIRMED"], kv[0]))])

    # B. objects
    oc = Counter(o["confidence"] for o in objs)
    S["N_OBJ"] = len(objs)
    S["N_OBJ_CONFIRMED"] = oc["CONFIRMED"]
    S["N_OBJ_PROBABLE"] = oc["PROBABLE"]
    S["N_OBJ_UNVERIFIED"] = oc["UNVERIFIED"]
    S["SUM_MIN_CONFIRMED"] = sum(int(r["minimum_confirmed_objects"] or 0) for r in inst)
    S["N_INST_STATED_EXCEEDS_ROWS"] = sum(
        1 for r in inst if int(r["minimum_confirmed_objects"] or 0) > int(r["x_object_rows_confirmed"] or 0))
    cls = defaultdict(Counter)
    for o in objs:
        cls[o["classification"]][o["confidence"]] += 1
    labels = {"A": "Whole / substantially complete", "B": "Bundle with crocodilian remains",
              "C": "Largely unwrapped", "D": "Partial", "E": "Container / coffin / mask only",
              "F": "Uncertain"}
    T["classification"] = md_table(
        ["Class", "Meaning", "CONFIRMED", "PROBABLE", "UNVERIFIED", "Total"],
        [[k, labels[k], cls[k]["CONFIRMED"], cls[k]["PROBABLE"], cls[k]["UNVERIFIED"],
          sum(cls[k].values())] for k in "ABCDEF"])
    with_img = [o for o in objs if o["image_urls"] not in ("", U)]
    S["N_OBJ_IMG"] = len(with_img)
    S["N_OBJ_IMG_CONFIRMED"] = sum(1 for o in with_img if o["confidence"] == "CONFIRMED")
    S["N_OBJ_IMG_AB"] = sum(1 for o in with_img if o["classification"] in "AB")
    for part in ("head", "dorsal", "tail"):
        c = Counter(o[f"{part}_visible"] for o in objs)
        S[f"N_{part.upper()}_YES"] = c["YES"]
        S[f"N_{part.upper()}_NO"] = c["NO"]
        S[f"N_{part.upper()}_UNKNOWN"] = c[U]
    S["N_ALL3_YES"] = sum(1 for o in objs if o["head_visible"] == o["dorsal_visible"] == o["tail_visible"] == "YES")
    S["N_OBJ_OPEN_IMG"] = sum(1 for o in with_img if is_open(o["image_license"]))

    # C. digital access
    def inst_list(pred):
        return sorted(f"{r['museum']} ({r['country']})" for r in inst
                      if r["confidence"] in ("CONFIRMED", "PROBABLE") and pred(r))
    api = inst_list(lambda r: r["api_available"] == "YES")
    iiif = inst_list(lambda r: r["iiif_available"] == "YES")
    open_inst = sorted({f"{o['museum']} ({o['x_country']})" for o in with_img if is_open(o["image_license"])})
    S["N_INST_API"], S["N_INST_IIIF"], S["N_INST_OPEN"] = len(api), len(iiif), len(open_inst)
    T["api"] = "\n".join(f"- {x}" for x in api) or "- none recorded"
    T["iiif"] = "\n".join(f"- {x}" for x in iiif) or "- none recorded"
    T["open"] = "\n".join(f"- {x}" for x in open_inst) or "- none recorded"

    # F. usefulness ranking for the wrapping study
    score = defaultdict(lambda: Counter())
    for o in objs:
        if o["confidence"] != "CONFIRMED":
            continue
        k = (o["institution_id"], o["museum"], o["x_country"])
        score[k]["objects"] += 1
        if o["classification"] in "AB":
            score[k]["AB"] += 1
            if o["image_urls"] not in ("", U):
                score[k]["AB_img"] += 1
                if is_open(o["image_license"]):
                    score[k]["AB_open"] += 1
    ranked = sorted(score.items(), key=lambda kv: (-kv[1]["AB_img"], -kv[1]["AB"], kv[0][1]))
    T["useful"] = md_table(
        ["Institution", "ID", "Country", "CONFIRMED objects", "A/B", "A/B with online images",
         "…of which open licence"],
        [[k[1], k[0], k[2], c["objects"], c["AB"], c["AB_img"], c["AB_open"]]
         for k, c in ranked if c["AB"] > 0][:40])

    # E. unresolved
    T["probable"] = md_table(
        ["ID", "Institution", "Country", "Evidence", "Notes"],
        [[r["institution_id"], r["museum"], r["country"], r["evidence_type"],
          (r["notes"][:160] + "…") if len(r["notes"]) > 160 else r["notes"]]
         for r in inst if r["confidence"] == "PROBABLE"])
    T["unverified"] = md_table(
        ["ID", "Institution", "Country", "Evidence"],
        [[r["institution_id"], r["museum"], r["country"], r["evidence_type"]]
         for r in inst if r["confidence"] == "UNVERIFIED"])
    T["no_online_db"] = md_table(
        ["Institution", "Country", "Result", "Detail"],
        [[r["museum"], r["country"], r["result_category"],
          (r["result_detail"][:140] + "…") if len(r["result_detail"]) > 140 else r["result_detail"]]
         for r in noconf if re.search(r"NO_ONLINE_DB|DB_BLOCKED", r["result_category"])])
    T["confirmed_list"] = md_table(
        ["ID", "Institution", "City", "Country", "Min. objects", "Object rows (confirmed)"],
        [[r["institution_id"], r["museum"], r["city"], r["country"], r["minimum_confirmed_objects"],
          r["x_object_rows_confirmed"]] for r in inst if r["confidence"] == "CONFIRMED"])
    langs = Counter(r["language"] for r in logs)
    T["languages"] = md_table(["Language", "Logged queries"], langs.most_common())
    return S, T


def render():
    S, T = compute()
    tpl_path = os.path.join(ROOT, "docs", "REPORT_template.md")
    tpl = open(tpl_path, encoding="utf-8").read()
    missing = set()

    def sub(m):
        key = m.group(1)
        if key.startswith("TABLE:"):
            name = key[6:]
            if name in T:
                return T[name]
        elif key in S:
            return str(S[key])
        missing.add(key)
        return m.group(0)

    out = re.sub(r"\{\{([A-Za-z0-9_:]+)\}\}", sub, tpl)
    if missing:
        raise SystemExit(f"unknown placeholders: {sorted(missing)}")
    open(os.path.join(ROOT, "REPORT.md"), "w", encoding="utf-8").write(out)
    for k, v in sorted(S.items()):
        print(f"{k} = {v}")


if __name__ == "__main__":
    render() if os.path.exists(os.path.join(ROOT, "docs", "REPORT_template.md")) else \
        [print(f"{k} = {v}") for k, v in sorted(compute()[0].items())]
