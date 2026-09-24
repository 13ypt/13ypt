# biodiversity agent – summary (stopped early on orchestrator WRAP UP)

## (a) Done
- Scripts: `scripts/nhm_portal_sweep.py`, `idigbio_sweep.py`, `gbif_sweep.py` (aborted), `gbif_media_fetch.py`, `querylog_to_searchlog.py`. Raw JSON in `raw/`.
- **NHM London Data Portal**: all crocodilian records (order/family/genus filters, ~3,500) plus 19 keyword queries. Result: 1977.448 'mummified'; 1976.290/.291 Hawara (Petrie) 'skull, partial skin' -> 3 objects, PROBABLE.
- **iDigBio**: every Crocodylidae/Alligatoridae/Gavialidae record (~42k) plus mummy/crocodile full-text queries. No new holders; the only Old World 'mummified' records are NHMUK 1977.448 and UWBM:Herp:7021 (lead).
- **GBIF**: count/facet queries; q=mummified/samoun/hawara/ombo/thebes within Crocodylia; all 18 MNHN Egyptian crocodilian records with verbatim data; images viewed through the GBIF image cache.
- **MNHN Paris**: CONFIRMED. 11 objects: RA 1986.1471-1474 (Thebes grottoes), 1986.1475-1478 and 1986.1480 (Samoun cave), 1901.214-215 (Kom Ombo, 'Comnunbo', Chantre).
- Totals: 2 institutions (1 CONFIRMED, 1 PROBABLE), 14 objects, 3 leads.

## Possible leads: Egyptian Crocodylus records with no sign of mummification (not recorded as objects)
- NHMUK: about 10 zoology specimens and about 100 fossil specimens (the fossils are Fayum Palaeogene). MNHN RA: 7. FMNH: 5 (1945-48). NRM: 3. UMZC: 2 (Wadi Natrun). USNM, AMNH, YPM, RMNH (Rüppell), RBINS, MZLU, CUMV: 1 each.

## (b) Not yet searched
- GBIF full paging of all Crocodylia records was not completed, because pages at deep offsets are too slow through the proxy.
- The GBIF untaxoned mummy-word and place-name queries were not run.
- Institution databases not checked directly: VertNet, MCZbase, AMNH EMu, NMNH, Naturalis Bioportal, MfN Berlin, Senckenberg, NHM Wien, ZFMK, SNSB, NHMD, NRM and other European museums, the Australian Museum, and the Zoological Institute St Petersburg.

## (c) Resume with these queries (keep offset below about 5,000 or split by datasetKey)
- `https://api.gbif.org/v1/occurrence/search?taxonKey=11493978&q={mummy|mummified|momie|mumie|mummia|momia|mumia}&limit=300`
- `https://api.gbif.org/v1/occurrence/search?q={term}&limit=300&offset=N`: page through each term, keeping only records that contain crocodile words (croc regex as in the scripts).
- `https://api.gbif.org/v1/occurrence/search?taxonKey=11493978&country=EG&limit=300`: 367 records, then check each record's locality.
- `https://api.gbif.org/v1/occurrence/search?q={crocodile|crocodilus|krokodil}&issue=TAXON_MATCH_HIGHERRANK&limit=300`
- `python3 scripts/gbif_sweep.py B: C: D:` (subset mode)

## Saturation
Not reached. Stopped when the orchestrator's budget ran out.
