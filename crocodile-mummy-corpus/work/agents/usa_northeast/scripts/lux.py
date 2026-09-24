#!/usr/bin/env python3
"""Query Yale LUX (lux.collections.yale.edu) item search and summarise each Linked Art object record."""
import json, sys, time, requests
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
def get(url, **kw):
    for a in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=60, **kw)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(3)
    return None
def summarise(o):
    names = [n.get("content") for n in o.get("identified_by", []) if n.get("type") == "Name"]
    ids = [n.get("content") for n in o.get("identified_by", []) if n.get("type") == "Identifier"]
    texts = [(",".join(c.get("_label", "") for c in (r.get("classified_as") or [])), r.get("content")) for r in o.get("referred_to_by", [])]
    member = [m.get("_label") or m.get("id") for m in o.get("member_of", [])]
    home = [h.get("id") for h in o.get("subject_of", [])]
    dims = [(d.get("_label") or ",".join(c.get("_label","") for c in d.get("classified_as",[])), d.get("value"), (d.get("unit") or {}).get("_label")) for d in o.get("dimension", [])]
    prod = o.get("produced_by", {})
    return {"id": o.get("id"), "label": o.get("_label"), "names": names, "identifiers": ids, "texts": texts, "member_of": member, "dims": dims,
            "produced_by": json.dumps(prod)[:600], "carried_out_by": json.dumps(o.get("current_owner", ""))[:300],
            "subject_of": json.dumps(o.get("subject_of", []))[:800], "representation": json.dumps(o.get("representation", []))[:300]}
out = []
for q in sys.argv[1:]:
    page = 1
    while True:
        d = get("https://lux.collections.yale.edu/api/search/item", params={"q": json.dumps({"text": q}), "page": page})
        if not d:
            break
        items = d.get("orderedItems", [])
        print(q, "page", page, "total", d.get("partOf", [{}])[0].get("totalItems"), file=sys.stderr)
        for it in items:
            o = get(it["id"])
            if o:
                s = summarise(o); s["query"] = q; out.append(s)
            time.sleep(0.7)
        if not d.get("next") or page >= 3:
            break
        page += 1
json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
