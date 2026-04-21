import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { parseKingMarkdown } from "../src/data/parseKing";

const here = dirname(fileURLToPath(import.meta.url));
const mdPath = resolve(here, "../src/data/kings/ptolemy-viii.md");
const md = readFileSync(mdPath, "utf8");

const king = parseKingMarkdown(md, "ptolemy-viii");

console.log("=== King ===");
console.log("nameJa:", king.nameJa);
console.log("name:", king.name);
console.log("epithet:", king.epithet);
console.log("birth/death:", king.birthYear, "/", king.deathYear);
console.log("reigns:");
for (const r of king.reigns) console.log(" ", r);

console.log("\n=== Events by layer ===");
const byLayer: Record<string, number> = {};
for (const e of king.events) byLayer[e.layer] = (byLayer[e.layer] || 0) + 1;
console.log(byLayer);
console.log("Total events:", king.events.length);
console.log(
  "Interpretations:",
  king.events.filter((e) => e.type === "interpretation").length
);
console.log(
  "Events with place:",
  king.events.filter((e) => e.placeId).length,
  "/ without:",
  king.events.filter((e) => !e.placeId).length
);

console.log("\n=== First 6 events ===");
for (const e of king.events.slice(0, 6)) {
  console.log(
    `  [${e.layer}/${e.type}] ${e.yearLabel} (${e.startYear}${
      e.endYear !== undefined ? `..${e.endYear}` : ""
    }) place=${e.placeId || "-"} refs=${e.citationRefs.length}`
  );
  console.log("    →", e.description.slice(0, 70));
}

console.log("\n=== Places ===");
for (const p of king.places) console.log(" ", p.id, p.nameJa);

console.log("\n=== Citations ===");
for (const c of king.citations) console.log(" ", c.key, "→", c.title);

console.log("\n=== Character notes ===");
if (king.characterNotes) {
  console.log(" title:", king.characterNotes.title);
  for (const i of king.characterNotes.items)
    console.log(
      "  -",
      i.label,
      ":",
      i.text.slice(0, 60),
      "refs=",
      i.citationRefs.length
    );
}

console.log("\n=== Transparency ===");
console.log(king.transparencyNote?.slice(0, 120));

console.log("\n=== Events missing place (hidden on map, shown in timeline/detail) ===");
for (const e of king.events.filter((e) => !e.placeId)) {
  console.log("  ·", e.yearLabel, "—", e.description.slice(0, 70));
}
