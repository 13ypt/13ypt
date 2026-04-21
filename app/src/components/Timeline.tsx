import type { HistoricalEvent, King } from "../data/types";

const CATEGORY_COLORS: Record<string, string> = {
  reign: "#b38b3f",
  war: "#c04040",
  diplomacy: "#3c6fb4",
  religion: "#7a3ca1",
  building: "#2f8f6e",
  family: "#c96a9a",
  decree: "#5b7d2f",
  revolt: "#e07c2b",
};

interface Props {
  king: King;
  selectedEventId: string | null;
  hoveredEventId: string | null;
  onSelect: (id: string) => void;
  onHover: (id: string | null) => void;
}

export default function Timeline({
  king,
  selectedEventId,
  hoveredEventId,
  onSelect,
  onHover,
}: Props) {
  const minYear = king.birthYear - 2;
  const maxYear = king.deathYear + 2;
  const span = maxYear - minYear;

  const width = 1100;
  const height = 190;
  const padL = 40;
  const padR = 20;
  const plotW = width - padL - padR;

  const yearToX = (y: number) => padL + ((y - minYear) / span) * plotW;

  // decade ticks
  const ticks: number[] = [];
  const startTick = Math.ceil(minYear / 10) * 10;
  for (let y = startTick; y <= maxYear; y += 10) ticks.push(y);

  const eventsSorted = [...king.events].sort((a, b) => a.startYear - b.startYear);

  // simple lane allocation to avoid overlap
  const lanes: { end: number }[] = [];
  const eventLanes: Record<string, number> = {};
  for (const ev of eventsSorted) {
    const start = ev.startYear;
    const end = ev.endYear ?? ev.startYear;
    let lane = 0;
    while (lane < lanes.length && lanes[lane].end >= start - 1) lane++;
    if (lane === lanes.length) lanes.push({ end });
    else lanes[lane].end = end;
    eventLanes[ev.id] = lane;
  }
  const laneCount = Math.max(lanes.length, 1);
  const reignBandY = 80;
  const reignBandH = 22;
  const eventsTop = reignBandY + reignBandH + 14;
  const laneH = 18;
  const dotR = 7;

  const formatYear = (y: number) => (y < 0 ? `${-y} BCE` : `${y} CE`);

  return (
    <div className="timeline-wrap">
      <svg
        viewBox={`0 0 ${width} ${Math.max(height, eventsTop + laneCount * laneH + 10)}`}
        className="timeline-svg"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* axis */}
        <line
          x1={padL}
          x2={width - padR}
          y1={60}
          y2={60}
          stroke="#888"
          strokeWidth={1}
        />
        {ticks.map((t) => (
          <g key={t}>
            <line
              x1={yearToX(t)}
              x2={yearToX(t)}
              y1={56}
              y2={64}
              stroke="#888"
            />
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

        {/* life span */}
        <line
          x1={yearToX(king.birthYear)}
          x2={yearToX(king.deathYear)}
          y1={60}
          y2={60}
          stroke="#333"
          strokeWidth={2}
        />
        <circle cx={yearToX(king.birthYear)} cy={60} r={3.5} fill="#333" />
        <circle cx={yearToX(king.deathYear)} cy={60} r={3.5} fill="#333" />

        {/* reign bands */}
        {king.reigns.map((r, i) => (
          <g key={i}>
            <rect
              x={yearToX(r.start)}
              y={reignBandY}
              width={yearToX(r.end) - yearToX(r.start)}
              height={reignBandH}
              fill="#d9b872"
              opacity={0.55}
              stroke="#a6863f"
            />
            <title>{r.noteJa ?? ""}</title>
          </g>
        ))}
        <text x={padL} y={reignBandY - 4} fontSize={11} fill="#6a5420">
          治世
        </text>

        {/* events */}
        {eventsSorted.map((ev) => {
          const lane = eventLanes[ev.id];
          const cy = eventsTop + lane * laneH;
          const x1 = yearToX(ev.startYear);
          const x2 = yearToX(ev.endYear ?? ev.startYear);
          const isSelected = selectedEventId === ev.id;
          const isHovered = hoveredEventId === ev.id;
          const color = CATEGORY_COLORS[ev.category] ?? "#666";
          return (
            <g
              key={ev.id}
              className="ev-g"
              onClick={() => onSelect(ev.id)}
              onMouseEnter={() => onHover(ev.id)}
              onMouseLeave={() => onHover(null)}
              style={{ cursor: "pointer" }}
            >
              {ev.endYear !== undefined && (
                <rect
                  x={x1}
                  y={cy - 4}
                  width={Math.max(2, x2 - x1)}
                  height={8}
                  fill={color}
                  opacity={isSelected ? 0.9 : 0.6}
                  rx={2}
                />
              )}
              <circle
                cx={x1}
                cy={cy}
                r={isSelected ? dotR + 2 : isHovered ? dotR + 1 : dotR}
                fill={color}
                stroke={isSelected ? "#111" : "white"}
                strokeWidth={isSelected ? 2 : 1}
              />
              <title>
                {`${formatYear(ev.startYear)}${
                  ev.endYear ? "–" + formatYear(ev.endYear) : ""
                } · ${ev.titleJa}`}
              </title>
            </g>
          );
        })}
      </svg>

      <div className="legend">
        {Object.entries(CATEGORY_COLORS).map(([k, v]) => (
          <span key={k} className="legend-item">
            <span className="legend-dot" style={{ background: v }} />
            {legendLabel(k)}
          </span>
        ))}
      </div>
    </div>
  );
}

function legendLabel(key: string) {
  const map: Record<string, string> = {
    reign: "即位／治世",
    war: "戦争",
    diplomacy: "外交",
    religion: "宗教",
    building: "建造",
    family: "王家・家族",
    decree: "勅令・法",
    revolt: "反乱",
  };
  return map[key] ?? key;
}

export type { HistoricalEvent };
