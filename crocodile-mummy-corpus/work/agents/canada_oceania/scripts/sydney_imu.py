#!/usr/bin/env python3
"""Query the University of Sydney museums (Chau Chak Wing Museum) KE EMu/IMu web
service behind https://www.sydney.edu.au/museums/collections_search/ .

The public web client POSTs JSON to imu/request.php; this script uses the same
calls (Module findKey/findTerms + fetch). Throttled to ~1 req/s.
Usage: python3 sydney_imu.py probe <irn>            # test which columns are readable
       python3 sydney_imu.py get <irn> [<irn> ...]
       python3 sydney_imu.py find <column> <term>
"""
import json
import sys
import time
import requests

URL = "https://www.sydney.edu.au/museums/collections_search/imu/request.php"
S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0", "Content-Type": "text/json"})
PORT = None

CANDIDATE_COLS = [
    "irn", "SummaryData", "TitMainTitle", "TitAccessionNo", "TitObjectName",
    "TitObjectStatement", "TitTitleNotes", "PhyDescription", "PhyMediumComments",
    "PhyMedium", "CreDateCreated", "CreDateCreatedComments", "CreCreationPeriod",
    "ProPlace", "ProStateProvince", "ProCountry", "AcqCreditLine", "AcqHistoricalNote",
    "AccAccessionLotRef", "DesDescription", "DesPhysicalDescription", "NotNotes",
    "PhyHeight", "PhyWidth", "PhyDepth", "PhyLength", "PhyUnitLength", "PhyDiameter",
    "TitCollectionGroup", "CatDiscipline", "CatDepartment", "ObjObjectName",
    "CreCulture", "CrePlace", "CreCountry", "CreDateCreatedComment", "MulMultiMediaRef",
    "EdiLabelDescription", "LabDescription", "CreDescription", "PhyMaterials",
    "PhyMediaCategory", "CreCreatorLocal_tab", "TitObjectType", "PhyMaterial_tab",
    "CreProvenance", "ProvenanceNotes", "TitPreviousAccessionNo_tab", "PhyObjectDimensions",
    "IdeTypeStatus", "IdeTaxonRef_tab", "WebDescription", "SumDescription",
]


def post(data):
    global PORT
    time.sleep(1.0)
    if PORT and "port" not in data:
        data["port"] = PORT
    r = S.post(URL, data=json.dumps(data), timeout=60)
    try:
        j = r.json()
    except ValueError:
        return {"error": f"HTTP {r.status_code} non-JSON"}
    PORT = j.get("port", PORT)
    return j


def handle_for_key(irn):
    j = post({"request": "Module", "table": "ecatalogue", "method": "findKey",
              "params": {"key": int(irn)}})
    return j.get("id")


def fetch(hid, cols, count=1, offset=0):
    return post({"request": "Module", "table": "ecatalogue", "id": hid, "method": "fetch",
                 "params": {"flag": "start", "offset": offset, "count": count,
                            "columns": cols}})


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "probe":
        hid = handle_for_key(sys.argv[2])
        ok = []
        for c in CANDIDATE_COLS:
            j = fetch(hid, ["irn", c])
            if "result" in j and isinstance(j["result"], dict):
                row = j["result"]["rows"][0]
                if c in row:
                    ok.append(c)
                    print(c, "=>", json.dumps(row[c], ensure_ascii=False)[:300])
            else:
                hid = handle_for_key(sys.argv[2])
        print("READABLE:", ok)
    elif mode == "get":
        cols = sys.argv[2].split(",")
        for irn in sys.argv[3:]:
            hid = handle_for_key(irn)
            j = fetch(hid, cols)
            print(json.dumps({"irn": irn, "result": j.get("result", j)}, ensure_ascii=False))
    elif mode == "find":
        col, term = sys.argv[2], sys.argv[3]
        cols = sys.argv[4].split(",") if len(sys.argv) > 4 else ["irn"]
        j = post({"request": "Module", "table": "ecatalogue", "method": "findTerms",
                  "params": {"terms": ["and", [[col, term]]]}})
        hid = j.get("id")
        hits = j.get("result")
        print(json.dumps({"find": [col, term], "hits": hits}), flush=True)
        if isinstance(hits, int) and hits > 0:
            off = 0
            while off < hits:
                r = fetch(hid, cols, count=50, offset=off)
                if "result" not in r:
                    print(json.dumps(r)); break
                for row in r["result"]["rows"]:
                    print(json.dumps(row, ensure_ascii=False))
                off += 50
