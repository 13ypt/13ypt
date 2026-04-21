import type { Actor, ActorId } from "./types";

export interface ActorEntry extends Actor {
  // keywords ordered most-specific-first; inference consumes them in order
  keywords: string[];
}

// Default dictionary used when a timeline doesn't provide its own
export const ACTORS: ActorEntry[] = [
  {
    id: "ptolemy-v",
    nameJa: "プトレマイオス5世エピファネス",
    nameEn: "Ptolemy V Epiphanes",
    lifespan: { birth: -210, death: -180 },
    keywords: ["プトレマイオス5世"],
  },
  {
    id: "ptolemy-vi",
    nameJa: "プトレマイオス6世フィロメトル",
    nameEn: "Ptolemy VI Philometor",
    lifespan: { birth: -186, death: -145 },
    keywords: ["プトレマイオス6世", "6世"],
  },
  {
    id: "ptolemy-vii",
    nameJa: "プトレマイオス7世ネオス・フィロパトル",
    nameEn: "Ptolemy VII Neos Philopator",
    lifespan: { birth: -161, death: -145 },
    keywords: ["プトレマイオス7世", "7世"],
  },
  {
    id: "ptolemy-viii",
    nameJa: "プトレマイオス8世エウエルゲテス2世",
    nameEn: "Ptolemy VIII Euergetes II",
    lifespan: { birth: -184, death: -116 },
    keywords: ["プトレマイオス8世", "8世", "エウエルゲテス2世"],
  },
  {
    id: "ptolemy-ix",
    nameJa: "プトレマイオス9世ソテル2世",
    nameEn: "Ptolemy IX Soter II",
    lifespan: { birth: -143, death: -81 },
    keywords: ["プトレマイオス9世", "9世"],
  },
  {
    id: "ptolemy-x",
    nameJa: "プトレマイオス10世アレクサンドロス1世",
    nameEn: "Ptolemy X Alexander I",
    lifespan: { birth: -140, death: -88 },
    keywords: ["プトレマイオス10世", "10世"],
  },
  {
    id: "cleopatra-i",
    nameJa: "クレオパトラ1世",
    nameEn: "Cleopatra I Syra",
    lifespan: { birth: -204, death: -176 },
    keywords: ["クレオパトラ1世"],
  },
  {
    id: "cleopatra-ii",
    nameJa: "クレオパトラ2世",
    nameEn: "Cleopatra II",
    lifespan: { birth: -185, death: -115 },
    keywords: ["クレオパトラ2世"],
  },
  {
    id: "cleopatra-iii",
    nameJa: "クレオパトラ3世",
    nameEn: "Cleopatra III",
    lifespan: { birth: -161, death: -101 },
    keywords: ["クレオパトラ3世"],
  },
  {
    id: "memphites",
    nameJa: "プトレマイオス・メンフィテス",
    nameEn: "Ptolemy Memphites",
    lifespan: { birth: -144, death: -130 },
    keywords: ["プトレマイオス・メンフィテス", "メンフィテス"],
  },
  {
    id: "soterichos",
    nameJa: "ソテリコス（王室近衛隊長）",
    nameEn: "Soterichos",
    role: "archisomatophylax",
    keywords: ["ソテリコス"],
  },
  {
    id: "demetrios-ii",
    nameJa: "デメトリオス2世（セレウコス朝）",
    nameEn: "Demetrios II Nikator",
    keywords: ["デメトリオス2世"],
  },
];

export function inferActors(text: string): ActorId[] {
  const hits = new Set<ActorId>();
  for (const a of ACTORS) {
    for (const k of a.keywords) {
      if (text.includes(k)) {
        hits.add(a.id);
        break;
      }
    }
  }
  return Array.from(hits);
}

export function getActor(id: ActorId): Actor | undefined {
  const a = ACTORS.find((x) => x.id === id);
  if (!a) return undefined;
  const { keywords: _k, ...rest } = a;
  return rest;
}

export function allActors(): Actor[] {
  return ACTORS.map(({ keywords: _k, ...rest }) => rest);
}
