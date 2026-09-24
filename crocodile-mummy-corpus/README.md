# Global Corpus of Ancient Egyptian Crocodile Mummies (round 1, partial)

This is a source-traceable register of institutions holding ancient Egyptian crocodile
mummies, and of the individual objects they hold. It is the population for a later
comparison of head, back and tail wrapping. Status: **partial, not saturated**. See
`REPORT.md` for the figures and `NEXT_STEPS.md` to resume.

## Files

| File | Content |
|---|---|
| `institutions_master.csv` | One row per holding institution. The specified columns come first; `x_*` columns add traceability. |
| `objects_master.csv` | One row per object (museum + inventory number), classified A–F |
| `search_log.csv` | Every logged query: portal or search engine, language, result, agent |
| `searched_no_confirmation.csv` | Institutions checked where no crocodile mummy could be confirmed, with the reason |
| `bibliography.csv` | Works consulted, with an `access` level (full text / abstract / citation only) |
| `REPORT.md` | Figures generated from the CSVs by `scripts/stats.py` from `docs/REPORT_template.md` |
| `NEXT_STEPS.md` | Countries and databases not yet searched, unresolved records, how to resume |
| `work/AGENT_PROTOCOL.md` | Evidence, confidence and classification rules used by every agent |
| `work/agents/<agent>/` | Raw JSONL records, query scripts, raw API responses, and each agent's summary |
| `work/institution_aliases.csv`, `work/object_merges.csv`, `work/overrides.csv` | Curated deduplication and corrections, each with a stated reason |
| `work/ids.json` | Persistent institution and object IDs. Do not delete. |
| `work/leads_status.csv` | Every lead with its resolution (OPEN / IN_MASTER / CHECKED_NO_CONFIRMATION) |
| `work/url_check.csv` | Mechanical check that each evidence URL resolves and shows the inventory number |

## Rules (summary; full text in `work/AGENT_PROTOCOL.md`)

- **CONFIRMED:** an official collection record, catalogue or institutional page, or a
  scholarly study that examined or cited the object in that collection, identifies at
  least one crocodile mummy there.
- **PROBABLE:** reliable evidence, but no current object-level record.
- **UNVERIFIED:** candidate-only sources.
- Search snippets, blogs, news, auction sites and Google Arts & Culture alone never
  confirm a holding. Wiki sources are excluded entirely.
- Nothing is inferred. Provenance, date, species, inventory number, licence and counts are
  `UNKNOWN` unless a source states them.
- "Holds animal mummies" is not treated as evidence of a crocodile mummy.
- Deduplication:
  - Objects are keyed by institution + normalised inventory number.
  - Records without a number are never merged automatically; they are flagged in
    `work/merge_qa.txt` and merged only by hand, with a reason.
  - Differing values from different sources are all kept in `x_conflicts`.
- `minimum_confirmed_objects` is the larger of two numbers: the institution's CONFIRMED
  object rows, or a count stated by an official or scholarly source.

## Reproduce

```bash
python3 scripts/merge.py       # agent JSONL -> master CSVs (aliases, dedupe, persistent IDs)
python3 scripts/stats.py       # figures -> REPORT.md
python3 scripts/verify_urls.py # URL / inventory-number screening -> work/url_check.csv
```
