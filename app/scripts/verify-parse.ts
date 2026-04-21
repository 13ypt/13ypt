import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { parseKingMarkdown } from "../src/data/parseKing";
import { parseTimelineMarkdown } from "../src/data/parseTimeline";

const here = dirname(fileURLToPath(import.meta.url));

function readMd(rel: string) {
  return readFileSync(resolve(here, "..", rel), "utf8");
}

// ---- King: Ptolemy VIII -------------------------------------------------
console.log("========== King: Ptolemy VIII ==========");
const king = parseKingMarkdown(
  readMd("src/data/kings/ptolemy-viii.md"),
  "ptolemy-viii"
);
console.log("name:", king.nameJa);
console.log("birth/death:", king.birthYear, "/", king.deathYear);
const kbyLayer: Record<string, number> = {};
for (const e of king.events) kbyLayer[e.layer] = (kbyLayer[e.layer] || 0) + 1;
console.log("events by layer:", kbyLayer);
console.log("total events:", king.events.length);
console.log("places:", king.places.map((p) => p.nameJa).join(", "));

// ---- Timeline: Late Ptolemies ------------------------------------------
console.log("\n========== Timeline: Late Ptolemies ==========");
const tl = parseTimelineMarkdown(
  readMd("src/data/timelines/late-ptolemies.md"),
  "late-ptolemies"
);
console.log("title:", tl.titleJa);
console.log("dateRange:", tl.dateRange);
console.log("total events:", tl.events.length);
const byLayer: Record<string, number> = {};
for (const e of tl.events) byLayer[e.layer] = (byLayer[e.layer] || 0) + 1;
console.log("events by layer:", byLayer);
console.log(
  "interpretations:",
  tl.events.filter((e) => e.type === "interpretation").length
);
console.log(
  "events with place:",
  tl.events.filter((e) => e.placeId).length,
  "/ without:",
  tl.events.filter((e) => !e.placeId).length
);
console.log("places:", tl.places.map((p) => p.nameJa).join(", "));
console.log("\nactors in use:");
for (const a of tl.actors) console.log("  -", a.id, ":", a.nameJa);

console.log("\nSample events (first 8):");
for (const e of tl.events.slice(0, 8)) {
  const actors = e.actors?.join(",") ?? "-";
  console.log(
    `  [${e.layer}/${e.type}] ${e.yearLabel} (${e.startYear}${
      e.endYear !== undefined ? `..${e.endYear}` : ""
    }) place=${e.placeId || "-"} actors=${actors}`
  );
  console.log("    →", e.description.slice(0, 70));
}

console.log("\nEvents by section:");
const bySection: Record<string, number> = {};
for (const e of tl.events)
  bySection[e.section] = (bySection[e.section] || 0) + 1;
for (const [k, v] of Object.entries(bySection))
  console.log(`  ${v} events: ${k}`);

console.log("\nCitations in timeline:");
for (const c of tl.citations)
  console.log(`  - ${c.key} → ${c.title.slice(0, 60)}`);

console.log("\nEvents with citations:");
const withCites = tl.events.filter((e) => e.citationRefs.length > 0);
console.log(`  ${withCites.length} / ${tl.events.length} events have citations`);
for (const e of withCites.slice(0, 12)) {
  const refs = e.citationRefs
    .map(
      (r) =>
        r.citationId
          ? tl.citations.find((c) => c.id === r.citationId)?.key +
            (r.pages ? `: ${r.pages}` : "")
          : `[${r.rawLabel}]`
    )
    .join(" · ");
  console.log(`  · ${e.yearLabel}: ${refs}`);
}

console.log("\nAnimal-cult events:");
for (const e of tl.events.filter((e) => e.layer === "animal-cult")) {
  console.log(`  · ${e.yearLabel} — ${e.description.slice(0, 70)}`);
}
