/** The stage-item registry: item id → builder + display metadata.
 * Every entry that references an EXTERNAL model (Track A) must carry
 * license provenance; the production build refuses non-commercial models
 * (gate lands with the Track A loader at M11).
 */
import type { StageModel } from "../engine/createEngine";
import { buildFixture } from "../geometry/fixture";
import { buildTempleMassing } from "../geometry/buildTemple";

export interface StageItem {
  id: string;
  label: string;
  build: () => StageModel;
  /** provenance for external models; parametric items are "generated" */
  license: "generated" | { source: string; terms: string };
}

export const stageItems: Record<string, StageItem> = {
  "massing-a": {
    id: "massing-a",
    label: "Massing — tower A (straight taper)",
    build: () => buildTempleMassing({ towerSilhouette: "A" }),
    license: "generated",
  },
  "massing-b": {
    id: "massing-b",
    label: "Massing — tower B (nagara curve)",
    build: () => buildTempleMassing({ towerSilhouette: "B" }),
    license: "generated",
  },
  fixture: {
    id: "fixture",
    label: "M0 spike fixture",
    build: buildFixture,
    license: "generated",
  },
};

export const DEFAULT_ITEM = "massing-a";

export function resolveItem(id: string): StageItem {
  return stageItems[id] ?? stageItems[DEFAULT_ITEM];
}
