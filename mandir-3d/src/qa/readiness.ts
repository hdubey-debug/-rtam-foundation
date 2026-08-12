/** Generation-scoped render-done protocol (not a global boolean).
 *
 * The harness polls window.__mandirShot until `done` is true AND `key`
 * matches the {item, view} generation it asked for — so a stale "done"
 * from a previous generation can never satisfy a new request. The payload
 * carries enough scene statistics for shots/measures.json.
 */

import type { Measures } from "./measures";

export interface ShotPayload {
  key: string; // `${item}::${view}`
  item: string;
  view: string;
  renderer: string;
  /** named-group real-meter measurements vs named envelopes */
  measures?: Measures;
  /** normalized stage-space bounds of the current model */
  stageBounds: { min: number[]; max: number[] };
  /** real-meter bounds of the current model */
  realBounds: { min: number[]; max: number[] };
  meshes: number;
  instancedMeshes: number;
  instances: number;
  drawCalls: number;
  triangles: number;
  shadowGen: number;
  frame: number;
}

interface ShotState {
  done: boolean;
  key: string;
  payload?: ShotPayload;
}

declare global {
  interface Window {
    __mandirShot?: ShotState;
    /** shot mode only: export the current model (real meters) as base64 GLB */
    __mandirExportGlb?: () => Promise<string>;
    /** shot mode only: export → reimport → swap onto the stage; returns
     * JSON {bytes, realBounds} for the harness to compare */
    __mandirRoundtrip?: () => Promise<string>;
  }
}

export function shotKey(item: string, view: string): string {
  return `${item}::${view}`;
}

export function publishShotPending(key: string): void {
  window.__mandirShot = { done: false, key };
}

export function publishShotDone(payload: ShotPayload): void {
  window.__mandirShot = { done: true, key: payload.key, payload };
}
