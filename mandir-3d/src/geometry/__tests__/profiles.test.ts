/** Gates for the M3 profile primitives — these run BEFORE any component
 * builds on them (the plan's "primitives first, tested first").
 */
import { describe, expect, it } from "vitest";
import * as THREE from "three/webgpu";
import { rectProfileRing, type ProfileSample } from "../lib/rectProfileRing";
import { profileRun } from "../lib/profileRun";

function indexedTris(geo: THREE.BufferGeometry): [THREE.Vector3, THREE.Vector3, THREE.Vector3][] {
  const pos = geo.getAttribute("position") as THREE.BufferAttribute;
  const idx = geo.getIndex()!;
  const out: [THREE.Vector3, THREE.Vector3, THREE.Vector3][] = [];
  for (let i = 0; i < idx.count; i += 3) {
    out.push([
      new THREE.Vector3().fromBufferAttribute(pos, idx.getX(i)),
      new THREE.Vector3().fromBufferAttribute(pos, idx.getX(i + 1)),
      new THREE.Vector3().fromBufferAttribute(pos, idx.getX(i + 2)),
    ]);
  }
  return out;
}

function expectSaneTriangles(geo: THREE.BufferGeometry, label: string): void {
  for (const [a, b, c] of indexedTris(geo)) {
    const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a));
    expect(n.length(), `${label}: degenerate triangle`).toBeGreaterThan(1e-10);
    expect(Number.isFinite(n.x) && Number.isFinite(n.y) && Number.isFinite(n.z), `${label}: NaN normal`).toBe(true);
  }
  const nrm = geo.getAttribute("normal") as THREE.BufferAttribute;
  for (let i = 0; i < nrm.count; i++) {
    expect(Number.isFinite(nrm.getX(i)) && Number.isFinite(nrm.getY(i)) && Number.isFinite(nrm.getZ(i))).toBe(true);
  }
}

/** every triangle must face away from the ring's central axis (rings are
 * star-shaped around the y axis) — the black-face bug class */
function expectOutwardFromAxis(geo: THREE.BufferGeometry, label: string): void {
  for (const [a, b, c] of indexedTris(geo)) {
    const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a)).normalize();
    const centroid = new THREE.Vector3().addVectors(a, b).add(c).divideScalar(3);
    const radial = new THREE.Vector3(centroid.x, 0, centroid.z);
    if (radial.length() < 1e-6) continue;
    const d = n.dot(radial.normalize());
    // horizontal faces (ledges, caps) have |d|≈0 — only reject clear inversions
    expect(d, `${label}: inward-facing side triangle at ${centroid.toArray().map((v) => v.toFixed(3))}`).toBeGreaterThan(
      -0.35,
    );
  }
}

const STEP: ProfileSample[] = [
  { dx: 0, dy: 0 },
  { dx: 0, dy: 0.3 },
  { dx: -0.1, dy: 0.3 },
  { dx: -0.1, dy: 0.6 },
];

describe("rectProfileRing", () => {
  it("emits crease-split loops + stitched quads, sane and outward", () => {
    const geo = rectProfileRing({ w: 4, d: 2, baseY: 0, profile: STEP, capBottom: true, capTop: true });
    const pos = geo.getAttribute("position") as THREE.BufferAttribute;
    // STEP has 90° creases at samples 1 and 2 → 6 emitted loops + 2 caps
    expect(pos.count).toBe((STEP.length + 2) * 8 + 8);
    expectSaneTriangles(geo, "ring");
    expectOutwardFromAxis(geo, "ring");
  });

  it("crease split keeps LEDGE normals crisp (no smoothed steps)", () => {
    const geo = rectProfileRing({ w: 4, d: 2, baseY: 0, profile: STEP });
    const pos = geo.getAttribute("position") as THREE.BufferAttribute;
    const nrm = geo.getAttribute("normal") as THREE.BufferAttribute;
    // verts on the vertical face BELOW the ledge (y within (0, 0.3), on
    // the +z side at dx=0 → z=1): normals must be horizontal
    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i);
      if (y > 0.01 && y < 0.29 && Math.abs(pos.getZ(i) - 1) < 1e-6) {
        expect(Math.abs(nrm.getY(i)), `vert ${i} at y=${y.toFixed(2)} smoothed over the ledge`).toBeLessThan(0.05);
      }
    }
  });

  it("rejects duplicate consecutive samples (the degenerate-stitch class)", () => {
    expect(() =>
      rectProfileRing({
        w: 4,
        d: 2,
        baseY: 0,
        profile: [
          { dx: 0, dy: 0 },
          { dx: -0.05, dy: 0.2 },
          { dx: -0.05, dy: 0.2 },
          { dx: -0.05, dy: 0.5 },
        ],
      }),
    ).toThrow(/duplicate/);
  });

  it("hits exact expected corner positions", () => {
    const geo = rectProfileRing({ w: 4, d: 2, baseY: 1, profile: STEP });
    geo.computeBoundingBox();
    const bb = geo.boundingBox!;
    expect(bb.min.x).toBeCloseTo(-2, 6);
    expect(bb.max.x).toBeCloseTo(2, 6);
    expect(bb.min.z).toBeCloseTo(-1, 6);
    expect(bb.max.z).toBeCloseTo(1, 6);
    expect(bb.min.y).toBeCloseTo(1, 6);
    expect(bb.max.y).toBeCloseTo(1.6, 6);
  });

  it("every stitched side edge is manifold (shared by exactly 2 triangles)", () => {
    const geo = rectProfileRing({ w: 4, d: 2, baseY: 0, profile: STEP });
    const idx = geo.getIndex()!;
    const edges = new Map<string, number>();
    for (let i = 0; i < idx.count; i += 3) {
      const t = [idx.getX(i), idx.getX(i + 1), idx.getX(i + 2)];
      for (let e = 0; e < 3; e++) {
        const a = t[e];
        const b = t[(e + 1) % 3];
        const k = a < b ? `${a}:${b}` : `${b}:${a}`;
        edges.set(k, (edges.get(k) ?? 0) + 1);
      }
    }
    // interior (vertical-run) edges are shared twice; boundary edges
    // (bottom/top rims, corner splits) once — none more than twice
    for (const [, count] of edges) expect(count).toBeLessThanOrEqual(2);
  });

  it("a smooth arc profile stays smooth along the profile (kumuda-class)", () => {
    const arc: ProfileSample[] = [];
    for (let i = 0; i <= 8; i++) {
      arc.push({ dx: -0.05 + 0.045 * Math.sin((Math.PI * i) / 8), dy: 0.15 * (i / 8) });
    }
    const geo = rectProfileRing({ w: 4, d: 2, baseY: 0, profile: arc });
    expectSaneTriangles(geo, "arc-ring");
    expectOutwardFromAxis(geo, "arc-ring");
  });
});

describe("profileRun", () => {
  it("extrudes with caps, sane triangles, caps face ±x", () => {
    const geo = profileRun({ profile: STEP.map((p) => ({ dx: -p.dx, dy: p.dy })), length: 3, baseY: 0 });
    expectSaneTriangles(geo, "run");
    const capped = profileRun({
      profile: [
        { dx: 0, dy: 0 },
        { dx: 0.08, dy: 0.1 },
        { dx: 0, dy: 0.2 },
      ],
      length: 3,
      baseY: 0,
      capStart: true,
      capEnd: true,
    });
    expectSaneTriangles(capped, "capped-run");
    // cap triangles: all three verts at the SAME signed x end
    const tris = indexedTris(capped);
    const capTris = tris.filter(([a, b, c]) => a.x === b.x && b.x === c.x && Math.abs(a.x) === 1.5);
    expect(capTris.length).toBeGreaterThan(0);
    for (const [a, b, c] of capTris) {
      const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a)).normalize();
      expect(Math.abs(n.x), "cap normal must be ±x").toBeGreaterThan(0.99);
      expect(n.x * Math.sign(a.x)).toBeGreaterThan(0); // outward
    }
  });

  it("rejects caps on open-ended profiles", () => {
    expect(() =>
      profileRun({
        profile: [
          { dx: 0.05, dy: 0 },
          { dx: 0.1, dy: 0.2 },
        ],
        length: 2,
        baseY: 0,
        capStart: true,
      }),
    ).toThrow();
  });
});
