/** rectProfileRing — a molding profile wrapped as a CLOSED RECTANGULAR
 * ring (podium courses, cornices, string moldings).
 *
 * Approach (the plan's): emit ONE rectangular loop per profile sample —
 * the loop is the base rectangle offset by that sample's dx on ALL four
 * faces — then stitch consecutive loops. Corner miters EMERGE from the
 * loop correspondence; there is no miter-plane math to get wrong.
 *
 * Topology: 8 vertices per loop (each corner duplicated once per side) so
 * normals stay CRISP at the four plan corners; and loops DUPLICATE at
 * profile CREASES (section angle > CREASE_DEG) so ledges and steps stay
 * crisp while arcs (kumuda) stay smooth — codex GEO M3 finding.
 *
 * Validation: rejects non-finite samples, consecutive duplicates
 * (degenerate stitching), and offsets that collapse the rectangle.
 */
import * as THREE from "three/webgpu";

export interface ProfileSample {
  /** offset from the base rectangle face; negative = inward */
  dx: number;
  /** height above the ring base */
  dy: number;
}

export interface RectProfileRingSpec {
  /** base rectangle (the dx = 0 plane), centered on the origin */
  w: number;
  d: number;
  baseY: number;
  /** bottom → top, at least 2 samples */
  profile: ProfileSample[];
  capBottom?: boolean;
  capTop?: boolean;
}

const CREASE_DEG = 30;

function validate(spec: RectProfileRingSpec): void {
  const { w, d, profile } = spec;
  if (!(w > 0) || !(d > 0)) throw new Error("rectProfileRing: w and d must be positive");
  if (profile.length < 2) throw new Error("rectProfileRing: profile needs ≥ 2 samples");
  for (let i = 0; i < profile.length; i++) {
    const p = profile[i];
    if (!Number.isFinite(p.dx) || !Number.isFinite(p.dy)) {
      throw new Error(`rectProfileRing: non-finite sample at ${i}`);
    }
    if (w / 2 + p.dx <= 0 || d / 2 + p.dx <= 0) {
      throw new Error(`rectProfileRing: sample ${i} collapses the rectangle (dx ${p.dx})`);
    }
    if (i > 0) {
      const q = profile[i - 1];
      if (Math.abs(p.dx - q.dx) < 1e-9 && Math.abs(p.dy - q.dy) < 1e-9) {
        throw new Error(`rectProfileRing: duplicate consecutive samples at ${i} — degenerate stitch`);
      }
    }
  }
}

export function rectProfileRing(spec: RectProfileRingSpec): THREE.BufferGeometry {
  validate(spec);
  const { w, d, baseY, profile } = spec;
  const n = profile.length;

  // crease detection: split the loop where the section direction turns
  const creased: boolean[] = new Array(n).fill(false);
  for (let i = 1; i < n - 1; i++) {
    const a = profile[i - 1];
    const b = profile[i];
    const c = profile[i + 1];
    const v1 = new THREE.Vector2(b.dx - a.dx, b.dy - a.dy).normalize();
    const v2 = new THREE.Vector2(c.dx - b.dx, c.dy - b.dy).normalize();
    const deg = (Math.acos(THREE.MathUtils.clamp(v1.dot(v2), -1, 1)) * 180) / Math.PI;
    creased[i] = deg > CREASE_DEG;
  }
  // emitted loops: sample index per loop; creased samples emit twice
  const firstLoop: number[] = new Array(n);
  const lastLoop: number[] = new Array(n);
  const loopSample: number[] = [];
  for (let i = 0; i < n; i++) {
    firstLoop[i] = loopSample.length;
    loopSample.push(i);
    if (creased[i]) loopSample.push(i);
    lastLoop[i] = loopSample.length - 1;
  }

  const positions: number[] = [];
  const uvs: number[] = [];
  const index: number[] = [];

  const arc: number[] = [0];
  for (let i = 1; i < n; i++) {
    const a = profile[i - 1];
    const b = profile[i];
    arc.push(arc[i - 1] + Math.hypot(b.dx - a.dx, b.dy - a.dy));
  }
  const totalArc = arc[n - 1] || 1;

  const corners = (e: number): [number, number][] => {
    const hw = w / 2 + e;
    const hd = d / 2 + e;
    return [
      [-hw, -hd],
      [hw, -hd],
      [hw, hd],
      [-hw, hd],
    ];
  };
  // each side lists its corners "left → right seen from outside"
  const SIDES: [number, number][] = [
    [3, 2], // +z
    [2, 1], // +x
    [1, 0], // −z
    [0, 3], // −x
  ];

  for (const si of loopSample) {
    const c = corners(profile[si].dx);
    const y = baseY + profile[si].dy;
    const v = arc[si] / totalArc;
    for (let s = 0; s < 4; s++) {
      const [ia, ib] = SIDES[s];
      positions.push(c[ia][0], y, c[ia][1], c[ib][0], y, c[ib][1]);
      uvs.push(0, v, 1, v);
    }
  }

  const vertAt = (loop: number, side: number, which: 0 | 1) => loop * 8 + side * 2 + which;
  for (let i = 0; i < n - 1; i++) {
    const lo = lastLoop[i];
    const hi = firstLoop[i + 1];
    for (let s = 0; s < 4; s++) {
      const a = vertAt(lo, s, 0);
      const b = vertAt(lo, s, 1);
      const a2 = vertAt(hi, s, 0);
      const b2 = vertAt(hi, s, 1);
      index.push(a, b, b2, a, b2, a2);
    }
  }

  // caps get their OWN vertices so cap normals stay flat ±y
  const addCap = (sample: number, up: boolean) => {
    const c = corners(profile[sample].dx);
    const y = baseY + profile[sample].dy;
    const base = positions.length / 3;
    for (const [cx, cz] of c) {
      positions.push(cx, y, cz);
      uvs.push(cx / w + 0.5, cz / d + 0.5);
    }
    if (up) index.push(base, base + 2, base + 1, base, base + 3, base + 2);
    else index.push(base, base + 1, base + 2, base, base + 2, base + 3);
  };
  if (spec.capBottom) addCap(0, false);
  if (spec.capTop) addCap(n - 1, true);

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(positions), 3));
  geo.setAttribute("uv", new THREE.BufferAttribute(new Float32Array(uvs), 2));
  geo.setIndex(index);
  geo.computeVertexNormals();
  return geo;
}
