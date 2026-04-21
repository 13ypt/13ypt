import { useMemo, useState } from "react";
import { ptolemyVIII } from "./data/ptolemyVIII";
import Timeline from "./components/Timeline";
import MapView from "./components/MapView";
import EventDetail from "./components/EventDetail";
import "./App.css";

function App() {
  const king = ptolemyVIII;
  const [selectedEventId, setSelectedEventId] = useState<string | null>(
    king.events[0]?.id ?? null
  );
  const [hoveredEventId, setHoveredEventId] = useState<string | null>(null);
  const [yearWindow, setYearWindow] = useState<[number, number]>([
    king.birthYear - 2,
    king.deathYear + 2,
  ]);

  const filteredEvents = useMemo(() => {
    const [lo, hi] = yearWindow;
    return king.events.filter((e) => {
      const s = e.startYear;
      const en = e.endYear ?? e.startYear;
      return en >= lo && s <= hi;
    });
  }, [king.events, yearWindow]);

  const selectedEvent =
    king.events.find((e) => e.id === selectedEventId) ?? null;

  return (
    <div className="app-root">
      <header className="app-header">
        <div>
          <h1>
            {king.nameJa}{" "}
            <span className="app-title-en">({king.name})</span>
          </h1>
          <div className="app-epithet">
            {king.epithetJa} · {king.epithet} ／ 生没: {formatYear(king.birthYear)}〜
            {formatYear(king.deathYear)}
          </div>
        </div>
        <div className="app-header-note">
          プトレマイオス朝史 可視化プロトタイプ (v0.1 — サンプル：プトレマイオス8世)
        </div>
      </header>

      <section className="panel timeline-panel">
        <div className="panel-head">
          <h2>タイムライン</h2>
          <div className="year-filter">
            <label>
              始点: 前{-yearWindow[0]}年
              <input
                type="range"
                min={king.deathYear + 2}
                max={king.birthYear - 2}
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
                min={king.deathYear + 2}
                max={king.birthYear - 2}
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
                setYearWindow([king.birthYear - 2, king.deathYear + 2])
              }
            >
              全期間
            </button>
          </div>
        </div>
        <Timeline
          king={king}
          selectedEventId={selectedEventId}
          hoveredEventId={hoveredEventId}
          onSelect={setSelectedEventId}
          onHover={setHoveredEventId}
        />
      </section>

      <section className="panel split-panel">
        <div className="map-panel">
          <div className="panel-head">
            <h2>地図</h2>
            <span className="muted">
              {filteredEvents.length} 件（年代フィルタ後）
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

      <footer className="app-footer">
        <div>
          データは学術文献・一次史料に基づくサンプル。実研究での利用時は必ず一次情報を再確認してください。
        </div>
        <div className="muted">
          © {new Date().getFullYear()} Ptolemaic History Visualizer (prototype)
        </div>
      </footer>
    </div>
  );
}

function formatYear(y: number) {
  return y < 0 ? `前${-y}年` : `${y}年`;
}

export default App;
