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
    keywords: ["キュレネ", "キュレナイカ", "キレネ"],
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
  {
    id: "ombos",
    name: "Ombos (Kom Ombo)",
    nameJa: "オンボイ（コム・オンボ）",
    lat: 24.4520,
    lng: 32.9233,
    keywords: ["オンボイ", "コム・オンボ"],
  },
  {
    id: "heracleopolis",
    name: "Heracleopolis Magna",
    nameJa: "ヘラクレオポリス",
    lat: 29.0859,
    lng: 30.9328,
    keywords: ["ヘラクレオポリス"],
  },
  {
    id: "antaiopolis",
    name: "Antaiopolis (Qaw el-Kebir)",
    nameJa: "アンタイオポリス",
    lat: 26.8903,
    lng: 31.5094,
    keywords: ["アンタイオポリス"],
  },
  {
    id: "coptos",
    name: "Coptos (Qift)",
    nameJa: "コプトス",
    lat: 25.9957,
    lng: 32.8183,
    keywords: ["コプトス"],
  },
  {
    id: "diospolis-parva",
    name: "Diospolis Parva (Hou)",
    nameJa: "ディオスポリス・パルヴァ",
    lat: 26.0208,
    lng: 32.2658,
    keywords: ["ディオスポリス・パルヴァ"],
  },
  {
    id: "philae",
    name: "Philae (Agilkia)",
    nameJa: "フィラエ",
    lat: 24.0257,
    lng: 32.8847,
    keywords: ["フィラエ"],
  },
  {
    id: "hatshepsut-temple",
    name: "Mortuary Temple of Hatshepsut (Deir el-Bahari)",
    nameJa: "ハトシェプスト女王葬祭殿",
    lat: 25.7381,
    lng: 32.6064,
    keywords: ["ハトシェプスト"],
  },
  {
    id: "medinet-habu",
    name: "Medinet Habu",
    nameJa: "メディネト・ハブ",
    lat: 25.7197,
    lng: 32.6006,
    keywords: ["メディネト・ハブ", "カスル・エル＝アグーズ", "カスル・エル=アグーズ"],
  },
  {
    id: "itanos",
    name: "Itanos (Crete)",
    nameJa: "イタノス",
    lat: 35.2833,
    lng: 26.2833,
    keywords: ["イタノス"],
  },
  {
    id: "thera",
    name: "Thera (Santorini)",
    nameJa: "テラ",
    lat: 36.4072,
    lng: 25.4569,
    keywords: ["テラ"],
  },
  {
    id: "methana",
    name: "Methana",
    nameJa: "メタナ",
    lat: 37.5833,
    lng: 23.3833,
    keywords: ["メタナ"],
  },
  {
    id: "india",
    name: "India (Indian Ocean routes)",
    nameJa: "インド",
    lat: 13.0,
    lng: 75.0,
    approximate: true,
    keywords: ["インド"],
  },
  // Broader regional / cross-cutting areas are listed LAST so specific cities
  // (e.g. コプトス 東部砂漠への入り口) take precedence in inference.
  {
    id: "eastern-desert",
    name: "Eastern Desert",
    nameJa: "東部砂漠",
    lat: 26.5,
    lng: 33.0,
    approximate: true,
    keywords: ["東部砂漠"],
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
