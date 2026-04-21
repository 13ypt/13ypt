import type { HistoricalEvent, King, Layer } from "../data/types";

const LAYER_COLORS: Record<Layer, string> = {
  political: "#c04040",
  regional: "#2f8f6e",
  religious: "#7a3ca1",
};

const LAYER_LABELS: Record<Layer, string> = {
  political: "政治",
  regional: "地域・建築",
  religious: "宗教",
};

interface Props {
  king: King;
  events: HistoricalEvent[]; // already filtered by layers
  enabledLayers: Set<Layer>;
  selectedEventId: string | null;
  hoveredEventId: string | null;
  onSelect: (id: string) => void;
  onHover: (id: string | null) => void;
  onToggleLayer: (layer: Layer) => void;
}

const formatYear = (y: number) => (y < 0 ? `前${-y}年` : `${y}年`);

export default function Timeline({
  king,
  events,
  enabledLayers,
  selectedEventId,
  hoveredEventId,
  onSelect,
  onHover,
  onToggleLayer,
}: Props) {
  const minYear = (king.birthYear ?? -200) - 2;
  const maxYear = (king.deathYear ?? -100) + 2;
  const span = Math.max(1, maxYear - minYear);

  const width = 1100;
  const padL = 40;
  const padR = 20;
  const plotW = width - padL - padR;

  const yearToX = (y: number) => padL + ((y - minYear) / span) * plotW;

  const ticks: number[] = [];
  const startTick = Math.ceil(minYear / 10) * 10;
  for (let y = startTick; y <= maxYear; y += 10) ticks.push(y);

  const eventsSorted = [...events].sort((a, b) => a.startYear - b.startYear);

  // Allocate lanes per layer (three row-groups)
  const layerOrder: Layer[] = ["political", "regional", "religious"];
  const laneByEvent: Record<string, { row: number; layerRow: number }> = {};
  const layerLaneCount: Record<Layer, number> = {
    political: 0,
    regional: 0,
    religious: 0,
  };

  for (const layer of layerOrder) {
    const lanesEnd: number[] = [];
    const evsInLayer = eventsSorted.filter((e) => e.layer === layer);
    for (const ev of evsInLayer) {
      const start = ev.startYear;
      const end = ev.endYear ?? ev.startYear;
      let lane = 0;
      while (lane < lanesEnd.length && lanesEnd[lane] >= start - 1) lane++;
      if (lane === lanesEnd.length) lanesEnd.push(end);
      else lanesEnd[lane] = end;
      laneByEvent[ev.id] = { row: lane, layerRow: lane };
    }
    layerLaneCount[layer] = Math.max(1, lanesEnd.length);
  }

  const reignBandY = 78;
  const reignBandH = 18;
  const groupGap = 10;
  const laneH = 16;
  const dotR = 6;

  // Compute y offsets for each layer group
  const layerYStart: Record<Layer, number> = {} as Record<Layer, number>;
  let cursor = reignBandY + reignBandH + groupGap + 4;
  for (const layer of layerOrder) {
    layerYStart[layer] = cursor;
    cursor += layerLaneCount[layer] * laneH + groupGap;
  }
  const svgHeight = cursor + 10;

  return (
    <div className="timeline-wrap">
      <div className="layer-toggles">
        {layerOrder.map((l) => (
          <label key={l} className="layer-toggle">
            <input
              type="checkbox"
              checked={enabledLayers.has(l)}
              onChange={() => onToggleLayer(l)}
            />
            <span
              className="layer-swatch"
              style={{ background: LAYER_COLORS[l] }}
            />
            {LAYER_LABELS[l]}
          </label>
        ))}
        <span className="legend-hint">
          <span className="legend-dot fact" /> 事実 / 記述
          <span className="legend-dot interp" /> 解釈・伝承
        </span>
      </div>

      <svg
        viewBox={`0 0 ${width} ${svgHeight}`}
        className="timeline-svg"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* axis */}
        <line x1={padL} x2={width - padR} y1={60} y2={60} stroke="#888" />
        {ticks.map((t) => (
          <g key={t}>
            <line x1={yearToX(t)} x2={yearToX(t)} y1={56} y2={64} stroke="#888" />
            <text
              x={yearToX(t)}
              y={48}
              textAnchor="middle"
              fontSize={11}
              fill="#555"
            >
              {formatYear(t)}
            </text>
          </g>
        ))}

        {/* life span line */}
        {king.birthYear !== undefined && king.deathYear !== undefined && (
          <>
            <line
              x1={yearToX(king.birthYear)}
              x2={yearToX(king.deathYear)}
              y1={60}
              y2={60}
              stroke="#333"
              strokeWidth={2}
            />
            <circle cx={yearToX(king.birthYear)} cy={60} r={3} fill="#333" />
            <circle cx={yearToX(king.deathYear)} cy={60} r={3} fill="#333" />
          </>
        )}

        {/* reign bands */}
        {king.reigns.map((r, i) => (
          <g key={i}>
            <rect
              x={yearToX(Math.min(r.start, r.end))}
              y={reignBandY}
              width={Math.max(2, Math.abs(yearToX(r.end) - yearToX(r.start)))}
              height={reignBandH}
              fill="#d9b872"
              opacity={0.6}
              stroke="#a6863f"
            />
            <title>{r.noteJa ?? ""}</title>
          </g>
        ))}
        <text x={padL} y={reignBandY - 3} fontSize={11} fill="#6a5420">
          治世
        </text>

        {/* layer group separators + labels */}
        {layerOrder.map((layer) => {
          const y = layerYStart[layer];
          const h = layerLaneCount[layer] * laneH;
          if (!enabledLayers.has(layer)) return null;
          return (
            <g key={layer}>
              <rect
                x={padL}
                y={y - 4}
                width={plotW}
                height={h + 4}
                fill={LAYER_COLORS[layer]}
                opacity={0.05}
              />
              <text x={padL - 4} y={y + 10} textAnchor="end" fontSize={10} fill="#555">
                {LAYER_LABELS[layer]}
              </text>
            </g>
          );
        })}

        {/* events */}
        {eventsSorted.map((ev) => {
          const info = laneByEvent[ev.id];
          if (!info) return null;
          const cy = layerYStart[ev.layer] + info.row * laneH + 8;
          const x1 = yearToX(ev.startYear);
          const x2 = yearToX(ev.endYear ?? ev.startYear);
          const isSelected = selectedEventId === ev.id;
          const isHovered = hoveredEventId === ev.id;
          const color = LAYER_COLORS[ev.layer];
          const isInterp = ev.type === "interpretation";
          return (
            <g
              key={ev.id}
              onClick={() => onSelect(ev.id)}
              onMouseEnter={() => onHover(ev.id)}
              onMouseLeave={() => onHover(null)}
              style={{ cursor: "pointer" }}
            >
              {ev.endYear !== undefined && (
                <rect
                  x={x1}
                  y={cy - 3}
                  width={Math.max(2, x2 - x1)}
                  height={6}
                  fill={color}
                  opacity={isSelected ? 0.9 : 0.55}
                  strokeDasharray={isInterp ? "3 3" : undefined}
                  stroke={isInterp ? color : "none"}
                  rx={2}
                />
              )}
              <circle
                cx={x1}
                cy={cy}
                r={isSelected ? dotR + 2 : isHovered ? dotR + 1 : dotR}
                fill={isInterp ? "white" : color}
                stroke={color}
                strokeWidth={isInterp ? 2 : isSelected ? 2 : 1}
                strokeDasharray={isInterp ? "2 2" : undefined}
              />
              <title>
                {`${ev.yearLabel} · ${ev.description.slice(0, 70)}${
                  ev.description.length > 70 ? "…" : ""
                }`}
              </title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
