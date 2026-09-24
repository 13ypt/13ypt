# usa_midwest_west - summary (stopped early on orchestrator WRAP UP; not saturated)

## Done
- CONFIRMED institutions (4), 59 object rows:
  - Phoebe A. Hearst Museum of Anthropology (Berkeley): 22 rows (stated 19). Source: Blacklight JSON API `portal.hearstmuseum.berkeley.edu/catalog.json?q=crocodile` (HTML is WAF-blocked; JSON works with a browser User-Agent). Plus Berkeley News 2021, UC Berkeley Library Object Lessons (CT of 6-20100), Stanford CT page (5-513).
  - ISAC Museum, Univ. of Chicago: 34 rows E695–E728 (stated 33). Source: Solr JSON `isac-idb.uchicago.edu/solr/index.php?dataset=MC&q=crocodile`.
  - Rosicrucian Egyptian Museum: RC-1675, RC-2253. Source: PastPerfect API (POST `/api/search/keyword`, GET `/api/items/<id>`). Bought from Mia in 1958.
  - Field Museum: 1 row, no inventory number (official blog). The collections DB is blocked.
- No confirmation (7): AIC, Cleveland MA, Nelson-Atkins, Oberlin AMAM, Mia (deaccessioned to Rosicrucian), Bancroft/CTP (papyri only), Burke (UWBM:Herp:7021 is "mummified" but gives no locality).
- Scripts: `scripts/hearst_query.py`, `isac_query.py`, `fetchgrep.py`, `findcoll.py`. Raw data: `raw/`.

## NOT YET SEARCHED / blocked (all in leads.jsonl)
- Blocked: Kelsey (quod Cloudflare), Field Museum EMu, DIA, Toledo, FAMSF, SLAM, Cantor (login), DMNS (403); Museum of Us, Crocker and UMFA (guessed URLs, proxy 502).
- Entry point found but not searched: Spurlock (`/collections/search-collection/`), MAA Missouri, Children's Museum of Indianapolis, NHM LA (Hearst loan L.1186-701/702).
- Not started: about 38 other candidates, listed in the last leads row.
- Tools unavailable: WebSearch quota exhausted (200/200). OpenAlex rate-limited. DuckDuckGo, Bing, Brave and Mojeek are unusable from curl.

## Resume
- Rosicrucian: retry the keyword API with `"Top":"50"` for "mummy" (the call failed with Top=300).
- Burke: retry `arctos.database.museum/guid/UWBM:Herp:7021`.
- Kelsey, Field Museum and DIA need a real browser.
