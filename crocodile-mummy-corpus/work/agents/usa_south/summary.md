# usa_south – summary (2026-09-24)

## (a) Done
- **CONFIRMED institutions (2):**
  - Smithsonian NMNH (Washington DC). Evidence: Open Access API. 2 object rows: **A74579-0** "Mummied Crocodile" (Thebes/Qena, donated by G.W. Samson 1885) and **AT5604-0** "Mummified Reptiles" (a box of 50 mummified reptiles "incl. crocodiles"; 4 crocodile mummies exhibited under this number).
  - San Antonio Museum of Art. Evidence: official exhibition page. stated_count 3; Culture in Crisis gives 4. 1 object row: **91.80.110.b,d** (PROBABLE; caption survives only in a secondary reproduction).
- **UNVERIFIED (1):** Michael C. Carlos Museum. An NBC News report (2010) mentions a displayed crocodile mummy, but it is not in eMuseum.
- **no_confirmation (21):** Walters (CC0 data dump), Dallas MA (API), VMFA, NCMA, HMNS, MFAH (blocked), JHU (blocked), Memphis IEAA/AMUM (JS-only DB), natural-history herpetology collections via iDigBio/GBIF (FLMNH, NCSM, LSUMZ, TCWC, TNHC, OMNH: no Egyptian crocodiles), and weak website-only negatives (McClung, Speed, Georgia MoA, Ringling, Cummer, Tellus, Pink Palace).
- Literature: Hekkala et al. 2011, Table S3. None of its mummy samples are in the region (PHM, Penn, BM, MNHN → leads).

## (b) NOT YET SEARCHED / blocked
- Blocked (403/bot): SAMA eMuseum, MFAH eMuseum, Chrysler, Nasher, BMA Baltimore, Birmingham MA, Charleston Museum, Gibbes, Ackland, UVA Fralin, JHU, collections.si.edu.
- Not searched: NMHM, Freer/Sackler, Dumbarton Oaks, Catholic U, Howard, Delaware AM, Muscarelle, VA MNH, Mint, Columbia MA DB, Lowe, Orlando, Brooks, Lauren Rogers, MS MNS, Ole Miss Museum, NOMA, Tulane, LSU MOA, Arkansas, Kimbell, Perot, Witte, Blanton, Mayborn, Texas Tech, Philbrook, Gilcrease, Fred Jones, Sam Noble ethnology, Puerto Rico (UPR Museo, Ponce). All are in leads.jsonl.
- Tools exhausted: the WebSearch session budget is used up, OpenAlex has hit its daily limit, and the SI DEMO_KEY returns 429.

## (c) Resume
- `https://api.si.edu/openaccess/api/v1.0/search?q=Sobek&api_key=DEMO_KEY` and `q=Crocodylus AND Egypt`
- `https://sanantonio.emuseum.com/search/crocodile` (browser): get the accession numbers for all 3–4 crocodiles
- `https://amum.catalogaccess.com/search` keyword "crocodile" (browser)
- `https://collections.carlos.emory.edu/` / registrar: verify the crocodile from the NBC 2010 report
- `https://emuseum.mfah.org/search/crocodile`, `https://chrysler.emuseum.com/search/crocodile`, `https://emuseum.nasher.duke.edu/search/crocodile`
- `https://tampamuseum.org/mysteries-of-the-nile-ancient-egypt/`: get the checklist and lenders

## Saturation
Not reached. The run stopped early on the orchestrator's budget instruction. Web discovery beyond the named candidates was not possible after WebSearch was exhausted.
