/** Massing-grade hip roof: a rectangular eave ring lofted to a ridge LINE
 * (two ridge points on the long axis). Good enough for M2 volumes; the
 * real hipRoof.ts (explicit eave/ridge polygons, facet-local UVs, curb
 * penetration) replaces it at M7.
 *
 * Winding is FORCED outward: every triangle's normal is checked against
 * an outward hint and flipped if it disagrees — no hand-derived orders.
 */
import * as THREE from "three/webgpu";

export interface HipPrismSpec {
  /** eave rectangle width (x) and depth (z), centered at origin */
  w: number;
  d: number;
  eaveY: number;
  ridgeY: number;
  /** ridge runs along the LONGER axis; inset from each end */
  ridgeInset: number;
}

type V3 = [number, number, number];

/** push triangle a-b-c, flipped if its normal disagrees with `outward` */
export function pushTriOutward(out: number[], a: V3, b: V3, c: V3, outward: V3): void {
  const ux = b[0] - a[0];
  const uy = b[1] - a[1];
  const uz = b[2] - a[2];
  const vx = c[0] - a[0];
  const vy = c[1] - a[1];
  const vz = c[2] - a[2];
  const nx = uy * vz - uz * vy;
  const ny = uz * vx - ux * vz;
  const nz = ux * vy - uy * vx;
  const dot = nx * outward[0] + ny * outward[1] + nz * outward[2];
  if (dot >= 0) out.push(...a, ...b, ...c);
  else out.push(...a, ...c, ...b);
}

export function hipPrismGeometry(spec: HipPrismSpec): THREE.BufferGeometry {
  const { w, d, eaveY, ridgeY, ridgeInset } = spec;
  if (!(w > 0) || !(d > 0)) throw new Error("hipPrism: w and d must be positive");
  if (!(ridgeY > eaveY)) throw new Error("hipPrism: ridge must sit above the eave");
  if (!(ridgeInset >= 0) || 2 * ridgeInset >= Math.max(w, d)) {
    throw new Error("hipPrism: ridgeInset collapses or reverses the ridge");
  }
  const hw = w / 2;
  const hd = d / 2;
  const alongX = w >= d;

  const e0: V3 = [-hw, eaveY, -hd];
  const e1: V3 = [hw, eaveY, -hd];
  const e2: V3 = [hw, eaveY, hd];
  const e3: V3 = [-hw, eaveY, hd];
  const r0: V3 = alongX ? [-hw + ridgeInset, ridgeY, 0] : [0, ridgeY, -hd + ridgeInset];
  const r1: V3 = alongX ? [hw - ridgeInset, ridgeY, 0] : [0, ridgeY, hd - ridgeInset];

  const out: number[] = [];
  if (alongX) {
    // slopes face ±z; hips face ±x
    pushTriOutward(out, e0, e1, r1, [0, 0.4, -1]);
    pushTriOutward(out, e0, r1, r0, [0, 0.4, -1]);
    pushTriOutward(out, e2, e3, r0, [0, 0.4, 1]);
    pushTriOutward(out, e2, r0, r1, [0, 0.4, 1]);
    pushTriOutward(out, e3, e0, r0, [-1, 0.4, 0]);
    pushTriOutward(out, e1, e2, r1, [1, 0.4, 0]);
  } else {
    // slopes face ±x; hips face ±z
    pushTriOutward(out, e1, e2, r1, [1, 0.4, 0]);
    pushTriOutward(out, e1, r1, r0, [1, 0.4, 0]);
    pushTriOutward(out, e3, e0, r0, [-1, 0.4, 0]);
    pushTriOutward(out, e3, r0, r1, [-1, 0.4, 0]);
    pushTriOutward(out, e0, e1, r0, [0, 0.4, -1]);
    pushTriOutward(out, e2, e3, r1, [0, 0.4, 1]);
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(out), 3));
  geo.computeVertexNormals();
  return geo;
}
