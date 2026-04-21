import type { ViewDescriptor } from "./types";
import { parseKingMarkdown } from "./parseKing";
import { parseTimelineMarkdown } from "./parseTimeline";
import ptolemyVIIIMd from "./kings/ptolemy-viii.md?raw";
import latePtolemiesMd from "./timelines/late-ptolemies.md?raw";

export const views: ViewDescriptor[] = [
  {
    kind: "king",
    id: "king:ptolemy-viii",
    labelJa: "王別：プトレマイオス8世",
    king: parseKingMarkdown(ptolemyVIIIMd, "ptolemy-viii"),
  },
  {
    kind: "timeline",
    id: "timeline:late-ptolemies",
    labelJa: "年表：プトレマイオス朝後期 (前180〜前86)",
    timeline: parseTimelineMarkdown(latePtolemiesMd, "late-ptolemies"),
  },
];
