# NEXT_STEPS — resuming the crocodile-mummy corpus without duplication

This round stopped **before global saturation** because the budget ran out. All 20 round-1
agents wrapped up early. None of them reached saturation in its region.

Every record the agents wrote is persisted in `work/agents/*/*.jsonl`. It is merged into
the master CSVs (final checkpoint). Each agent's summary is saved in
`work/agents/<agent>/summary.md`; where the harness stopped an agent from writing it, the
orchestrator copied it from the agent's final report.

Final figures, from the CSVs:

| Measure | Count |
|---|---|
| Institutions | 88: 75 CONFIRMED (23 countries), 7 PROBABLE, 6 UNVERIFIED |
| Object rows | 774: 722 CONFIRMED, 46 PROBABLE, 6 UNVERIFIED |
| Sum of `minimum_confirmed_objects` | 735 |
| Checked, no confirmation | 76 institutions |
| Leads | 380: 339 OPEN, 32 IN_MASTER, 9 CHECKED_NO_CONFIRMATION |
| Logged queries | 984 |

## 0. How to resume (pipeline)

1. Read `work/AGENT_PROTOCOL.md` (evidence and confidence rules, classes A–F, no wiki
   sources).
2. Append new records with `python3 scripts/rec.py <agent_name> <kind>`. The validator
   enforces the schema.
3. Run `scripts/checkpoint.sh "<message>"`. It runs `merge.py` (aliases, deduplication,
   persistent IDs), then commits and pushes.
4. Curated files in `work/`:
   - `institution_aliases.csv`: name variants mapped to one institution.
   - `overrides.csv`: field corrections after verification.
   - `object_merges.csv`: manual merges of objects without inventory numbers.
   - `ids.json`: persistent IDs. **Never delete this file.**
5. Before searching anything, check that it has not already been done:
   - `search_log.csv`: every query already run, by agent.
   - `searched_no_confirmation.csv`: institutions already checked with a negative result.
   - `work/leads_status.csv`: every lead. `resolution` is OPEN, IN_MASTER or
     CHECKED_NO_CONFIRMATION.
   - `work/agents/<agent>/summary.md`: each agent's own list of what it did not search,
     and the scripts and URLs to resume from.
6. Tools that failed in this session and need an alternative next time:
   - WebSearch was capped at 200 calls per session and ran out early.
   - OpenAlex and Semantic Scholar returned 429 (daily quota).
   - The Smithsonian DEMO_KEY returned 429.
   - Several museum sites are behind Cloudflare or Anubis bot checks (see §4). Use a
     browser, a registered API key or a curator enquiry.

## 1. Countries and databases not yet searched (or only partly)

"Partly" means that some institutions were checked and the rest are listed.

| Region | Not yet searched / incomplete | Resume hints |
|---|---|---|
| **Egypt** | Regional museums (Kom Oshim/Karanis, Luxor Museum, Aswan and Nubia museums, Mallawi, Minya, Beni Suef, Sohag and others), Agricultural Museum (Dokki), Geological Museum, university museums, excavation stores. GEM unresolved. The MoTA portal (all 24 museum pages) and 67 ASAE volumes are exhausted. Kom Ombo Crocodile Museum: the official page names only 2 mummies (4.30 m and 2 m); the total is not stated. | Arabic queries: مومياء تمساح + museum and site names. Berruyer 2021 thesis. Ikram & Iskander 2002 (print only). |
| **United Kingdom – South & Wales** | **Oxford:** Ashmolean, Pitt Rivers, OUMNH. **Cambridge:** Museum of Zoology, Duckworth, MAA (Fitzwilliam done via API). **Wales:** Egypt Centre Swansea, Amgueddfa Cymru. **London:** Horniman only partly (candidates 4505, nn9438, 26.4.54/2). **All other S/E/SW regional museums**, e.g. Bristol H3034 (UNVERIFIED), RAMM Exeter, Torquay, Plymouth The Box, Norwich, Ipswich, Maidstone, Brighton, Reading, Eton Myers, Harrow. **BM:** full search impossible, site 403 to automated clients. | McKnight 2010 (BAR IS 2175) is the national catalogue of UK animal mummies; McKnight & Atherton-Woolham 2015 *Gifts for the Gods* |
| **United Kingdom – North, Scotland, Ireland** | Garstang, Durham Oriental Museum, Great North Museum, Leeds, York, Sheffield, other Yorkshire and Midlands museums, NMS, Hunterian, Aberdeen, Perth, Dundee, National Museum of Ireland, NMNI (Ulster Museum), Isle of Man | Glasgow: page the 125 "crocodile" results with `work/agents/uk_north/scripts/glasgow_mweb.py`. York search returns HTTP 200: parse it. NMS and NMI returned 403: retry. |
| **France & Monaco** | Every candidate except Louvre, Confluences, MNHN, Avignon, Besançon, Sens, Verdun, Cherbourg and Nancy. Not checked: Marseille MAM, Grenoble, Toulouse (Muséum, Labit), Montauban, Arles, Rouen, Le Havre, Boulogne, Lille, Strasbourg, Nantes, Dijon, Limoges, Roanne, Aix, Nice, Monaco and others (67 open FR leads). | Download the full Joconde export `https://ministere-culture.s3.sbg.io.cloud.ovh.net/POP/joconde.csv` to disk, then rerun `work/agents/france/scripts/joconde_filter2.py` (the stream broke after about 1M lines). Louvre: only per-object JSON pages work, search returns 429. Still missing: Champollion B. 240/241, "N 2901 ter", Louvre long-term deposits (`longTermLoanTo`). Nicolotti & Robert 1994 (Persée) is the Lyon crocodile catalogue. |
| **Germany** | **Natural history:** MfN Berlin, ZSM München, Senckenberg. **Museums:** Würzburg, Reiss-Engelhorn Mannheim, Landesmuseum Württemberg, Badisches Landesmuseum, MARKK, Gotha, Halle, Jena and the rest of the brief's list. **Portals:** DDB (website behind Anubis; Solr API partly used), museum-digital, bavarikon. **Literature:** Kockelmann 2017, Kessler 1989, Zesch 2015. | Hildesheim numbers: Zesch 2015 (academia.edu/12864588). Göttingen: https://sammlungen.uni-goettingen.de/suche/?q=Krokodil in a browser. Berlin ÄM and Leipzig returned negative online: ask the curators. |
| **Netherlands, Belgium, Luxembourg, Switzerland, Austria** | Naturalis, other Dutch candidates. RBINS Brussels, Mariemont, Grand Curtius Liège (lead I/681). All of Switzerland except MAH Geneva, which is bot-blocked (leads D 0241, D 0337). Museum der Kulturen Basel (onlinecollection.mkb.ch). NHM Wien, Austrian monastery collections. | Collectie Nederland: 3 of 13 queries ran before its rate limit (see `portals_europe` summary). rmo.nl is Cloudflare-blocked, so RMO data rests on Europeana and Collectie Nederland only; verify on rmo.nl in a browser. |
| **Italy, Vatican, Malta, Spain, Portugal** | **Italy:** Bologna, Milan (sites 403; lead E 0.9.41359), MAET Torino, Rome, MANN Naples, Padua, Pisa (Medinet Madi) and most other cities. **Vatican:** online catalogue timed out, recorded as no_confirmation, needs a retry. **Malta.** **Portugal:** MatrizNet not queried. **Spain:** Barcelona Museu Egipci, Montserrat. **Blocked:** PatER (403), CERES (429). | Ikram, Aicardi & Facchetti 2024 (Turin catalogue, nos. 149–163) lists parallels in other museums |
| **Nordic & Baltic** | Ny Carlsberg Glyptotek, NHMD Copenhagen, Gustavianum and Victoriamuseet Uppsala, NRM Stockholm, Östergötlands museum, Finland (Finna API), Iceland, Estonia, Latvia, Lithuania (except the National Museum of Lithuania via literature) | Finna: `https://api.finna.fi/v1/search?lookfor=krokotiili+muumio`. Natmus image URLs return 404 and api.natmus.dk fails. |
| **Central / Eastern Europe, Balkans, Greece, Turkey, Russia** | **Poland:** Warsaw NM, Kraków and Poznań archaeological museums, Łódź, Wrocław, Gdańsk, Gołuchów, Elbląg. **Russia:** Hermitage and goskatalog.ru (unreachable); Kunstkamera and the zoological museums (reachable, not searched). **Not searched at all:** HR, SI, RS, BA, MK, AL, BG, GR, CY, TR, BY, GE, AM, AZ, MD; Ukraine only through the literature. | Szépművészeti Múzeum Budapest: open `/mutargyak/14576/` and `/14577/` ("Krokodilmúmia"; HTTP 451 here). Topkapı: DOI 10.16947/fsmia.582351. Semmelweis Museum: DOI 10.1127/anthranz/2022/1587. goskatalog: «мумия крокодила». Zagreb Archaeological Museum; NAM Athens. |
| **USA – Northeast** | About 41 institutions, including MFA Boston, Harvard (Peabody, HMANE, Art Museums), AMNH Anthropology, Princeton, Buffalo, Rochester, RISD, Wadsworth, Berkshire, Springfield, Worcester. Brooklyn is UNVERIFIED (site 429). | MFA: `https://collections.mfa.org/search/objects/*/crocodile%20mummy`. Princeton: `https://artmuseum.princeton.edu/search/collections?mainSearch=crocodile`. Brooklyn: open object 3124 and lead 37.1365E (Manfalut) in a browser. Yale LUX: rerun `work/agents/portals_world/scripts/lux_sweep.py` (11 unverified hits). |
| **USA – South & Mid-Atlantic** | About 30 institutions: Texas/Oklahoma art museums, Puerto Rico, smaller DC museums. **Blocked:** SAMA, MFAH, Chrysler, Nasher, BMA, Birmingham MA, Gibbes, Ackland, Fralin, JHU, Memphis IEAA (JavaScript-only database). Carlos Museum is UNVERIFIED (2010 news only). | SAMA: official object record for 91.80.110.b,d |
| **USA – Midwest & West** | About 50 leads. **Blocked:** Kelsey (lead: Karanis), Field Museum database (object recorded without a number), DIA, Toledo, FAMSF, SLAM, Cantor (login), DMNS (403). | Kelsey: `quod.lib.umich.edu/k/kelsey` "crocodile" |
| **Canada** | Canadian Museum of History, McCord Stewart, MMFA, Musées de la civilisation, provincial and university museums. **Redpath:** 13 Artefacts Canada records, detail pages not opened, so numbers are UNKNOWN and 2 are probable duplicates. | `https://app.pch.gc.ca/application/artefacts_hum/detailler_detail.app?d=RMMH8469&lang=en` and the 12 other IDs in `work/agents/canada_oceania/raw/`. `scripts/artefacts_canada_get.py` handles the cookie challenge. |
| **Australia & New Zealand** | **Australia:** Australian Museum, Powerhouse, Macquarie, South Australian Museum, Queensland Museum, WA Museum, TMAG, NGV; Trove unused. **Museums Victoria:** blocked. **NZ:** Otago, Teece database, Whanganui. | Museums Victoria API: `https://collections.museumsvictoria.com.au/api/search?query=crocodile%20mummy` from an unblocked client. DigitalNZ API needs no key. |
| **Japan** | UMUT Tokyo, Gunma Museum of Natural History (Morimoto et al. 1998), Okayama Orient Museum, Waseda, MIHO, Tenri Sankokan, Nariwa, Shimonoseki, Middle Eastern Culture Center (Mitaka), Minpaku, other university and natural-history museums. The national portals (Japan Search, ColBase, CiNii, J-STAGE) are exhausted. | Scripts in `work/agents/east_asia/scripts/` |
| **China, Hong Kong, Taiwan, Korea, SE Asia, Mongolia** | Nothing searched, except Korea's e-museum portal. Seoul National University Museum record 「악어」 not opened. | 鳄鱼木乃伊 / 鱷魚木乃伊 / 악어 미라 |
| **Middle East, South Asia, Africa, Latin America** | **Middle East:** Gulf, Jordan, Lebanon, Iran. **South Asia:** CSMVS Mumbai, Baroda, Chennai, Lucknow, Lahore, Karachi. **Africa:** Sudan, Tunisia, Kenya, Ethiopia, Zimbabwe, Libya. **Latin America:** MAE-USP, Museu Egípcio Curitiba, Montevideo, Caracas, Bogotá. **Could not open:** Havana MNBA, Nierika, Durban. **Languages:** no Arabic or Persian queries run. | — |

### Cross-cutting sweeps not finished

| Sweep | Status | Resume |
|---|---|---|
| **National portals** | Europeana, K-samsök, DigitaltMuseum: done. **Not run:** DDB, museum-digital, bavarikon, POP/Joconde (full file), CulturaItalia, catalogo.beniculturali.it, CERES/Hispana, MatrizNet, Finna, Danish portals, Polish, Hungarian, Russian (goskatalog), UK Museum Data Service, Google Arts & Culture (candidate discovery only). | `work/agents/portals_europe/summary.md` |
| **Open APIs** | **Done:** Met, Cleveland, AIC, Japan Search, DigitalNZ, Fitzwilliam, partial Smithsonian. **Not run:** Harvard, Brooklyn, Walters, Penn (done by `usa_northeast`), Carlos, MFA, Field, ROM (done by `canada_oceania`), Trove, Princeton, BM, Manchester, NMS, NML, SMG, Google Arts & Culture. **Met:** screen all 653 "crocodile" hits (only mummy-term hits were screened). | — |
| **Natural-history databases** | GBIF and iDigBio were used only for MNHN and NHM. **Not run:** GBIF mummy-term and place-name searches, full Crocodylia paging (proxy too slow above about 10k records), VertNet, MCZ, AMNH, NMNH herpetology, Naturalis, MfN, Senckenberg, NHMW. Lead: Burke Museum UWBM:Herp:7021 (crocodile "mummified", no locality). | `work/agents/biodiversity/summary.md` |
| **Toponym reverse lookup** | **Sites not done:** Medinet Madi, Kiman Faris, Soknopaiou Nesos, Karanis, Philadelphia, Bacchias, Euhemeria, Magdola, Ghoran, Kom el-Ahmar, Gebelein, Gebel el-Silsila, Elephantine, Abydos, Tuna el-Gebel, Saqqara, Atfih, el-Hibeh, Shurafa, Kom Ishqaw, Dendera. | Egypt Exploration Society "Artefacts of Excavation" distribution lists for Theadelphia, Umm el-Baragat, Dimai, Hawara, Lahun and Gebelein |
| **Literature snowball** | Reference lists of about 12 papers followed. **Key unread works:** Nicolotti & Robert 1994; Ikram & Iskander 2002 (CG *Non-Human Mummies*); Ikram, Aicardi & Facchetti 2024 (Turin); Atherton-Woolham 2015 (Hawara crocodiles); McKnight et al. 2015 (Manchester); McKnight 2010 (BAR IS 2175); Diker & Ulaş 2019 (Topkapı); Kockelmann 2017; Molcho 2014; Berruyer 2021; Acolat 2024; the specimen table of Hekkala et al. 2011 and 2022; Strouhal & Vyhnánek 1979 (read; covers Czechoslovakia). | `bibliography.csv` has an `access` column: CITATION_ONLY / ABSTRACT rows are the unread ones |

## 2. Unresolved PROBABLE and UNVERIFIED institutions

See `institutions_master.csv` (confidence ≠ CONFIRMED) for the full rows.

| Institution | Status | What is needed |
|---|---|---|
| Museu Nacional, Rio de Janeiro | PROBABLE | 10 hatchling mummies (Nº 234, 268–275, 277) were studied in 2005. Did they survive the 2018 fire? Needs an official statement. |
| Museo Bacardí, Santiago de Cuba | PROBABLE | Juvenile bought in 1912. Needs an official catalogue record. |
| Roemer- und Pelizaeus-Museum Hildesheim | PROBABLE | No inventory number. Needs Zesch 2015 or a curator enquiry. |
| Mummification Museum, Luxor | PROBABLE | The Egyptian State Information Service (official government portal) says only generically that crocodile mummies are displayed. Needs an object-level record. |
| Muséum-Aquarium de Nancy | PROBABLE | Joconde gives "N 2902", which equals Louvre N 2902: is it a deposit or an outdated location? Ask the Louvre (AE) or Nancy. |
| National Museum in Lublin | PROBABLE | Official exhibition page, but ownership vs loan is unclear |
| D.I. Yavornytsky Museum, Dnipro | PROBABLE | Literature only. Needs a museum record. |
| Bristol Museum & Art Gallery | UNVERIFIED | H3034 known from search snippets only. Bristol site had TLS/503 errors. |
| Museum of Fine Arts, Budapest | UNVERIFIED | Pages /mutargyak/14576/ and /14577/ (HTTP 451 from this network) |
| Savaria Museum, Szombathely | UNVERIFIED | Museum blog only |
| National Museum in Poznań | UNVERIFIED | Crocodile head, news only |
| Brooklyn Museum | UNVERIFIED | Site 429. Leads: 37.1365E (Manfalut), object 3124. |
| Michael C. Carlos Museum | UNVERIFIED | 2010 news article only. Online database shows none. |

## 3. Open leads

`work/leads_status.csv` holds 380 leads, of which 339 are OPEN.

Leading countries: FR 67, US 64, GB 38, DE 30, IT 15, EG 10, CA 8, AU 7, JP 7, CH 6,
then 1–6 each for about 50 other countries. Work through the OPEN rows by country. Record
each checked lead as institution/objects or as `no_confirmation`. `merge.py` then updates
the `resolution` column automatically.

High-value open leads named by several agents:
- British Museum: EA 35734, 35726, 35747, 35751, 6837, 6847, EA6850.
- Manchester: MM 7892, 12008, 1772, "EA 19/2".
- Carnegie Museum of Natural History: 1867-4.
- MAH Geneva: D 0241, D 0337.
- Grand Curtius, Liège: I/681.
- Milan: E 0.9.41359.
- Brooklyn: 37.1365E.
- Horniman: 4505, nn9438, 26.4.54/2.
- Kelsey Museum: Karanis.
- Burke Museum: UWBM:Herp:7021.
- Topkapı Palace: Diker & Ulaş 2019.

## 4. Unfinished verification tasks

1. **Mechanical URL check — UNFINISHED.** It was stopped on budget after 37 of 774 objects
   (48 URL rows, up to `INST-CA-001-O008`, in `object_id` order).
   - Results so far: 17 × HTTP 200 with the inventory number found; 14 × HTTP 200 with the
     number not found; 11 × HTTP 403; 6 × no number to check.
   - To resume, run `python3 scripts/verify_urls.py`. It skips (object_id, url) pairs
     already in `work/url_check.csv` and caches repeated URLs.
   - Budget for about 800 URLs at 1.5 s per host (roughly 30–60 min). Most of the time goes
     on the Musée des Confluences portal (about 300 URLs).
   - A "NO" or an error is a prompt for a manual check, not evidence against a record.
     Likely false negatives: pages rendered by JavaScript, bot-blocked sites (BM, MNHN,
     rmo.nl, Louvre search), and archive.org catalogue scans where the number is not in the
     page text.
   - Manual follow-up needed now: the 25 rows marked NO or 403 in `work/url_check.csv`.
2. **Official records not yet opened.** These records rest on portal copies or archived
   pages:
   - RMO Leiden: Europeana / Collectie Nederland.
   - British Museum: archived official pages and BM PDFs.
   - MNHN Paris: GBIF/iDigBio, because its own site is Cloudflare-blocked.
   - Museon, MAN Madrid, Cluj, Brussels (part), SKD Dresden, Kestner: Europeana records only.
3. **Inventory numbers still UNKNOWN or from secondary sources.**
   - SMÄK Munich mask ÄS 6809 (secondary source).
   - Manchester 1772 and "EA 19/2".
   - SAMA 91.80.110.b,d (blog copy of the caption).
   - Redpath: 13 Artefacts Canada records.
   - Field Museum: 1 object.
   - Allard Pierson: 1 object.
   - Bergen: 2 objects, photos only.
   - Qubbat al-Hawa: 10 objects, find numbers only.
   - Kom Ombo Crocodile Museum: 2 rows (official total unknown).
   - `work/merge_qa.txt` lists every institution where rows without numbers may duplicate
     one another.
4. **Two records with the same inventory number** (merged, pending confirmation).
   - Cluj V 1681: Europeana has two records. It could be two objects under one number.
   - Görlitz EK 102-1999-6: one number for 7 hatchlings.
   - Kestner: one record for two mummies.
5. **Old catalogue entries.** The Cairo CG entries from Gaillard & Daressy 1905 are PROBABLE
   unless also in a current record. Check them against Ikram & Iskander 2002 (CG
   *Non-Human Mummies*).
6. **Origin not stated as Egyptian.**
   - KHM Oslo UEM3648 ("krokodillemumie", place unknown).
   - NHM London 1977.448 ("mummified", no locality).
   - Burke Museum lead.
   - These are kept but flagged. Egyptian origin is not stated.
7. **Image audit not done.** `head_visible`, `dorsal_visible` and `tail_visible` are
   `UNKNOWN` for almost all objects. Next step: download the primary image of every
   class A/B object with `image_urls`, then record the three visibility fields.
