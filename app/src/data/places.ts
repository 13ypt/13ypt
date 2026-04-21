import type { Place } from "./types";

// Gazetteer: known places with keyword aliases used to infer location from event text.
// Order matters — more specific entries should come first so their keywords match
// before broader ones (e.g. "アレクサンドリア" before "エジプト").
export interface GazetteerEntry extends Place {
  keywords: string[];
}

export const GAZETTEER: GazetteerEntry[] = [
  {
    id: "alexandria",
    name: "Alexandria",
    nameJa: "アレクサンドリア",
    lat: 31.2001,
    lng: 29.9187,
    keywords: ["アレクサンドリア"],
  },
  {
    id: "memphis",
    name: "Memphis",
    nameJa: "メンフィス",
    lat: 29.8440,
    lng: 31.2547,
    keywords: ["メンフィス"],
  },
  {
    id: "edfu",
    name: "Edfu",
    nameJa: "エドフ",
    lat: 24.9781,
    lng: 32.8733,
    keywords: ["エドフ"],
  },
  {
    id: "hermonthis",
    name: "Hermonthis (Armant)",
    nameJa: "ヘルモンティス（アルマント）",
    lat: 25.6178,
    lng: 32.5383,
    keywords: ["ヘルモンティス", "ブケウム"],
  },
  {
    id: "fayyum",
    name: "Fayyum",
    nameJa: "ファイユーム",
    lat: 29.3084,
    lng: 30.8428,
    approximate: true,
    keywords: ["ファイユーム"],
  },
  {
    id: "thebes",
    name: "Thebes",
    nameJa: "テーベ",
    lat: 25.7188,
    lng: 32.6103,
    keywords: ["テーベ"],
  },
  {
    id: "cyrene",
    name: "Cyrene",
    nameJa: "キュレネ",
    lat: 32.8250,
    lng: 21.8583,
    keywords: ["キュレネ", "キュレナイカ"],
  },
  {
    id: "cyprus",
    name: "Cyprus",
    nameJa: "キプロス",
    lat: 34.9229,
    lng: 33.1469,
    approximate: true,
    keywords: ["キプロス", "キュプロス", "パフォス"],
  },
  {
    id: "rome",
    name: "Rome",
    nameJa: "ローマ",
    lat: 41.9028,
    lng: 12.4964,
    keywords: ["ローマ"],
  },
  {
    id: "syria",
    name: "Syria (Seleucid realm)",
    nameJa: "シリア",
    lat: 35.0,
    lng: 37.0,
    approximate: true,
    keywords: ["シリア", "セレウコス"],
  },
  {
    id: "aegean",
    name: "Aegean Sea",
    nameJa: "エーゲ海",
    lat: 37.5,
    lng: 25.0,
    approximate: true,
    keywords: ["エーゲ海"],
  },
  {
    id: "cyzicus",
    name: "Cyzicus",
    nameJa: "キュジコス",
    lat: 40.3833,
    lng: 27.8833,
    keywords: ["キュジコス"],
  },
];

export function inferPlaceId(text: string): string | undefined {
  for (const g of GAZETTEER) {
    if (g.keywords.some((k) => text.includes(k))) return g.id;
  }
  return undefined;
}

export function getPlace(id: string): Place | undefined {
  const g = GAZETTEER.find((p) => p.id === id);
  if (!g) return undefined;
  const { keywords: _k, ...place } = g;
  return place;
}

export function allPlaces(): Place[] {
  return GAZETTEER.map(({ keywords: _k, ...rest }) => rest);
}
