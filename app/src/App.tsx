import { useMemo, useRef, useState } from "react";
import { views } from "./data/loadData";
import type {
  ActorId,
  HistoricalEvent,
  Layer,
  Place,
  Citation,
  Actor,
} from "./data/types";
import Timeline from "./components/Timeline";
import MapView from "./components/MapView";
import EventDetail from "./components/EventDetail";
import CharacterPanel from "./components/CharacterPanel";
import BibliographyPanel from "./components/BibliographyPanel";
import ActorFilter from "./components/ActorFilter";
import "./App.css";

const ALL_LAYERS: Layer[] = ["political", "regional", "religious", "animal-cult"];

interface NormalizedView {
  id: string;
  labelJa: string;
  kind: "king" | "timeline";
  titleJa: string;
  titleEn?: string;
  epithetJa?: string;
  headerMeta?: { label: string; value: string }[];
  reignSummary?: string[];
  reigns?: { start: number; end: number; noteJa?: string }[];
  dateRange: { start: number; end: number };
  events: HistoricalEvent[];
  places: Place[];
  citations: Citation[];
  actors: Actor[];
  transparencyNote?: string;
  characterNotes?: ReturnType<
    typeof Object.assign
  > extends infer _ ? any : never;
}

function normalize(v: (typeof views)[number]): NormalizedView {
  if (v.kind === "king") {
    const k = v.king;
    const start = (k.birthYear ?? -200) - 2;
    const end = (k.deathYear ?? -100) + 2;
    return {
      id: v.id,
      labelJa: v.labelJa,
      kind: "king",
      titleJa: k.nameJa,
      titleEn: k.name,
      epithetJa: k.epithetJa,
      headerMeta: k.headerMeta,
      reignSummary: k.reignSummary,
      reigns: k.reigns,
      dateRange: { start, end },
      events: k.events,
      places: k.places,
      citations: k.citations,
      actors: [],
      transparencyNote: k.transparencyNote,
      characterNotes: k.characterNotes,
    };
  }
  const t = v.timeline;
  return {
    id: v.id,
    labelJa: v.labelJa,
    kind: "timeline",
    titleJa: t.titleJa,
    titleEn: t.title,
    dateRange: t.dateRange,
    events: t.events,
    places: t.places,
    citations: t.citations,
    actors: t.actors,
    transparencyNote: t.transparencyNote,
  };
}

function App() {
  const [viewId, setViewId] = useState<string>(views[0].id);
  const normalized = useMemo(() => {
    const v = views.find((x) => x.id === viewId) ?? views[0];
    return normalize(v);
  }, [viewId]);

  const [selectedEventId, setSelectedEventId] = useState<string | null>(
    normalized.events[0]?.id ?? null
  );
  const [hoveredEventId, setHoveredEventId] = useState<string | null>(null);
  const [enabledLayers, setEnabledLayers] = useState<Set<Layer>>(
    new Set(ALL_LAYERS)
  );
  const [showInterpretations, setShowInterpretations] = useState(true);

  const [enabledActors, setEnabledActors] = useState<Set<ActorId>>(
    new Set(normalized.actors.map((a) => a.id))
  );
  const [yearWindow, setYearWindow] = useState<[number, number]>([
    normalized.dateRange.start,
    normalized.dateRange.end,
  ]);

  // Reset state when switching views
  const prevViewId = useRef<string | null>(null);
  if (prevViewId.current !== viewId) {
    prevViewId.current = viewId;
    const nextView = views.find((x) => x.id === viewId) ?? views[0];
    const norm = normalize(nextView);
    queueMicrotask(() => {
      setSelectedEventId(norm.events[0]?.id ?? null);
      setEnabledActors(new Set(norm.actors.map((a) => a.id)));
      setYearWindow([norm.dateRange.start, norm.dateRange.end]);
    });
  }

  const filteredEvents = useMemo(() => {
    const [lo, hi] = yearWindow;
    return normalized.events.filter((e) => {
      if (!enabledLayers.has(e.layer)) return false;
      if (!showInterpretations && e.type === "interpretation") return false;
      const s = e.startYear;
      const en = e.endYear ?? e.startYear;
      if (en < lo || s > hi) return false;
      // Actor filter (only applies when the dataset has actors at all)
      if (normalized.actors.length > 0 && e.actors && e.actors.length > 0) {
        if (!e.actors.some((a) => enabledActors.has(a))) return false;
      }
      return true;
    });
  }, [
    normalized.events,
    normalized.actors,
    yearWindow,
    enabledLayers,
    showInterpretations,
    enabledActors,
  ]);

  const selectedEvent =
    normalized.events.find((e) => e.id === selectedEventId) ?? null;

  function toggleLayer(l: Layer) {
    setEnabledLayers((prev) => {
      const next = new Set(prev);
      if (next.has(l)) next.delete(l);
      else next.add(l);
      return next;
    });
  }

  function toggleActor(id: ActorId) {
    setEnabledActors((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="app-header-left">
          <div className="view-selector">
            {views.map((v) => (
              <button
                key={v.id}
                className={viewId === v.id ? "view-tab active" : "view-tab"}
                onClick={() => setViewId(v.id)}
              >
                {v.labelJa}
              </button>
            ))}
          </div>
          <h1>
            {normalized.titleJa}
            {normalized.titleEn && (
              <span className="app-title-en"> ({normalized.titleEn})</span>
            )}
          </h1>
          {normalized.epithetJa && (
            <div className="app-epithet">{normalized.epithetJa}</div>
          )}
          {normalized.reignSummary && normalized.reignSummary.length > 0 && (
            <ul className="reign-list">
              {normalized.reignSummary.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          )}
          {normalized.headerMeta && normalized.headerMeta.length > 0 && (
            <div className="app-meta">
              {normalized.headerMeta.map((m) => (
                <span key={m.label} className="meta-item">
                  <strong>{m.label}</strong>: {m.value}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="app-header-note">
          プトレマイオス朝史 可視化プロトタイプ (v0.3)
        </div>
      </header>

      {normalized.transparencyNote && (
        <div className="transparency-note">
          <strong>⚠ 補注</strong> {normalized.transparencyNote}
        </div>
      )}

      {normalized.actors.length > 0 && (
        <section className="panel actor-panel">
          <ActorFilter
            actors={normalized.actors}
            enabled={enabledActors}
            onToggle={toggleActor}
            onAll={() =>
              setEnabledActors(new Set(normalized.actors.map((a) => a.id)))
            }
            onNone={() => setEnabledActors(new Set())}
          />
        </section>
      )}

      <section className="panel timeline-panel">
        <div className="panel-head">
          <h2>タイムライン</h2>
          <div className="year-filter">
            <label className="interp-toggle">
              <input
                type="checkbox"
                checked={showInterpretations}
                onChange={(e) => setShowInterpretations(e.target.checked)}
              />
              解釈・伝承を表示
            </label>
            <label>
              始点: 前{-yearWindow[0]}年
              <input
                type="range"
                min={normalized.dateRange.start}
                max={normalized.dateRange.end}
                step={1}
                value={yearWindow[0]}
                onChange={(e) =>
                  setYearWindow([
                    Math.min(Number(e.target.value), yearWindow[1] - 1),
                    yearWindow[1],
                  ])
                }
              />
            </label>
            <label>
              終点: 前{-yearWindow[1]}年
              <input
                type="range"
                min={normalized.dateRange.start}
                max={normalized.dateRange.end}
                step={1}
                value={yearWindow[1]}
                onChange={(e) =>
                  setYearWindow([
                    yearWindow[0],
                    Math.max(Number(e.target.value), yearWindow[0] + 1),
                  ])
                }
              />
            </label>
            <button
              className="reset-btn"
              onClick={() =>
                setYearWindow([
                  normalized.dateRange.start,
                  normalized.dateRange.end,
                ])
              }
            >
              全期間
            </button>
          </div>
        </div>
        <Timeline
          startYear={yearWindow[0]}
          endYear={yearWindow[1]}
          reigns={normalized.reigns}
          events={filteredEvents}
          enabledLayers={enabledLayers}
          selectedEventId={selectedEventId}
          hoveredEventId={hoveredEventId}
          onSelect={setSelectedEventId}
          onHover={setHoveredEventId}
          onToggleLayer={toggleLayer}
        />
      </section>

      <section className="split-panel">
        <div className="map-panel">
          <div className="panel-head">
            <h2>地図</h2>
            <span className="muted">
              {filteredEvents.length} 件（フィルタ後 / 全{" "}
              {normalized.events.length} 件中）
            </span>
          </div>
          <MapView
            places={normalized.places}
            events={filteredEvents}
            selectedEventId={selectedEventId}
            hoveredEventId={hoveredEventId}
            onSelect={setSelectedEventId}
            onHover={setHoveredEventId}
          />
        </div>
        <div className="detail-panel">
          <div className="panel-head">
            <h2>詳細</h2>
          </div>
          <EventDetail
            event={selectedEvent}
            places={normalized.places}
            citations={normalized.citations}
            actors={normalized.actors}
          />
        </div>
      </section>

      {normalized.characterNotes && (
        <CharacterPanel
          king={{
            id: normalized.id,
            name: normalized.titleEn ?? "",
            nameJa: normalized.titleJa,
            headerMeta: normalized.headerMeta ?? [],
            reignSummary: normalized.reignSummary ?? [],
            reigns: normalized.reigns ?? [],
            events: normalized.events,
            places: normalized.places,
            citations: normalized.citations,
            characterNotes: normalized.characterNotes,
          }}
        />
      )}

      <BibliographyPanel
        citations={normalized.citations}
        events={normalized.events}
      />

      <footer className="app-footer">
        <div>
          データソース：
          {normalized.kind === "king" ? (
            <code>app/src/data/kings/{normalized.id}.md</code>
          ) : (
            <code>app/src/data/timelines/{normalized.id}.md</code>
          )}
          {" "}（Markdownを編集するとアプリが自動更新されます）
        </div>
        <div className="muted">
          © {new Date().getFullYear()} Ptolemaic History Visualizer (prototype)
        </div>
      </footer>
    </div>
  );
}

export default App;
