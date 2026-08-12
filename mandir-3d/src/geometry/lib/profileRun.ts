/** profileRun — a molding profile extruded along a STRAIGHT run (stair
 * cheek caps, door surrounds, sill bands). The run lies along X, centered
 * at the origin, facing +z: profile dx becomes z (outward +), dy is
 * height above baseY.
 *
 * Convention: the profile traces the OUTER skin bottom → top with solid
 * behind (−z). Steps OUT while ascending face DOWN (overhang undersides),
 * steps IN face UP — this falls out of the winding, deterministically.
 *
 * The BACK (z=0 plane) is deliberately OPEN — runs sit against walls;
 * even with both caps this is not a closed solid. End caps close the
 * section with a straight return along z=0 and require dx=0 at both
 * profile ends. Self-intersecting sections are NOT detected (documented
 * limitation); duplicates and negative dx are rejected.
 */
import * as THREE from "three/webgpu";
import type { ProfileSample } from "./rectProfileRing";

export interface ProfileRunSpec {
  profile: ProfileSample[];
  length: number;
  baseY: number;
  capStart?: boolean;
  capEnd?: boolean;
}

export function profileRun(spec: ProfileRunSpec): THREE.BufferGeometry {
  const { profile, length, baseY } = spec;
  if (profile.length < 2) throw new Error("profileRun: profile needs ≥ 2 samples");
  if (!(length > 0)) throw new Error("profileRun: length must be positive");
  const n = profile.length;
  const hl = length / 2;
  for (let i = 0; i < n; i++) {
    const p = profile[i];
    if (!Number.isFinite(p.dx) || !Number.isFinite(p.dy)) throw new Error(`profileRun: non-finite sample ${i}`);
    if (p.dx < -1e-9) throw new Error(`profileRun: dx must be ≥ 0 (sample ${i}) — solid sits behind z=0`);
    if (i > 0 && Math.abs(p.dx - profile[i - 1].dx) < 1e-9 && Math.abs(p.dy - profile[i - 1].dy) < 1e-9) {
      throw new Error(`profileRun: duplicate consecutive samples at ${i}`);
    }
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

  // two columns of profile verts: x = −hl (start) and x = +hl (end)
  for (let i = 0; i < n; i++) {
    const y = baseY + profile[i].dy;
    const z = profile[i].dx;
    const v = arc[i] / totalArc;
    positions.push(-hl, y, z, hl, y, z);
    uvs.push(0, v, 1, v);
  }
  // facing +z, seen from outside: left = −x (start), right = +x (end)
  for (let i = 0; i < n - 1; i++) {
    const a = i * 2; // start, lower
    const b = i * 2 + 1; // end, lower
    const a2 = (i + 1) * 2;
    const b2 = (i + 1) * 2 + 1;
    index.push(a, b, b2, a, b2, a2);
  }

  const addCap = (x: number, outward: 1 | -1) => {
    if (Math.abs(profile[0].dx) > 1e-9 || Math.abs(profile[n - 1].dx) > 1e-9) {
      throw new Error("profileRun caps need dx=0 at both profile ends");
    }
    // section polygon in (z, y): profile polyline + straight z=0 return
    const pts = profile.map((p) => new THREE.Vector2(p.dx, p.dy));
    const tris = THREE.ShapeUtils.triangulateShape(pts, []);
    const base = positions.length / 3;
    for (const p of profile) {
      positions.push(x, baseY + p.dy, p.dx);
      uvs.push(p.dx, p.dy);
    }
    for (const [i0, i1, i2] of tris) {
      // wind by the COMPUTED 3D normal, never a hand-derived sign: the
      // cap must face `outward` along x
      const p = (i: number) => new THREE.Vector3(x, baseY + profile[i].dy, profile[i].dx);
      const nrm = new THREE.Vector3()
        .subVectors(p(i1), p(i0))
        .cross(new THREE.Vector3().subVectors(p(i2), p(i0)));
      if (nrm.x * outward >= 0) index.push(base + i0, base + i1, base + i2);
      else index.push(base + i0, base + i2, base + i1);
    }
  };
  if (spec.capStart) addCap(-hl, -1);
  if (spec.capEnd) addCap(hl, 1);

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(positions), 3));
  geo.setAttribute("uv", new THREE.BufferAttribute(new Float32Array(uvs), 2));
  geo.setIndex(index);
  geo.computeVertexNormals();
  return geo;
}
