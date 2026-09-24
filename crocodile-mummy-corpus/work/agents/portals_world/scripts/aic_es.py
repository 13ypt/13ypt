"""Art Institute of Chicago: exact Elasticsearch query_string searches (the plain ?q= search
returns total=133118 for every query because it scores all records, so totals are useless).
POST https://api.artic.edu/api/v1/artworks/search with {"query":{"query_string":{...}}}."""
import json, time, requests
from common import save_raw
QS = ['(crocodile OR Sobek OR crocodil*) AND mumm*', 'crocodile', 'Sobek',
      'mumm* AND place_of_origin:Egypt', 'animal AND mumm*']
out = {}
for qs in QS:
    body = {"query": {"query_string": {"query": qs}}, "limit": 100,
            "fields": ["id", "title", "main_reference_number", "place_of_origin", "artwork_type_title"]}
    r = requests.post("https://api.artic.edu/api/v1/artworks/search", json=body, timeout=60)
    d = r.json()
    out[qs] = {"total": d["pagination"]["total"],
               "rows": [(x["main_reference_number"], x["title"], x["place_of_origin"]) for x in d["data"]]}
    time.sleep(1.1)
save_raw("aic_es_results.json", out)
print(json.dumps({k: v["total"] for k, v in out.items()}))
