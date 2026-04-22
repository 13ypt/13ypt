export type Layer = "political" | "regional" | "religious" | "animal-cult";
export type EventType = "fact" | "interpretation";

export type ActorId = string; // e.g. "ptolemy-viii"

export interface Actor {
  id: ActorId;
  nameJa: string;
  nameEn?: string;
  role?: string;
  lifespan?: { birth?: number; death?: number };
}

export interface Citation {
  id: string;
  key: string; // "Grainger 2024"
  authors: string;
  year: number | string;
  title: string;
  publication: string;
  pages?: string;
  url?: string;
  note?: string;
}

export interface CitationRef {
  citationId: string;
  pages?: string;
  rawLabel?: string; // e.g. "補注参照"
}

export interface AlternativeInterpretation {
  id: string;
  text: string;
  citationRefs: CitationRef[];
}

export interface Place {
  id: string;
  name: string;
  nameJa: string;
  lat: number;
  lng: number;
  approximate?: boolean;
}

export interface HistoricalEvent {
  id: string;
  // chronology
  startYear: number;
  endYear?: number;
  yearLabel: string; // original "前145年 夏" string
  approximate?: boolean;
  qualifier?: string; // "夏", "7月28日", "以降", "後半"
  // semantic axis
  layer: Layer;           // primary layer (from section)
  extraLayers?: Layer[];  // additional layers inferred from keywords
  section: string; // e.g. "エジプト王として再即位"
  type: EventType;
  // content
  description: string;
  placeId?: string;
  actors?: ActorId[];
  citationRefs: CitationRef[];
  alternatives?: AlternativeInterpretation[];
}

export interface CharacterNote {
  label: string;
  text: string;
  citationRefs: CitationRef[];
}

export interface King {
  id: string;
  name: string;
  nameJa: string;
  epithet?: string;
  epithetJa?: string;
  headerMeta: { label: string; value: string }[]; // 父, 母, 兄, etc.
  reignSummary: string[]; // lines from 在位 section
  reigns: { start: number; end: number; noteJa?: string }[];
  birthYear?: number;
  deathYear?: number;
  events: HistoricalEvent[];
  places: Place[];
  citations: Citation[];
  transparencyNote?: string;
  characterNotes?: { title: string; intro?: string; items: CharacterNote[] };
}

export interface TimelineDataset {
  id: string;
  title: string;
  titleJa: string;
  summaryJa?: string;
  dateRange: { start: number; end: number };
  actors: Actor[];
  events: HistoricalEvent[];
  places: Place[];
  citations: Citation[];
  transparencyNote?: string;
}

export type ViewDescriptor =
  | { kind: "king"; id: string; labelJa: string; king: King }
  | {
      kind: "timeline";
      id: string;
      labelJa: string;
      timeline: TimelineDataset;
    };
