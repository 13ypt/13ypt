export type EventCategory =
  | "reign"
  | "war"
  | "diplomacy"
  | "religion"
  | "building"
  | "family"
  | "decree"
  | "revolt";

export interface Citation {
  id: string;
  authors: string;
  year: number | string;
  title: string;
  publication: string;
  pages?: string;
  url?: string;
  note?: string;
}

export interface Place {
  id: string;
  name: string;
  nameJa: string;
  lat: number;
  lng: number;
}

export interface HistoricalEvent {
  id: string;
  startYear: number; // BCE as negative integer (e.g., -170 for 170 BCE)
  endYear?: number;
  placeId: string;
  title: string;
  titleJa: string;
  summary: string;
  summaryJa: string;
  category: EventCategory;
  citationIds: string[];
  stateOfCountryJa?: string;
  stateOfCountry?: string;
}

export interface King {
  id: string;
  name: string;
  nameJa: string;
  epithet: string;
  epithetJa: string;
  birthYear: number;
  deathYear: number;
  reigns: { start: number; end: number; noteJa?: string }[];
  events: HistoricalEvent[];
  places: Place[];
  citations: Citation[];
}
