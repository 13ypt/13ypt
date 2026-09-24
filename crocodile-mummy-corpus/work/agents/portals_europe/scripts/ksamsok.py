#!/usr/bin/env python3
"""K-samsök (Swedish national heritage aggregator, frontend Kringla) helper.
  search:  python3 ksamsok.py search 'text="krokodil" AND text="mumie"'
  record:  python3 ksamsok.py record MM/objekt/21265
Search results -> ../raw/ksamsok_q_<slug>.json ; records -> ../raw/ksamsok_records.json
"""
import json, os, re, sys, time
import requests
from lxml import etree
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
API = "https://kulturarvsdata.se/ksamsok/api"
NS = {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "k": "http://kulturarvsdata.se/ksamsok#",
      "pres": "http://kulturarvsdata.se/presentation#"}


def text_all(el, path):
    return [re.sub(r"\s+", " ", "".join(x.itertext())).strip() for x in el.xpath(path, namespaces=NS)]


def parse_entity(root):
    ent = root.xpath("//k:Entity", namespaces=NS)
    if not ent:
        return None
    e = ent[0]
    rec = {"uri": e.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about")}
    rec["url"] = text_all(e, "k:url")
    rec["org"] = text_all(e, "k:serviceOrganizationFull")
    rec["label"] = text_all(e, "k:itemLabel")
    rec["keywords"] = text_all(e, "k:itemKeyWord")
    rec["idLabel"] = text_all(root, "//pres:idLabel")
    rec["numbers"] = text_all(root, "//k:ItemNumber/k:number") or text_all(root, "//k:number")
    rec["descriptions"] = [d[:600] for d in text_all(root, "//k:ItemDescription/k:desc")]
    rec["names"] = text_all(root, "//k:ItemName/k:name")
    rec["licence"] = [x.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource") for x in e.xpath("k:itemLicenseUrl|k:itemLicense", namespaces=NS)]
    rec["images"] = text_all(root, "//k:Image/k:highresSource") or text_all(root, "//k:Image/k:lowresSource")
    rec["image_licence"] = [x.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource") for x in root.xpath("//k:Image/k:mediaLicenseUrl|//k:Image/k:mediaLicense", namespaces=NS)]
    rec["measurements"] = text_all(root, "//k:ItemMeasurement")
    rec["contexts"] = text_all(root, "//k:Context")[:6]
    return rec


def record(ref):
    r = requests.get(f"https://kulturarvsdata.se/{ref}", headers={"Accept": "application/rdf+xml"}, timeout=90)
    root = etree.fromstring(r.content)
    return parse_entity(root)


def search(q, hits=100):
    out, start, total = [], 1, None
    while True:
        params = {"method": "search", "query": q, "hitsPerPage": hits, "startRecord": start,
                  "recordSchema": "presentation"}
        r = requests.get(API, params=params, timeout=120, headers={"Accept": "application/xml"})
        root = etree.fromstring(r.content)
        tot = root.xpath("//totalHits/text()")
        total = int(tot[0]) if tot else 0
        recs = root.xpath("//record")
        for rc in recs:
            pr = etree.tostring(rc, encoding="unicode")
            ent = {
                "uri": (re.findall(r"<pres:entityUri>([^<]+)", pr) or [None])[0],
                "org": (re.findall(r"<pres:organization[^>]*>([^<]+)", pr) or [None])[0],
                "label": (re.findall(r"<pres:itemLabel[^>]*>([^<]+)", pr) or [None])[0],
                "idLabel": (re.findall(r"<pres:idLabel>([^<]+)", pr) or [None])[0],
                "type": (re.findall(r"<pres:type[^>]*>([^<]+)", pr) or [None])[0],
                "desc": [d[:300] for d in re.findall(r"<pres:description[^>]*>([^<]+)", pr)][:3],
            }
            out.append(ent)
        start += hits
        if start > total or not recs or start > 3000:
            break
        time.sleep(1)
    return {"query": q, "total": total, "items": out}


if __name__ == "__main__":
    if sys.argv[1] == "record":
        p = os.path.join(RAW, "ksamsok_records.json")
        store = json.load(open(p)) if os.path.exists(p) else {}
        for ref in sys.argv[2:]:
            store[ref] = record(ref)
            print(json.dumps(store[ref], ensure_ascii=False, indent=0))
            time.sleep(1)
        json.dump(store, open(p, "w"), ensure_ascii=False, indent=1)
    else:
        for q in sys.argv[2:]:
            res = search(q)
            slug = re.sub(r"[^a-z0-9]+", "_", q.lower()).strip("_")[:60]
            json.dump(res, open(os.path.join(RAW, f"ksamsok_q_{slug}.json"), "w"), ensure_ascii=False, indent=0)
            print(f"{q!r}: total={res['total']} fetched={len(res['items'])}")
