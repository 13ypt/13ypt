import type { King, CitationRef } from "../data/types";

interface Props {
  king: King;
}

export default function CharacterPanel({ king }: Props) {
  const notes = king.characterNotes;
  if (!notes) return null;
  return (
    <section className="panel character-panel">
      <div className="panel-head">
        <h2>{notes.title}</h2>
        <span className="muted">解釈は論文ごとに異なりうる点に注意</span>
      </div>
      {notes.intro && <p className="char-intro">{notes.intro}</p>}
      <ul className="char-list">
        {notes.items.map((item, i) => (
          <li key={i}>
            {item.label && <strong>{item.label}：</strong>}
            <span>{stripCitations(item.text)}</span>
            <Refs king={king} refs={item.citationRefs} />
          </li>
        ))}
      </ul>
    </section>
  );
}

function stripCitations(s: string): string {
  return s.replace(/\[[^\]]+\]/g, "").replace(/\s+$/g, "").trim();
}

function Refs({ king, refs }: { king: King; refs: CitationRef[] }) {
  if (!refs.length) return null;
  return (
    <div className="char-refs">
      {refs.map((ref, i) => {
        if (!ref.citationId)
          return (
            <span key={i} className="cite-inline muted">
              [{ref.rawLabel}]
            </span>
          );
        const c = king.citations.find((x) => x.id === ref.citationId);
        if (!c) return null;
        return (
          <span key={i} className="cite-inline">
            [{c.key}
            {ref.pages ? `: ${ref.pages}` : ""}]
          </span>
        );
      })}
    </div>
  );
}
