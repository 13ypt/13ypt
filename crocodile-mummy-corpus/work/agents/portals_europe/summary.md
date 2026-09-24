# portals_europe — summary (2026-09-24, stopped early on orchestrator WRAP-UP)

**Output:** 13 institutions (12 CONFIRMED, 1 PROBABLE), 50 objects, 85 search_log rows, 4 leads.
Scripts are in `scripts/` (europeana_sweep.py, europeana_records.py, ksamsok.py, digitaltmuseum_sweep.py,
collectienederland_sweep.py, carlotta_extract.py, khm_extract.py, builders/*). Raw JSON is in `raw/`.

## (a) Done (portal × query → crocodile-mummy hits)
| Portal | Queries | Hits / relevant |
|---|---|---|
| Europeana API | 53 queries (the 21 assigned + 32 extra: AND-forms in de/fr/it/es/pt/pl/cs/hu/sv/da/fi/el/ru/hr/ro, Sobek/Souchos/Suchos, Kom Ombo, Tebtunis, Crocodilopolis, Manfalut, Fayum) | 67 relevant records → SMVK Stockholm 22, KHM Vienna 6, RMO Leiden 6, Brussels 3, Cluj 2, Museon, MAN Madrid, SKD Dresden, Kestner Hannover, Bohuslän, Malmö |
| K-samsök/Kringla (SE) | 9 queries | only SMVK, Malmö, Bohuslän (no new) |
| DigitaltMuseum DiMu API (SE+NO) | 17 queries | NEW: KHM Oslo UEM3648; Bergen (photos only); Bohuslän |
| Collectie Nederland | 3 of 13 queries | RMO AMM 16h (not in Europeana); rest were rate-limited |
| Provider pages | SMVK Carlotta (24 pp.), KHM (8 pp., found INV 266a/266b outside Europeana), DiMu | verified |

Findings in brief: zero hits for the it/es/pl/cs/hu/el/ru exact phrases. Europeana concept expansion of "Mumie" returns the same set. NME 793 (SMVK) is a snake, not a crocodile. Brussels E.00453 is an ancient pseudo-mummy.

## (b) NOT YET SEARCHED
- Provider pages still to check: RMO (403), Museon, CERES/MAN, Clasate, Carmentis, SKD, museum-digital. Their values come from the Europeana Record API only.
- Deutsche Digitale Bibliothek; museum-digital (all instances); bavarikon.
- POP/Joconde and data.culture.gouv.fr.
- Carmentis and erfgoedplus searches.
- catalogo.beniculturali.it, CulturaItalia, Lombardia BC.
- CERES/Hispana searches, MatrizNet.
- Finna, Danish Samlinger Online, eSbírky, Polish/Hungarian portals, Goskatalog.
- Museum Data Service (UK); Google Arts & Culture.
- Collectie Nederland: 10 queries remain (see search_log).

## (c) Resume
- `python3 scripts/collectienederland_sweep.py "krokodil" "Sobek" ...`: the API rate-limits, so use OAI-PMH instead (`/api/oai-pmh?verb=ListRecords&metadataPrefix=edm`).
- Finna: `https://api.finna.fi/v1/search?lookfor=krokotiili+muumio`
- museum-digital: `https://global.museum-digital.org/json/objects?s=Krokodil` (endpoint not yet checked)
- POP: `https://pop.culture.gouv.fr/search/list?base=["Collections des musées de France (Joconde)"]&mainSearch="momie crocodile"`
- CERES: `http://ceres.mcu.es/pages/SimpleSearch?index=true` with the term "cocodrilo"
- Any new Europeana term: `python3 scripts/europeana_sweep.py "<q>"`, then run `europeana_records.py`.

Saturation: this was **not** reached, because most national portals are still unsearched.
