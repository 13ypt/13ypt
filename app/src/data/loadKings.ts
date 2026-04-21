import type { King } from "./types";
import { parseKingMarkdown } from "./parseKing";
import ptolemyVIIIMd from "./kings/ptolemy-viii.md?raw";

export const kings: King[] = [parseKingMarkdown(ptolemyVIIIMd, "ptolemy-viii")];
