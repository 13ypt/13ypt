import type { King, HistoricalEvent } from "../data/types";

interface Props {
  king: King;
  event: HistoricalEvent | null;
}

const formatYear = (y: number) => (y < 0 ? `前${-y}年` : `${y}年`);

const CATEGORY_JA: Record<string, string> = {
  reign: "即位／治世",
  war: "戦争",
  diplomacy: "外交",
  religion: "宗教",
  building: "建造",
  family: "王家・家族",
  decree: "勅令・法",
  revolt: "反乱",
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

  const place = king.places.find((p) => p.id === event.placeId);
  const citations = event.citationIds
    .map((id) => king.citations.find((c) => c.id === id))
    .filter((c): c is NonNullable<typeof c> => Boolean(c));

  const yearRange =
    event.endYear !== undefined
      ? `${formatYear(event.startYear)}–${formatYear(event.endYear)}`
      : formatYear(event.startYear);

  return (
    <div className="detail">
      <div className="detail-meta">
        <span className="chip">{CATEGORY_JA[event.category] ?? event.category}</span>
        <span className="detail-year">{yearRange}</span>
        {place && (
          <span className="detail-place">
            @ {place.nameJa}
            <span className="detail-place-en"> ({place.name})</span>
          </span>
        )}
      </div>

      <h2 className="detail-title">{event.titleJa}</h2>
      <div className="detail-title-en">{event.title}</div>

      <section className="detail-section">
        <h3>概要</h3>
        <p>{event.summaryJa}</p>
        <p className="detail-en">{event.summary}</p>
      </section>

      {event.stateOfCountryJa && (
        <section className="detail-section">
          <h3>当時のエジプトの状況</h3>
          <p>{event.stateOfCountryJa}</p>
          {event.stateOfCountry && (
            <p className="detail-en">{event.stateOfCountry}</p>
          )}
        </section>
      )}

      <section className="detail-section">
        <h3>論文・史料</h3>
        <ul className="cite-list">
          {citations.map((c) => (
            <li key={c.id}>
              <span className="cite-authors">{c.authors}</span>{" "}
              <span className="cite-year">({c.year})</span>{" "}
              <em>{c.title}</em>, <span>{c.publication}</span>
              {c.pages && <span>, {c.pages}</span>}
              {c.url && (
                <>
                  {" "}
                  —{" "}
                  <a href={c.url} target="_blank" rel="noreferrer">
                    link
                  </a>
                </>
              )}
              {c.note && <span className="cite-note"> · {c.note}</span>}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
