import type { HistoricalEvent, Layer } from "../data/types";

export const LAYER_COLORS: Record<Layer, string> = {
  political: "#c04040",
  regional: "#2f8f6e",
  religious: "#7a3ca1",
  "animal-cult": "#d98c3d",
};

export const LAYER_LABELS: Record<Layer, string> = {
  political: "政治",
  regional: "地域・建築",
  religious: "宗教",
  "animal-cult": "動物崇拝・聖獣",
};

const LAYER_ORDER: Layer[] = [
  "political",
  "regional",
  "religious",
  "animal-cult",
];

interface Props {
  startYear: number;
  endYear: number;
  reigns?: { start: number; end: number; noteJa?: string }[];
  events: HistoricalEvent[]; // already filtered
  enabledLayers: Set<Layer>;
  selectedEventId: string | null;
  hoveredEventId: string | null;
  onSelect: (id: string) => void;
  onHover: (id: string | null) => void;
  onToggleLayer: (layer: Layer) => void;
}

const formatYear = (y: number) => (y < 0 ? `前${-y}年` : `${y}年`);

export default function Timeline({
  startYear,
  endYear,
  reigns,
  events,
  enabledLayers,
  selectedEventId,
  hoveredEventId,
  onSelect,
  onHover,
  onToggleLayer,
}: Props) {
  const minYear = startYear;
  const maxYear = endYear;
  const span = Math.max(1, maxYear - minYear);

  const width = 1100;
  const padL = 50;
  const padR = 20;
  const plotW = width - padL - padR;
  const yearToX = (y: number) => padL + ((y - minYear) / span) * plotW;

  const ticks: number[] = [];
  const tickStep = span > 80 ? 20 : span > 30 ? 10 : 5;
  const startTick = Math.ceil(minYear / tickStep) * tickStep;
  for (let y = startTick; y <= maxYear; y += tickStep) ticks.push(y);

  const eventsSorted = [...events].sort((a, b) => a.startYear - b.startYear);

  // An event appears in its primary layer AND any extraLayers — so the same
  // event can surface in multiple rows (e.g. a 宗教 event also showing up in
  // 政治 if it's a governing-strategy moment).
  const layersOfEvent = (ev: HistoricalEvent): Layer[] => {
    const all = [ev.layer, ...(ev.extraLayers ?? [])];
    // dedupe while keeping order
    return Array.from(new Set(all));
  };

  // Allocate lanes per layer — each (eventId, layer) pair has its own lane.
  const laneByEventLayer: Record<string, number> = {};
  const keyFor = (id: string, layer: Layer) => `${layer}::${id}`;
  const layerLaneCount: Record<Layer, number> = {
    political: 0,
    regional: 0,
    religious: 0,
    "animal-cult": 0,
  };
  for (const layer of LAYER_ORDER) {
    const lanesEnd: number[] = [];
    const evsInLayer = eventsSorted.filter((e) =>
      layersOfEvent(e).includes(layer)
    );
    for (const ev of evsInLayer) {
      const start = ev.startYear;
      const end = ev.endYear ?? ev.startYear;
      let lane = 0;
      while (lane < lanesEnd.length && lanesEnd[lane] >= start - 1) lane++;
      if (lane === lanesEnd.length) lanesEnd.push(end);
      else lanesEnd[lane] = end;
      laneByEventLayer[keyFor(ev.id, layer)] = lane;
    }
    layerLaneCount[layer] = enabledLayers.has(layer)
      ? Math.max(1, lanesEnd.length)
      : 0;
  }

  const reignBandY = 78;
  const reignBandH = 18;
  const groupGap = 10;
  const laneH = 16;
  const dotR = 6;

  const layerYStart: Record<Layer, number> = {} as Record<Layer, number>;
  let cursor = reignBandY + (reigns && reigns.length ? reignBandH + groupGap : groupGap) + 4;
  for (const layer of LAYER_ORDER) {
    layerYStart[layer] = cursor;
    if (enabledLayers.has(layer)) {
      cursor += layerLaneCount[layer] * laneH + groupGap;
    }
  }
  const svgHeight = cursor + 10;

  return (
    <div className="timeline-wrap">
      <div className="layer-toggles">
        {LAYER_ORDER.map((l) => (
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

        {reigns && reigns.length > 0 && (
          <>
            {reigns.map((r, i) => (
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
            <text x={padL - 4} y={reignBandY + 13} textAnchor="end" fontSize={10} fill="#6a5420">
              治世
            </text>
          </>
        )}

        {LAYER_ORDER.map((layer) => {
          if (!enabledLayers.has(layer)) return null;
          const y = layerYStart[layer];
          const h = layerLaneCount[layer] * laneH;
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

        {eventsSorted.flatMap((ev) => {
          const layers = layersOfEvent(ev).filter((l) => enabledLayers.has(l));
          return layers.map((layer) => {
            const lane = laneByEventLayer[keyFor(ev.id, layer)] ?? 0;
            const cy = layerYStart[layer] + lane * laneH + 8;
            const x1 = yearToX(ev.startYear);
            const x2 = yearToX(ev.endYear ?? ev.startYear);
            const isSelected = selectedEventId === ev.id;
            const isHovered = hoveredEventId === ev.id;
            const color = LAYER_COLORS[layer];
            const isExtra = layer !== ev.layer;
            const isInterp = ev.type === "interpretation";
            return (
              <g
                key={`${ev.id}-${layer}`}
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
                    opacity={isSelected ? 0.9 : isExtra ? 0.35 : 0.55}
                    strokeDasharray={isInterp ? "3 3" : undefined}
                    stroke={isInterp ? color : "none"}
                    rx={2}
                  />
                )}
                <circle
                  cx={x1}
                  cy={cy}
                  r={isSelected ? dotR + 2 : isHovered ? dotR + 1 : dotR}
                  fill={isInterp ? "white" : isExtra ? "white" : color}
                  stroke={color}
                  strokeWidth={isInterp ? 2 : isExtra ? 1.5 : isSelected ? 2 : 1}
                  strokeDasharray={isInterp ? "2 2" : undefined}
                  opacity={isExtra ? 0.85 : 1}
                />
                <title>
                  {`${ev.yearLabel}${isExtra ? " (関連)" : ""} · ${ev.description.slice(0, 80)}${
                    ev.description.length > 80 ? "…" : ""
                  }`}
                </title>
              </g>
            );
          });
        })}
      </svg>
    </div>
  );
}
