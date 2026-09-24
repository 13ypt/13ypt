#!/usr/bin/env python3
"""Fetch Penn Museum object pages (collections.penn.museum) for crocodile-mummy candidates
selected from Penn_Museum_Collections_Data.csv and extract labelled fields."""
import json, re, sys, time, requests
hits = json.load(open(sys.argv[1]))
extra = {"E12571", "29-65-563", "E2832", "97-121-12", "2003-34-1A", "2003-34-1B"}
sel = [r for r in hits if r["objectName"].startswith("Mummy,Crocodile") or r["identifier"] in extra]
LABELS = ["Object Number","Current Location","Culture","Provenience","Period","Date Made","Section","Materials","Iconography","Description","Height","Length","Width","Depth","Diameter","Credit Line","Other Number"]
out = []
for r in sel:
    url = r["Record URL"]
    h = None
    for attempt in range(4):
        try:
            h = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}, timeout=30).text
            break
        except requests.RequestException:
            time.sleep(5 * (attempt + 1))
    if h is None:
        out.append({"url": url, "csv_identifier": r["identifier"], "error": "fetch failed"})
        continue
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    d = {"url": url, "csv_identifier": r["identifier"]}
    try:
        s = lines.index("Details")
    except ValueError:
        s = 0
    for i in range(s, len(lines) - 1):
        if lines[i] in LABELS and lines[i] not in d:
            d[lines[i]] = lines[i + 1]
    m = re.search(r"View All \((\d+)\) Object Images", h)
    d["image_count"] = m.group(1) if m else ("1" if re.search(r"/collections/assets/[^\"]+_800\.jpg", h) else "0")
    d["images"] = sorted(set("https://collections.penn.museum" + x for x in re.findall(r"(/collections/assets/[^\"]+_800\.jpg)", h)))
    try:
        e = lines.index("Current &amp; Past Exhibitions")
        b = lines.index("Bibliography", e)
        d["exhibitions"] = " | ".join(lines[e + 1:b])
        f = lines.index("Report problems and issues to", b)
        d["bibliography"] = " | ".join(lines[b + 1:f])
    except ValueError:
        pass
    out.append(d)
    time.sleep(1)
json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
