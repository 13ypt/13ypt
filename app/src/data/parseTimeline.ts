import type {
  Actor,
  ActorId,
  Citation,
  CitationRef,
  HistoricalEvent,
  Layer,
  TimelineDataset,
} from "./types";
import { inferActors, ACTORS } from "./actors";
import { inferPlaceId, GAZETTEER } from "./places";

type Section = {
  title: string;
  level: number;
  lines: string[];
};

// Keyword → layer inference. Order matters: most-specific-first wins.
const LAYER_RULES: { layer: Layer; keywords: string[] }[] = [
  {
    layer: "animal-cult",
    keywords: ["アピス", "ムネヴィス", "聖獣", "セド祭"],
  },
  {
    layer: "religious",
    keywords: [
      "神殿",
      "奉献",
      "ホルス",
      "イシス",
      "神官",
      "神格化",
      "フィラントローパ",
      "戴冠式",
      "碑文",
      "石碑",
      "ヒエロス",
      "埋葬",
    ],
  },
  {
    layer: "political",
    keywords: [
      "即位",
      "摂政",
      "結婚",
      "共同統治",
      "単独",
      "追放",
      "帰還",
      "奪還",
      "介入",
      "内戦",
      "殺害",
      "戦死",
      "死去",
      "大赦",
      "恩赦",
      "勅令",
      "和解",
      "反撃",
      "襲撃",
    ],
  },
  {
    layer: "regional",
    keywords: ["巡幸", "東部砂漠", "鉱山", "地方"],
  },
];

const INTERPRETATION_MARKERS = [
  "とみられる",
  "可能性",
  "示唆",
  "扱う必要がある",
  "とされる",
  "伝承では",
  "考えられる",
  "目的があった",
];

function inferLayer(text: string): Layer {
  for (const rule of LAYER_RULES) {
    if (rule.keywords.some((k) => text.includes(k))) return rule.layer;
  }
  return "political";
}

function isInterpretation(text: string): boolean {
  return INTERPRETATION_MARKERS.some((m) => text.includes(m));
}

// ---- Year parsing (accepts 紀元前 / 前) -------------------------------

export interface ParsedYear {
  startYear: number;
  endYear?: number;
  approximate?: boolean;
  qualifier?: string;
}

export function parseYear(raw: string): ParsedYear {
  let s = raw.trim();
  s = s.replace(/紀元前/g, "前");
  const approximate = /ごろ|頃/.test(s);
  s = s.replace(/ごろ|頃/g, "").trim();
  s = s.replace(/[~～]/g, "〜");

  // Range with parenthetical qualifier at start, like "前131年（7〜9月頃）"
  // First strip trailing parenthetical to save as qualifier
  let outerQualifier = "";
  const parenTrail = s.match(/^(.+?)\s*（([^）]+)）\s*$/);
  if (parenTrail) {
    s = parenTrail[1].trim();
    outerQualifier = parenTrail[2].trim();
  }

  // Month/day trailing after the year, e.g. "前130年10月2日"
  const ymd = s.match(/^前(\d+)\s*年\s*(\d+月.+)$/);
  if (ymd) {
    return {
      startYear: -parseInt(ymd[1], 10),
      approximate,
      qualifier: [ymd[2], outerQualifier].filter(Boolean).join(" "),
    };
  }

  // Range: 前X〜(前)?Y年
  let m = s.match(/^前(\d+)\s*〜\s*前?(\d+)\s*年(.*)$/);
  if (m) {
    return {
      startYear: -parseInt(m[1], 10),
      endYear: -parseInt(m[2], 10),
      approximate,
      qualifier:
        [m[3].trim(), outerQualifier].filter(Boolean).join(" ") || undefined,
    };
  }

  // Range: 前X年（...）〜前?Y年 — already captured outerQualifier, fall through
  // Range: 前X年〜前Y年 when written with 年 in middle: 前131年〜130年
  m = s.match(/^前(\d+)\s*年\s*〜\s*前?(\d+)\s*年?(.*)$/);
  if (m) {
    return {
      startYear: -parseInt(m[1], 10),
      endYear: -parseInt(m[2], 10),
      approximate,
      qualifier:
        [m[3].trim(), outerQualifier].filter(Boolean).join(" ") || undefined,
    };
  }

  // Slash: 前X/Y年
  m = s.match(/^前(\d+)\s*\/\s*(\d+)\s*年(.*)$/);
  if (m) {
    const a = parseInt(m[1], 10);
    const b = parseInt(m[2], 10);
    return {
      startYear: -Math.max(a, b),
      endYear: -Math.min(a, b),
      approximate: true,
      qualifier:
        [m[3].trim(), outerQualifier].filter(Boolean).join(" ") || undefined,
    };
  }

  // Single: 前X年 [qualifier]
  m = s.match(/^前(\d+)\s*年(.*)$/);
  if (m) {
    return {
      startYear: -parseInt(m[1], 10),
      approximate,
      qualifier:
        [m[2].trim(), outerQualifier].filter(Boolean).join(" ") || undefined,
    };
  }

  return { startYear: 0, approximate };
}

// ---- Section splitting -------------------------------------------------

function splitSections(md: string): Section[] {
  const lines = md.split(/\r?\n/);
  const sections: Section[] = [];
  let current: Section | null = null;
  for (const line of lines) {
    const h = line.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      if (current) sections.push(current);
      current = { title: h[2].trim(), level: h[1].length, lines: [] };
    } else if (current) {
      current.lines.push(line);
    }
  }
  if (current) sections.push(current);
  return sections;
}

// ---- Citation parsing --------------------------------------------------

function parseCitationList(lines: string[]): Citation[] {
  const citations: Citation[] = [];
  for (const raw of lines) {
    const line = raw.trim();
    if (!line.startsWith("-")) continue;
    if (/^-{2,}$/.test(line)) continue;
    if (!/\d{4}/.test(line)) continue;
    const body = line.replace(/^-\s*/, "");
    let titleMatch = body.match(/\*([^*]+)\*/);
    if (!titleMatch) titleMatch = body.match(/_([^_]+)_/);
    const title = titleMatch ? titleMatch[1].trim() : "";
    const before = titleMatch
      ? body.substring(0, titleMatch.index!).trim()
      : body;
    const after = titleMatch
      ? body.substring(titleMatch.index! + titleMatch[0].length).trim()
      : "";
    const authors = before.replace(/\.$/, "").trim();
    const yearMatch = after.match(/(\d{4})/);
    const year = yearMatch ? parseInt(yearMatch[1], 10) : 0;
    const publication = after.replace(/^\.\s*/, "").replace(/\.$/, "").trim();
    const lastName = (authors.split(",")[0] || "").trim();
    const key = `${lastName} ${year}`;
    const id = `${lastName.toLowerCase().replace(/\s+/g, "-")}-${year}`;
    citations.push({ id, key, authors, year, title, publication });
  }
  return citations;
}

function parseCitationRefs(
  text: string,
  keyToId: Map<string, string>
): { refs: CitationRef[]; cleaned: string } {
  const refs: CitationRef[] = [];
  const matches = Array.from(text.matchAll(/\[([^\]]+)\]/g));
  for (const m of matches) {
    const content = m[1].trim();
    if (!/\d{4}/.test(content) && !content.includes(":")) {
      refs.push({ citationId: "", rawLabel: content });
      continue;
    }
    const idx = content.indexOf(":");
    const key = (idx === -1 ? content : content.slice(0, idx)).trim();
    const pages = idx === -1 ? undefined : content.slice(idx + 1).trim();
    const id = keyToId.get(key);
    if (id) refs.push({ citationId: id, pages });
    else refs.push({ citationId: "", rawLabel: content });
  }
  const cleaned = text.replace(/\[[^\]]+\]/g, "").trim();
  return { refs, cleaned };
}

// ---- Actor dictionary section -----------------------------------------

function parseActorList(lines: string[]): Actor[] {
  const actors: Actor[] = [];
  for (const raw of lines) {
    const line = raw.trim();
    if (!line.startsWith("-")) continue;
    const body = line.replace(/^-\s*/, "");
    const m = body.match(/^\*\*([^*]+)\*\*\s*[：:]\s*(.+)$/);
    if (!m) continue;
    actors.push({ id: m[1].trim(), nameJa: m[2].trim() });
  }
  return actors;
}

// ---- Event row parsing -------------------------------------------------

function parseBulletEvents(
  lines: string[],
  opts: {
    sectionTitle: string;
    keyToId: Map<string, string>;
    idPrefix: string;
  }
): HistoricalEvent[] {
  const events: HistoricalEvent[] = [];
  let counter = 0;
  for (const raw of lines) {
    const line = raw.trim();
    if (!line.startsWith("-")) continue;
    if (/^-{2,}$/.test(line)) continue;
    const body = line.replace(/^-\s*/, "").trim();
    if (!body) continue;
    // Expect **year**: content
    const m = body.match(/^\*\*([^*]+)\*\*\s*[：:]\s*(.+)$/);
    if (!m) continue;
    const yearCell = m[1].trim();
    const rest = m[2].trim();
    const py = parseYear(yearCell);
    if (!py.startYear) continue;
    const { refs, cleaned } = parseCitationRefs(rest, opts.keyToId);
    const description = cleaned || rest;
    const actors = inferActors(description);
    const placeId = inferPlaceId(description);
    counter++;
    events.push({
      id: `${opts.idPrefix}-${counter}`,
      startYear: py.startYear,
      endYear: py.endYear,
      yearLabel: yearCell,
      approximate: py.approximate,
      qualifier: py.qualifier,
      layer: inferLayer(description),
      section: opts.sectionTitle,
      type: isInterpretation(description) ? "interpretation" : "fact",
      description,
      placeId,
      actors: actors.length ? actors : undefined,
      citationRefs: refs,
    });
  }
  return events;
}

// ---- Slug util --------------------------------------------------------

function slug(s: string): string {
  return s
    .replace(/[^\p{Letter}\p{Number}]+/gu, "-")
    .replace(/^-|-$/g, "")
    .toLowerCase();
}

// ---- Main parser ------------------------------------------------------

export function parseTimelineMarkdown(
  md: string,
  id: string
): TimelineDataset {
  const sections = splitSections(md);
  const h1 = sections.find((s) => s.level === 1);
  const title = h1?.title ?? "Timeline";

  const refSection = sections.find((s) => s.title === "参考文献");
  const citations = refSection ? parseCitationList(refSection.lines) : [];
  const keyToId = new Map<string, string>(citations.map((c) => [c.key, c.id]));

  const personSection = sections.find((s) => /^人物/.test(s.title));
  const explicitActors = personSection
    ? parseActorList(personSection.lines)
    : [];

  const events: HistoricalEvent[] = [];
  const skipTitles = new Set(["人物", "参考文献", "補注"]);
  for (const sec of sections) {
    if (sec.level !== 2) continue;
    if ([...skipTitles].some((t) => sec.title.startsWith(t))) continue;
    const evs = parseBulletEvents(sec.lines, {
      sectionTitle: sec.title,
      keyToId,
      idPrefix: `${id}-${slug(sec.title)}`,
    });
    events.push(...evs);
  }

  const usedPlaceIds = new Set<string>();
  for (const ev of events) if (ev.placeId) usedPlaceIds.add(ev.placeId);
  const places = GAZETTEER.filter((g) => usedPlaceIds.has(g.id)).map(
    ({ keywords: _k, ...rest }) => rest
  );

  const usedActors = new Set<ActorId>();
  for (const ev of events) ev.actors?.forEach((a) => usedActors.add(a));
  const allActors = explicitActors.length
    ? explicitActors
    : ACTORS.filter((a) => usedActors.has(a.id)).map(
        ({ keywords: _k, ...rest }) => rest
      );
  // Ensure every used actor is represented
  for (const id of usedActors) {
    if (!allActors.some((a) => a.id === id)) {
      const found = ACTORS.find((a) => a.id === id);
      if (found) {
        const { keywords: _k, ...rest } = found;
        allActors.push(rest);
      }
    }
  }

  const transparency = sections.find((s) => s.title === "補注");
  const transparencyNote = transparency
    ? transparency.lines.map((l) => l.trim()).filter(Boolean).join(" ")
    : undefined;

  const years = events.flatMap((e) =>
    e.endYear !== undefined ? [e.startYear, e.endYear] : [e.startYear]
  );
  const start = years.length ? Math.min(...years) - 2 : -200;
  const end = years.length ? Math.max(...years) + 2 : -50;

  // Extract title text + Japanese short name
  const titleJa = title.replace(/\s*[（(][^）)]*[）)]\s*$/u, "").trim();

  return {
    id,
    title,
    titleJa,
    dateRange: { start, end },
    actors: allActors,
    events,
    places,
    citations,
    transparencyNote,
  };
}
