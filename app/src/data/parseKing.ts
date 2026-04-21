import type {
  King,
  HistoricalEvent,
  Citation,
  CitationRef,
  Layer,
  CharacterNote,
} from "./types";
import { inferPlaceId, getPlace, GAZETTEER } from "./places";

type Section = {
  title: string;
  level: number;
  lines: string[];
};

const LAYER_BY_SECTION: Record<string, Layer> = {
  政治的事件: "political",
  "地域・建築": "regional",
  宗教的動向: "religious",
};

const INTERPRETATION_MARKERS = [
  "解釈",
  "演出として",
  "とみられる",
  "可能性",
  "示唆",
  "理解されることが多い",
  "扱う必要がある",
  "伝承では",
];

function isInterpretation(text: string): boolean {
  return INTERPRETATION_MARKERS.some((m) => text.includes(m));
}

// ---- Year parsing ------------------------------------------------------

export interface ParsedYear {
  startYear: number;
  endYear?: number;
  approximate?: boolean;
  qualifier?: string;
}

export function parseYear(raw: string): ParsedYear {
  let s = raw.trim();
  const approximate = /ごろ|頃/.test(s);
  s = s.replace(/ごろ|頃/g, "").trim();
  s = s.replace(/[~～]/g, "〜");

  // Range: 前X〜(前)?Y年
  let m = s.match(/^前(\d+)\s*〜\s*前?(\d+)\s*年(.*)$/);
  if (m) {
    return {
      startYear: -parseInt(m[1], 10),
      endYear: -parseInt(m[2], 10),
      approximate,
      qualifier: m[3].trim() || undefined,
    };
  }

  // Slash: 前X/Y年 — ambiguous Egyptian year boundary
  m = s.match(/^前(\d+)\s*\/\s*(\d+)\s*年(.*)$/);
  if (m) {
    const a = parseInt(m[1], 10);
    const b = parseInt(m[2], 10);
    return {
      startYear: -Math.max(a, b),
      endYear: -Math.min(a, b),
      approximate: true,
      qualifier: m[3].trim() || undefined,
    };
  }

  // Single: 前X年 [qualifier]
  m = s.match(/^前(\d+)\s*年(.*)$/);
  if (m) {
    return {
      startYear: -parseInt(m[1], 10),
      approximate,
      qualifier: m[2].trim() || undefined,
    };
  }

  return { startYear: 0, approximate };
}

// ---- Section / line splitting -----------------------------------------

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
    // Skip horizontal-rule separators like `---`
    if (/^-{2,}$/.test(line)) continue;
    // Require the entry to contain a 4-digit year somewhere
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
): CitationRef[] {
  const refs: CitationRef[] = [];
  const matches = Array.from(text.matchAll(/\[([^\]]+)\]/g));
  for (const m of matches) {
    const content = m[1].trim();
    // Non-citation bracket like [補注参照]
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
  return refs;
}

// ---- Table parsing -----------------------------------------------------

interface Row {
  cells: string[];
}

function parseMarkdownTables(lines: string[]): Row[][] {
  const tables: Row[][] = [];
  let current: Row[] | null = null;

  const flush = () => {
    if (current && current.length) tables.push(current);
    current = null;
  };

  for (const raw of lines) {
    const line = raw.trim();
    const isTableRow = line.startsWith("|") && line.endsWith("|");
    if (!isTableRow) {
      flush();
      continue;
    }
    const cells = line
      .slice(1, -1)
      .split("|")
      .map((c) => c.trim());
    // Skip separator row like | --- | --- |
    if (cells.every((c) => /^:?-+:?$/.test(c))) continue;
    if (!current) current = [];
    current.push({ cells });
  }
  flush();
  return tables;
}

function rowsToEvents(
  rows: Row[],
  opts: {
    layer: Layer;
    section: string;
    keyToId: Map<string, string>;
    idPrefix: string;
  }
): HistoricalEvent[] {
  const events: HistoricalEvent[] = [];
  // First row is the header (年代 / できごと / 出典)
  const dataRows = rows.slice(1);
  dataRows.forEach((row, i) => {
    const yearCell = row.cells[0] ?? "";
    const eventCell = row.cells[1] ?? "";
    const sourceCell = row.cells[2] ?? "";
    if (!yearCell || !eventCell) return;
    const py = parseYear(yearCell);
    const refs = parseCitationRefs(sourceCell, opts.keyToId);
    const placeId = inferPlaceId(eventCell);
    events.push({
      id: `${opts.idPrefix}-${i + 1}`,
      startYear: py.startYear,
      endYear: py.endYear,
      yearLabel: yearCell,
      approximate: py.approximate,
      qualifier: py.qualifier,
      layer: opts.layer,
      section: opts.section,
      type: isInterpretation(eventCell) ? "interpretation" : "fact",
      description: eventCell,
      placeId,
      citationRefs: refs,
    });
  });
  return events;
}

// ---- Header (bio) parsing ----------------------------------------------

function parseBioLines(lines: string[]): {
  reignSummary: string[];
  headerMeta: { label: string; value: string }[];
  epithetJa?: string;
} {
  const reignSummary: string[] = [];
  const headerMeta: { label: string; value: string }[] = [];
  let inReign = false;
  let epithetJa: string | undefined;
  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      inReign = false;
      continue;
    }
    const m = line.match(/^\*\*([^*]+)\*\*\s*[：:]\s*(.*)$/);
    if (m) {
      const label = m[1].trim();
      const value = m[2].trim();
      if (label === "在位") {
        inReign = true;
        if (value) reignSummary.push(value);
      } else {
        inReign = false;
        if (label === "別名") epithetJa = value;
        headerMeta.push({ label, value });
      }
      continue;
    }
    if (inReign && line.startsWith("-")) {
      reignSummary.push(line.replace(/^-\s*/, "").trim());
    }
  }
  return { reignSummary, headerMeta, epithetJa };
}

function extractReigns(
  summary: string[]
): { start: number; end: number; noteJa?: string }[] {
  const out: { start: number; end: number; noteJa?: string }[] = [];
  for (const s of summary) {
    const range = s.match(/前(\d+)\s*[〜~～]\s*前?(\d+)\s*年/);
    if (range) {
      out.push({
        start: -parseInt(range[1], 10),
        end: -parseInt(range[2], 10),
        noteJa: s,
      });
      continue;
    }
    const single = s.match(/前(\d+)\s*年/);
    if (single) {
      const y = -parseInt(single[1], 10);
      out.push({ start: y, end: y, noteJa: s });
    }
  }
  return out;
}

function parseNameHeader(title: string): {
  nameJa: string;
  name: string;
  epithet?: string;
} {
  const m = title.match(/^([^（(]+)[（(]([^）)]+)[）)]/);
  if (!m) return { nameJa: title, name: title };
  const nameJa = m[1].trim();
  const inside = m[2].trim();
  const parts = inside.split(/\s*\/\s*/);
  return {
    nameJa,
    name: parts[0].trim(),
    epithet: parts[1]?.trim(),
  };
}

// ---- Character notes ---------------------------------------------------

function parseCharacterNotes(
  lines: string[],
  keyToId: Map<string, string>
): { intro?: string; items: CharacterNote[] } {
  const items: CharacterNote[] = [];
  const introBuf: string[] = [];
  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;
    if (/^-{2,}$/.test(line)) continue; // skip horizontal rule
    if (line.startsWith("-")) {
      const body = line.replace(/^-\s*/, "");
      if (!body) continue;
      const m = body.match(/^\*\*([^*]+)\*\*\s*[：:]\s*(.*)$/);
      if (m) {
        const label = m[1].trim();
        const rest = m[2].trim();
        const refs = parseCitationRefs(rest, keyToId);
        items.push({ label, text: rest, citationRefs: refs });
      } else {
        const refs = parseCitationRefs(body, keyToId);
        items.push({ label: "", text: body, citationRefs: refs });
      }
    } else {
      introBuf.push(line);
    }
  }
  return { intro: introBuf.length ? introBuf.join(" ") : undefined, items };
}

// ---- Main parser -------------------------------------------------------

function slug(s: string): string {
  return s
    .replace(/[^\p{Letter}\p{Number}]+/gu, "-")
    .replace(/^-|-$/g, "")
    .toLowerCase();
}

export function parseKingMarkdown(md: string, kingId: string): King {
  const sections = splitSections(md);

  const h1 = sections.find((s) => s.level === 1);
  const nameParts = h1
    ? parseNameHeader(h1.title)
    : { nameJa: "Unknown", name: "Unknown" };

  const bioLines = h1 ? h1.lines : [];
  const { reignSummary, headerMeta, epithetJa } = parseBioLines(bioLines);
  const reigns = extractReigns(reignSummary);

  const refSection = sections.find((s) => s.title === "参考文献");
  const citations: Citation[] = refSection
    ? parseCitationList(refSection.lines)
    : [];
  const keyToId = new Map<string, string>(citations.map((c) => [c.key, c.id]));

  // Walk sections, tracking current layer
  const events: HistoricalEvent[] = [];
  let currentLayer: Layer | null = null;

  for (const sec of sections) {
    if (sec.level === 2) {
      currentLayer = LAYER_BY_SECTION[sec.title] ?? null;
      if (currentLayer) {
        const tables = parseMarkdownTables(sec.lines);
        tables.forEach((tbl, ti) => {
          const evs = rowsToEvents(tbl, {
            layer: currentLayer!,
            section: sec.title,
            keyToId,
            idPrefix: `${kingId}-${currentLayer}-${ti}`,
          });
          events.push(...evs);
        });
      }
    } else if (sec.level === 3 && currentLayer) {
      const tables = parseMarkdownTables(sec.lines);
      tables.forEach((tbl, ti) => {
        const evs = rowsToEvents(tbl, {
          layer: currentLayer!,
          section: sec.title,
          keyToId,
          idPrefix: `${kingId}-${currentLayer}-${slug(sec.title)}-${ti}`,
        });
        events.push(...evs);
      });
    }
  }

  const usedPlaceIds = new Set<string>();
  for (const ev of events) if (ev.placeId) usedPlaceIds.add(ev.placeId);

  const charSec = sections.find((s) => /^人物像/.test(s.title));
  const characterNotes = charSec
    ? {
        title: charSec.title,
        ...parseCharacterNotes(charSec.lines, keyToId),
      }
    : undefined;

  const transparencySec = sections.find((s) => s.title === "補注");
  const transparencyNote = transparencySec
    ? transparencySec.lines
        .map((l) => l.trim())
        .filter(Boolean)
        .join(" ")
    : undefined;

  const reignYears = reigns.flatMap((r) => [r.start, r.end]);
  const eventYears = events.flatMap((e) =>
    e.endYear !== undefined ? [e.startYear, e.endYear] : [e.startYear]
  );
  const pool = [...reignYears, ...eventYears].filter((y) => y !== 0);
  const birthYear = pool.length ? Math.min(...pool) - 3 : undefined;
  const deathYear = pool.length ? Math.max(...pool) + 1 : undefined;

  const places = GAZETTEER.filter((g) => usedPlaceIds.has(g.id)).map(
    ({ keywords: _k, ...p }) => p
  );

  return {
    id: kingId,
    nameJa: nameParts.nameJa,
    name: nameParts.name,
    epithet: nameParts.epithet,
    epithetJa,
    headerMeta,
    reignSummary,
    reigns,
    birthYear,
    deathYear,
    events,
    places,
    citations,
    transparencyNote,
    characterNotes,
  };
}

export { getPlace };
