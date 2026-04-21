import type {
  King,
  HistoricalEvent,
  CitationRef,
  Layer,
} from "../data/types";

interface Props {
  king: King;
  event: HistoricalEvent | null;
}

const LAYER_LABELS: Record<Layer, string> = {
  political: "政治",
  regional: "地域・建築",
  religious: "宗教",
};

const LAYER_COLORS: Record<Layer, string> = {
  political: "#c04040",
  regional: "#2f8f6e",
  religious: "#7a3ca1",
};

export default function EventDetail({ king, event }: Props) {
  if (!event) {
    return (
      <div className="detail">
        <p className="detail-empty">
          タイムラインの点、または地図の地点をクリックするとイベントの詳細が表示されます。
        </p>
      </div>
    );
  }

  const place = event.placeId
    ? king.places.find((p) => p.id === event.placeId)
    : undefined;

  return (
    <div className={`detail ${event.type === "interpretation" ? "is-interp" : ""}`}>
      <div className="detail-meta">
        <span
          className="chip"
          style={{ background: LAYER_COLORS[event.layer] }}
        >
          {LAYER_LABELS[event.layer]}
        </span>
        <span className="chip-section">{event.section}</span>
        {event.type === "interpretation" && (
          <span className="chip interp-chip">解釈・伝承</span>
        )}
        <span className="detail-year">
          {event.yearLabel}
          {event.approximate && " ※推定"}
        </span>
        {place && (
          <span className="detail-place">
            @ {place.nameJa}
            <span className="detail-place-en"> ({place.name})</span>
            {place.approximate && <em> ・概位置</em>}
          </span>
        )}
      </div>

      <h2 className="detail-title">{stripCitations(event.description)}</h2>

      <section className="detail-section">
        <h3>論文・史料</h3>
        <CitationRefsList king={king} refs={event.citationRefs} />
      </section>

      {event.alternatives && event.alternatives.length > 0 && (
        <section className="detail-section">
          <h3>別の研究者による解釈</h3>
          <ul className="alt-list">
            {event.alternatives.map((alt) => (
              <li key={alt.id}>
                <p>{alt.text}</p>
                <CitationRefsList king={king} refs={alt.citationRefs} />
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function stripCitations(s: string): string {
  return s.replace(/\[[^\]]+\]/g, "").replace(/\s+$/g, "").trim();
}

function CitationRefsList({
  king,
  refs,
}: {
  king: King;
  refs: CitationRef[];
}) {
  if (!refs.length)
    return <p className="detail-empty">（出典情報なし）</p>;
  return (
    <ul className="cite-list">
      {refs.map((ref, i) => {
        if (!ref.citationId) {
          return (
            <li key={i} className="cite-raw">
              <span className="cite-note">{ref.rawLabel}</span>
            </li>
          );
        }
        const c = king.citations.find((x) => x.id === ref.citationId);
        if (!c) return null;
        return (
          <li key={i}>
            <span className="cite-authors">{c.authors}</span>{" "}
            <span className="cite-year">({c.year})</span>{" "}
            <em>{c.title}</em>
            {c.publication && <>, {c.publication}</>}
            {ref.pages && <>, {ref.pages}</>}
            {c.url && (
              <>
                {" "}— <a href={c.url} target="_blank" rel="noreferrer">link</a>
              </>
            )}
            {c.note && <span className="cite-note"> · {c.note}</span>}
          </li>
        );
      })}
    </ul>
  );
}
