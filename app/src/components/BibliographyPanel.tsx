import type { Citation, HistoricalEvent } from "../data/types";

interface Props {
  citations: Citation[];
  events: HistoricalEvent[]; // used to compute per-citation event counts
}

export default function BibliographyPanel({ citations, events }: Props) {
  if (!citations.length) return null;

  // Count how many events reference each citation
  const countById: Record<string, number> = {};
  for (const ev of events) {
    for (const ref of ev.citationRefs) {
      if (!ref.citationId) continue;
      countById[ref.citationId] = (countById[ref.citationId] ?? 0) + 1;
    }
  }

  // Only show citations actually in use
  const used = citations.filter((c) => (countById[c.id] ?? 0) > 0);
  const unused = citations.filter((c) => !(countById[c.id] ?? 0));

  return (
    <section className="panel bibliography-panel">
      <div className="panel-head">
        <h2>参考文献</h2>
        <span className="muted">
          {used.length} 件使用中{unused.length > 0 && ` / ${unused.length} 件未参照`}
        </span>
      </div>
      <ol className="bib-list">
        {used.map((c) => (
          <li key={c.id} id={`bib-${c.id}`}>
            <span className="cite-authors">{c.authors}</span>{" "}
            <span className="cite-year">({c.year})</span>{" "}
            <em>{c.title}</em>
            {c.publication && <>, {c.publication}</>}
            {c.note && <span className="cite-note"> · {c.note}</span>}
            <span className="bib-count"> [{countById[c.id]} 件]</span>
          </li>
        ))}
      </ol>
      {unused.length > 0 && (
        <details className="bib-unused">
          <summary>未参照の文献 ({unused.length}件)</summary>
          <ol>
            {unused.map((c) => (
              <li key={c.id}>
                <span className="cite-authors">{c.authors}</span>{" "}
                <span className="cite-year">({c.year})</span>{" "}
                <em>{c.title}</em>
                {c.publication && <>, {c.publication}</>}
              </li>
            ))}
          </ol>
        </details>
      )}
    </section>
  );
}
