/** Deterministic shot mode, parsed once from the URL.
 *
 * ?shot=1&item=fixture&view=front  → frozen, render-on-demand, dpr 1,
 * instant camera, done-protocol published on window.__mandirShot.
 * ?perf=1 → live perf overlay (founder's real-browser oracle).
 */
export interface ShotMode {
  shot: boolean;
  /** stage-item id; null → the registry default */
  item: string | null;
  view: string | null;
  perf: boolean;
  /** ?layers=wire,xray */
  wireframe: boolean;
  xray: boolean;
}

function parse(): ShotMode {
  const q = new URLSearchParams(window.location.search);
  const layers = (q.get("layers") ?? "").split(",");
  return {
    shot: q.get("shot") === "1",
    item: q.get("item"),
    view: q.get("view"),
    perf: q.get("perf") === "1",
    wireframe: layers.includes("wire"),
    xray: layers.includes("xray"),
  };
}

export const shotMode: ShotMode = parse();
