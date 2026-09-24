#!/usr/bin/env python3
"""Append validated records to a research agent's JSONL working files.

Usage (one JSON object per stdin line; use a quoted heredoc to avoid shell expansion):

    python3 crocodile-mummy-corpus/scripts/rec.py <agent> <kind> <<'EOF'
    {"museum": "...", ...}
    EOF

kind: institutions | objects | search_log | no_confirmation | bibliography | leads

Missing optional fields are filled with "UNKNOWN". Unknown keys and invalid
controlled-vocabulary values are rejected, so every agent writes the same schema.
"""
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()

CONFIDENCE = {"CONFIRMED", "PROBABLE", "UNVERIFIED"}
YNU = {"YES", "NO", "UNKNOWN"}
YNPU = {"YES", "NO", "PARTIAL", "UNKNOWN"}
EVIDENCE = {
    "OFFICIAL_DB", "OFFICIAL_API", "IIIF", "OFFICIAL_CATALOGUE", "OFFICIAL_WEBPAGE",
    "PEER_REVIEWED", "MONOGRAPH", "EXCAVATION_REPORT", "NATIONAL_PORTAL", "THESIS",
    "SECONDARY",
}
CLASSIFICATION = {"A", "B", "C", "D", "E", "F"}
WHOLE = {"WHOLE", "PARTIAL", "UNKNOWN"}
NOCONF = {
    "NO_CROCODILE_IN_ONLINE_DB", "NO_ONLINE_DB", "DB_BLOCKED_OR_UNAVAILABLE",
    "ONLY_OTHER_ANIMAL_MUMMIES", "ONLY_NON_MUMMY_CROCODILE_ITEMS",
    "NO_EGYPTIAN_COLLECTION", "OTHER",
}
BIBTYPE = {
    "PEER_REVIEWED", "MONOGRAPH", "MUSEUM_CATALOGUE", "EXCAVATION_REPORT", "THESIS",
    "CONFERENCE", "EDITED_VOLUME_CHAPTER", "OTHER",
}
ACCESS = {"FULL_TEXT", "PARTIAL_TEXT", "ABSTRACT", "CITATION_ONLY"}
RELIABILITY = {"SCHOLARLY", "OFFICIAL", "SECONDARY"}
LEADSTATUS = {"NOT_CHECKED", "OUT_OF_SCOPE", "CHECK_FAILED"}

# field -> (required, allowed set or None, multi-valued ';' list?)
SCHEMAS = {
    "institutions": {
        "museum": (True, None, False),
        "museum_original_name": (False, None, False),
        "city": (True, None, False),
        "country": (True, None, False),
        "official_collection_url": (False, None, False),
        "stated_count": (False, None, False),
        "stated_count_source": (False, None, False),
        "possible_additional_holdings": (False, None, False),
        "inventory_numbers_known": (False, None, False),
        "evidence_type": (True, EVIDENCE, True),
        "evidence_urls": (True, None, False),
        "scholarly_catalogue": (False, None, False),
        "online_images": (False, YNU, False),
        "image_license": (False, None, False),
        "api_available": (False, YNU, False),
        "api_url": (False, None, False),
        "iiif_available": (False, YNU, False),
        "iiif_url": (False, None, False),
        "confidence": (True, CONFIDENCE, False),
        "date_checked": (False, None, False),
        "notes": (False, None, False),
    },
    "objects": {
        "museum": (True, None, False),
        "city": (True, None, False),
        "country": (True, None, False),
        "inventory_number": (True, None, False),
        "other_numbers": (False, None, False),
        "object_title_original": (False, None, False),
        "object_title_english": (False, None, False),
        "classification": (True, CLASSIFICATION, False),
        "classification_basis": (True, None, False),
        "species_if_given": (False, None, False),
        "provenance": (False, None, False),
        "acquisition": (False, None, False),
        "date_period": (False, None, False),
        "length": (False, None, False),
        "width": (False, None, False),
        "other_dimensions": (False, None, False),
        "description": (False, None, False),
        "whole_or_partial": (False, WHOLE, False),
        "wrapping_present": (False, YNPU, False),
        "head_visible": (False, YNU, False),
        "dorsal_visible": (False, YNU, False),
        "tail_visible": (False, YNU, False),
        "online_record_url": (False, None, False),
        "image_urls": (False, None, False),
        "image_count": (False, None, False),
        "image_license": (False, None, False),
        "api_or_iiif": (False, None, False),
        "bibliography": (False, None, False),
        "source_of_identification": (True, None, False),
        "evidence_type": (True, EVIDENCE, True),
        "confidence": (True, CONFIDENCE, False),
        "possible_duplicate_of": (False, None, False),
        "date_checked": (False, None, False),
        "notes": (False, None, False),
    },
    "search_log": {
        "date": (False, None, False),
        "country": (True, None, False),
        "language": (True, None, False),
        "database_or_search_engine": (True, None, False),
        "query": (True, None, False),
        "institution_checked": (False, None, False),
        "result": (True, None, False),
        "notes": (False, None, False),
    },
    "no_confirmation": {
        "museum": (True, None, False),
        "city": (True, None, False),
        "country": (True, None, False),
        "official_collection_url": (False, None, False),
        "sources_checked": (True, None, False),
        "queries": (True, None, False),
        "result_category": (True, NOCONF, False),
        "result_detail": (True, None, False),
        "date_checked": (False, None, False),
        "notes": (False, None, False),
    },
    "bibliography": {
        "citation": (True, None, False),
        "year": (False, None, False),
        "type": (True, BIBTYPE, False),
        "doi_or_url": (False, None, False),
        "access": (True, ACCESS, False),
        "institutions_mentioned": (False, None, False),
        "objects_mentioned": (False, None, False),
        "relevance": (False, None, False),
        "notes": (False, None, False),
    },
    "leads": {
        "museum": (True, None, False),
        "city": (False, None, False),
        "country": (True, None, False),
        "lead_source": (True, None, False),
        "lead_detail": (True, None, False),
        "source_reliability": (True, RELIABILITY, False),
        "status": (True, LEADSTATUS, False),
        "notes": (False, None, False),
    },
}

DATE_FIELDS = {"date_checked", "date"}
FORBIDDEN_URL = re.compile(r"wiki(pedia|data|media)|\.wiki/|fandom\.com", re.I)


def validate(kind, rec):
    schema = SCHEMAS[kind]
    errors = []
    extra = set(rec) - set(schema)
    if extra:
        errors.append(f"unknown keys: {sorted(extra)}")
    out = {}
    for field, (required, allowed, multi) in schema.items():
        val = rec.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            if required:
                errors.append(f"missing required field '{field}'")
                continue
            val = TODAY if field in DATE_FIELDS else "UNKNOWN"
        if not isinstance(val, str):
            val = str(val)
        val = val.strip()
        if allowed is not None:
            parts = [p.strip() for p in val.split(";")] if multi else [val]
            bad = [p for p in parts if p not in allowed]
            if bad:
                errors.append(f"field '{field}' has invalid value(s) {bad}; allowed: {sorted(allowed)}")
        out[field] = val
    if "country" in out and not re.fullmatch(r"[A-Z]{2}|UNKNOWN", out["country"]):
        errors.append("country must be an ISO 3166-1 alpha-2 code, e.g. GB, FR, DE, US, EG")
    if out.get("country") in {"UK", "EN", "EL"}:
        errors.append("use ISO 3166-1 alpha-2: GB for the United Kingdom, GR for Greece")
    for field in ("evidence_urls", "online_record_url", "official_collection_url", "doi_or_url",
                  "lead_source", "sources_checked", "image_urls"):
        if field in out and FORBIDDEN_URL.search(out[field]):
            errors.append(f"field '{field}' cites a wiki source; wiki sources are not permitted")
    if kind == "institutions" and out.get("confidence") == "CONFIRMED":
        ev = set(out["evidence_type"].split(";"))
        if ev <= {"SECONDARY"}:
            errors.append("CONFIRMED requires non-SECONDARY evidence")
    if kind == "objects" and out.get("confidence") == "CONFIRMED":
        ev = set(p.strip() for p in out["evidence_type"].split(";"))
        if ev <= {"SECONDARY"}:
            errors.append("CONFIRMED requires non-SECONDARY evidence")
    return out, errors


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in SCHEMAS:
        sys.exit(__doc__)
    agent, kind = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[a-z0-9_]+", agent):
        sys.exit("agent name must match [a-z0-9_]+")
    outdir = os.path.join(ROOT, "work", "agents", agent)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{kind}.jsonl")
    ok, failed = 0, 0
    with open(path, "a", encoding="utf-8") as fh:
        for n, line in enumerate(sys.stdin, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"line {n}: invalid JSON: {exc}", file=sys.stderr)
                failed += 1
                continue
            out, errors = validate(kind, rec)
            if errors:
                print(f"line {n}: REJECTED: {'; '.join(errors)}", file=sys.stderr)
                failed += 1
                continue
            out["_agent"] = agent
            out["_recorded"] = datetime.datetime.now().isoformat(timespec="seconds")
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")
            ok += 1
    print(f"{kind}: {ok} written to {os.path.relpath(path, ROOT)}; {failed} rejected")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
