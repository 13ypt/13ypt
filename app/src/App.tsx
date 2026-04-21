import { useMemo, useState } from "react";
import { kings } from "./data/loadKings";
import type { Layer } from "./data/types";
import Timeline from "./components/Timeline";
import MapView from "./components/MapView";
import EventDetail from "./components/EventDetail";
import CharacterPanel from "./components/CharacterPanel";
import "./App.css";

const ALL_LAYERS: Layer[] = ["political", "regional", "religious"];

function App() {
  const king = kings[0];
  const [selectedEventId, setSelectedEventId] = useState<string | null>(
    king.events[0]?.id ?? null
  );
  const [hoveredEventId, setHoveredEventId] = useState<string | null>(null);
  const [enabledLayers, setEnabledLayers] = useState<Set<Layer>>(
    new Set(ALL_LAYERS)
  );
  const [showInterpretations, setShowInterpretations] = useState(true);

  const minYear = (king.birthYear ?? -200) - 2;
  const maxYear = (king.deathYear ?? -100) + 2;
  const [yearWindow, setYearWindow] = useState<[number, number]>([
    minYear,
    maxYear,
  ]);

  const filteredEvents = useMemo(() => {
    const [lo, hi] = yearWindow;
    return king.events.filter((e) => {
      if (!enabledLayers.has(e.layer)) return false;
      if (!showInterpretations && e.type === "interpretation") return false;
      const s = e.startYear;
      const en = e.endYear ?? e.startYear;
      return en >= lo && s <= hi;
    });
  }, [king.events, yearWindow, enabledLayers, showInterpretations]);

  const selectedEvent =
    king.events.find((e) => e.id === selectedEventId) ?? null;

  function toggleLayer(l: Layer) {
    setEnabledLayers((prev) => {
      const next = new Set(prev);
      if (next.has(l)) next.delete(l);
      else next.add(l);
      return next;
    });
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <div>
          <h1>
            {king.nameJa}{" "}
            <span className="app-title-en">({king.name})</span>
          </h1>
          <div className="app-epithet">
            {king.epithetJa && <>{king.epithetJa}</>}
          </div>
          {king.reignSummary.length > 0 && (
            <ul className="reign-list">
              {king.reignSummary.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          )}
          {king.headerMeta.length > 0 && (
            <div className="app-meta">
              {king.headerMeta.map((m) => (
                <span key={m.label} className="meta-item">
                  <strong>{m.label}</strong>: {m.value}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="app-header-note">
          プトレマイオス朝史 可視化プロトタイプ (v0.2)
        </div>
      </header>

      {king.transparencyNote && (
        <div className="transparency-note">
          <strong>⚠ 補注</strong> {king.transparencyNote}
        </div>
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
                min={maxYear}
                max={minYear}
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
                min={maxYear}
                max={minYear}
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
              onClick={() => setYearWindow([minYear, maxYear])}
            >
              全期間
            </button>
          </div>
        </div>
        <Timeline
          king={king}
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
              {filteredEvents.length} 件（フィルタ後 / 全 {king.events.length} 件中）
            </span>
          </div>
          <MapView
            king={king}
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
          <EventDetail king={king} event={selectedEvent} />
        </div>
      </section>

      <CharacterPanel king={king} />

      <footer className="app-footer">
        <div>
          データソース：
          <code>app/src/data/kings/ptolemy-viii.md</code>{" "}
          （Markdownを編集するとアプリが自動更新されます）
        </div>
        <div className="muted">
          © {new Date().getFullYear()} Ptolemaic History Visualizer (prototype)
        </div>
      </footer>
    </div>
  );
}

export default App;
