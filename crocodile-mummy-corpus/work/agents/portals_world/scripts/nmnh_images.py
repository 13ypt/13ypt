"""Build and verify Smithsonian IDS image URLs (ark:/65665/m3<muluu>) for NMNH candidate records.
Uses curl's default User-Agent style (the IDS WAF rejects a bare 'Mozilla/5.0')."""
import json, time, requests
from common import RAW, save_raw
c = json.load(open(f"{RAW}/nmnh_candidates_full.json"))
out = {}
for k, r in c.items():
    rows = []
    for m in r.get("mulmm", []):
        u = "https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3" + m["muluu"]
        time.sleep(1.1)
        resp = requests.get(u, headers={"User-Agent": "curl/8.5.0"}, timeout=60, stream=True)
        rows.append({"url": u, "status": resp.status_code, "type": resp.headers.get("content-type"),
                     "mulid": m.get("mulid"), "desc": m.get("mulds"), "rights": m.get("detrs"),
                     "rights_statement": m.get("detrg"), "creator": m.get("mulcr")})
        resp.close()
    out[r.get("catbc")] = rows
save_raw("nmnh_image_check.json", out)
for k, v in out.items():
    print(k, len(v), [(x["status"], x["type"]) for x in v])
