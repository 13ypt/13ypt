# nordic_baltic — summary (stopped early on orchestrator WRAP-UP order)

## (a) Done
- Institutions: 5 CONFIRMED (Medelhavsmuseet Stockholm 22 obj; Malmö Museum 1; Bohusläns museum Uddevalla 2 [Manfalut 1850]; Univ. Museum Bergen 1; Nationalmuseet Copenhagen 12 records incl. Kom Ombo & el-Maabda), 1 PROBABLE (KHM Oslo UEM3648, origin 'unknown place').
- Objects: 39 rows. No_confirmation: 3 (Helsingborg, Kulturen Lund, Etnografiska). Leads: 10.
- Sources fully run: Europeana API; K-samsök API (all Swedish orgs); DigitaltMuseum Solr+artifact API (SE+NO); Carlotta MHM + Malmö; Natmus objectbrowse API.
- WebSearch budget exhausted at start (0 web searches run) — only institutional DBs/APIs used.
- head/dorsal/tail_visible left UNKNOWN; photos viewed are noted in classification_basis.

## (b) NOT YET SEARCHED
- DK: Glyptotek, NHMD, Museernes Samlinger, Moesgaard, Thorvaldsen.
- SE: Gustavianum/Victoriamuseet, NRM, Östergötlands museum own DB, Göteborg Världskultur/Naturhistoriska.
- FI (Finna), IS (Sarpur), EE/LV/LT portals (MuIS etc.), GBIF natural-history specimens, literature (CT/X-ray study of SMVK crocodiles, Karolinska 2012).

## (c) Resume with
- https://api.finna.fi/v1/search?lookfor=krokotiili+muumio (also 'krokodiili', 'muumio')
- https://www.muis.ee/ search 'krokodill muumia'
- https://api.gbif.org/v1/occurrence/search?taxonKey=11493978&publishingCountry=DK|SE|NO|FI&q=mummy|mumie
- DiMu: q='mumie AND identifier.owner:S-ÖM'; natmus: api/objectbrowse?keyword=dyremumie (AS 7464 unspecified)
- Scripts: work/agents/nordic_baltic/scripts/{ksamsok_parse,dimu_search,carlotta_search,natmus,build_mm_objects}.py
