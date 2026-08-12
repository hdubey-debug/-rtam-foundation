/** Canonical camera views — the single source of the shot geometry, shared
 * by the app and (by name) the shot harness. Azimuth 0 looks at the front
 * facade (+Z); positive azimuth orbits toward the east side.
 *
 * `hero` gets calibrated once against temple_v3.jpeg at M2, then FROZEN.
 */
export interface ViewDef {
  azimuthDeg: number;
  elevationDeg: number;
  /** margin multiplier on the fitted distance (1 = bounding sphere exactly) */
  fit: number;
  /** closeup: orbit a NAMED ANCHOR instead of fitting the whole model */
  anchor?: string;
  /** closeup camera distance in REAL METERS (converted per item scale) */
  distM?: number;
}

export const VIEWS: Record<string, ViewDef> = {
  front: { azimuthDeg: 0, elevationDeg: 8, fit: 1.12 },
  // CALIBRATED at M2 against temple_v3.jpeg (front face frame-left, long
  // flank receding right, low horizon) — FROZEN; do not retune.
  hero: { azimuthDeg: 35, elevationDeg: 6, fit: 1.06 },
  side: { azimuthDeg: 90, elevationDeg: 8, fit: 1.12 },
  rear: { azimuthDeg: 180, elevationDeg: 8, fit: 1.12 },
  top: { azimuthDeg: 30, elevationDeg: 55, fit: 1.12 },
  // canonical closeups on named anchors
  "close-podium-corner": { azimuthDeg: 38, elevationDeg: 12, fit: 1, anchor: "podium-corner", distM: 7 },
  "close-stair-door": { azimuthDeg: 8, elevationDeg: 9, fit: 1, anchor: "stair-base", distM: 11 },
  "close-tower-crown": { azimuthDeg: 30, elevationDeg: 18, fit: 1, anchor: "kalasha-tip", distM: 9 },
  "close-window": { azimuthDeg: 55, elevationDeg: 4, fit: 1, anchor: "window-ground", distM: 5 },
};

export const DEFAULT_VIEW = "hero";
