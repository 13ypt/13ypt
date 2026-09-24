# benelux_alpine — summary (stopped early on orchestrator WRAP-UP order)

## (a) Done
- CONFIRMED institutions (5), objects written (26):
  - RMO Leiden (NL): AMM 16a, 16g, 16h, 16i, 16k, CI 260, F 1998/11.3 + crocodile masks F 1987/1.1, 1.2 (via Europeana + Collectie Nederland OAI; rmo.nl blocked by Cloudflare).
  - Museon-Omniversum, The Hague (NL): 8258 (juvenile, Krokodilopolis/Fayum).
  - Allard Pierson, Amsterdam (NL): 1 crocodile mummy, inventory not found (Sidestone 2025 monograph, abstract/contents only).
  - Art & History Museum / KMKG Brussels (BE): E.00453 (ancient pseudo-mummy), E.01229, E.07043a/b (Tebtunis), E.07092a/b, E.09018 (Carmentis; scripts/carmentis_search.py).
  - KHM Vienna (AT): ÄS 264, 265, 266, 266a, 266b, 266c (eggs), 290, 292 (khm.at + Europeana).
- Europeana checked by country for NL/BE/CH/AT/LU/LI: no Swiss, Luxembourg or Liechtenstein crocodile mummies.
- MAH Genève: no_confirmation (DB blocked).

## (b) NOT YET SEARCHED
- CH: everything except the MAH attempt. Includes MKB Basel (onlinecollection.mkb.ch), Antikenmuseum Basel, NMB, BHM Bern, NMBE, MEN/Muséum Neuchâtel, MCAH Lausanne, MEG, Muséum Genève, UZH, BIBEL+ORIENT, Gandur, St. Gallen, Schaffhausen, Abegg, Prangins.
- BE: RBINS, Mariemont, Grand Curtius, ULiège, Musée L, GUM, MAS, Tongeren, Mons, Namur, Charleroi; erfgoedplus.be.
- NL: Naturalis Bioportal, Wereldmuseum, Teylers, Meermanno, Utrecht, Groningen, Valkhof, Kam, Maastricht, Brabant, Boerhaave. Collectie Nederland search was rate-limited (429).
- AT: NHM Wien, Weltmuseum, Joanneum, Tirol, Linz, Salzburg, Kärnten, monasteries, Univ. Wien.
- LU: MNHA, MNHN (only Europeana checked).
- WebSearch budget (200) exhausted; OpenAlex daily quota exhausted; DDG/Bing/Brave/Mojeek unusable.

## (c) Resume
- Collectie Nederland: OAI works (`/api/oai-pmh/?verb=GetRecord&metadataPrefix=edm&identifier=dcn_<set>_<id>`); search `https://www.collectienederland.nl/search/?q=krokodil+mummie` once the 429 clears.
- Allard Pierson inventory number: https://www.sidestone.com/bookviewer/9789464263640 (chapter 'Crocodile Mummy').
- RMO own DB: https://www.rmo.nl/collectie/collectiezoeker/?q=krokodil (browser needed); check for eggs/bundles that are not in the portals.
- MAH: https://www.mahmah.ch/collection/oeuvres?search=crocodile (browser).
- Saturation: not reached in this assignment. The Europeana country sweeps are saturated for NL/BE/AT/CH/LU/LI.
