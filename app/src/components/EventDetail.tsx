import type {
  HistoricalEvent,
  CitationRef,
  Layer,
  Citation,
  Place,
  Actor,
} from "../data/types";
import { LAYER_COLORS, LAYER_LABELS } from "./Timeline";

interface Props {
  event: HistoricalEvent | null;
  places: Place[];
  citations: Citation[];
  actors?: Actor[];
}

export default function EventDetail({
  event,
  places,
  citations,
  actors = [],
}: Props) {
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
    ? places.find((p) => p.id === event.placeId)
    : undefined;

  const actorObjs =
    event.actors
      ?.map((id) => actors.find((a) => a.id === id))
      .filter((a): a is Actor => Boolean(a)) ?? [];

  return (
    <div
      className={`detail ${event.type === "interpretation" ? "is-interp" : ""}`}
    >
      <div className="detail-meta">
        <span
          className="chip"
          style={{ background: LAYER_COLORS[event.layer as Layer] }}
        >
          {LAYER_LABELS[event.layer as Layer]}
        </span>
        <span className="chip-section">{event.section}</span>
        {event.type === "interpretation" && (
          <span className="chip interp-chip">解釈・伝承</span>
        )}
        <span className="detail-year">{event.yearLabel}</span>
        {place && (
          <span className="detail-place">
            @ {place.nameJa}
            <span className="detail-place-en"> ({place.name})</span>
            {place.approximate && <em> ・概位置</em>}
          </span>
        )}
      </div>

      {event.approximate && (
        <div className="detail-approx-row">
          <span className="chip approx-chip">推定</span>
          <span className="detail-approx-note">
            年代は研究者の推定値／範囲表記です（「ごろ」「後半」「夏」等）。
          </span>
        </div>
      )}

      {actorObjs.length > 0 && (
        <div className="actor-chips">
          {actorObjs.map((a) => (
            <span key={a.id} className="actor-chip">
              {a.nameJa}
            </span>
          ))}
        </div>
      )}

      <h2 className="detail-title">{stripCitations(event.description)}</h2>

      <section className="detail-section">
        <h3>論文・史料</h3>
        <CitationRefsList citations={citations} refs={event.citationRefs} />
      </section>

      {event.alternatives && event.alternatives.length > 0 && (
        <section className="detail-section">
          <h3>別の研究者による解釈</h3>
          <ul className="alt-list">
            {event.alternatives.map((alt) => (
              <li key={alt.id}>
                <p>{alt.text}</p>
                <CitationRefsList
                  citations={citations}
                  refs={alt.citationRefs}
                />
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
  citations,
  refs,
}: {
  citations: Citation[];
  refs: CitationRef[];
}) {
  if (!refs.length)
    return <p className="detail-empty">（典拠未記載）</p>;
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
        const c = citations.find((x) => x.id === ref.citationId);
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
