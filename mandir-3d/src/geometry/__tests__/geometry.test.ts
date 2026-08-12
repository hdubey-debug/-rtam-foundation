/** Geometry gates, seeded at M1/M2: datum assertions hold, custom
 * geometry winds OUTWARD (the massing's black-face bug class), and the
 * founder datums are physically present in the built model.
 */
import { describe, expect, it } from "vitest";
import * as THREE from "three/webgpu";
import { hipPrismGeometry } from "../lib/hipPrism";
import { buildTempleMassing } from "../buildTemple";
import { assertDims, envelopes, stations, FT } from "../dimensions";
import { assertOpenings } from "../openings";

interface Tri {
  a: THREE.Vector3;
  b: THREE.Vector3;
  c: THREE.Vector3;
  normal: THREE.Vector3;
  centroid: THREE.Vector3;
  area: number;
}

function triangles(geo: THREE.BufferGeometry): Tri[] {
  const pos = geo.getAttribute("position") as THREE.BufferAttribute;
  expect(geo.getIndex()).toBeNull(); // massing lofts are non-indexed
  const tris: Tri[] = [];
  for (let i = 0; i < pos.count; i += 3) {
    const a = new THREE.Vector3().fromBufferAttribute(pos, i);
    const b = new THREE.Vector3().fromBufferAttribute(pos, i + 1);
    const c = new THREE.Vector3().fromBufferAttribute(pos, i + 2);
    const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a));
    tris.push({
      a,
      b,
      c,
      normal: n.clone().normalize(),
      centroid: new THREE.Vector3().addVectors(a, b).add(c).divideScalar(3),
      area: n.length() / 2,
    });
  }
  return tris;
}

/** convex-ish solids: every face must look AWAY from the centroid */
function expectOutward(geo: THREE.BufferGeometry, label: string): void {
  const tris = triangles(geo);
  const center = new THREE.Vector3();
  tris.forEach((t) => center.add(t.centroid));
  center.divideScalar(tris.length);
  for (const t of tris) {
    expect(t.area, `${label}: degenerate triangle`).toBeGreaterThan(1e-9);
    expect(Number.isFinite(t.normal.x), `${label}: non-finite normal`).toBe(true);
    const dot = t.normal.dot(new THREE.Vector3().subVectors(t.centroid, center));
    expect(dot, `${label}: inward-facing triangle at ${t.centroid.toArray().map((v) => v.toFixed(2))}`).toBeGreaterThan(0);
  }
}

describe("datum gate", () => {
  it("assertDims holds", () => {
    expect(assertDims()).toEqual([]);
  });
  it("law 3 opening gate holds", () => {
    expect(assertOpenings()).toEqual([]);
  });
});

describe("hipPrism", () => {
  it("winds outward with the ridge along x", () => {
    expectOutward(hipPrismGeometry({ w: 10, d: 4, eaveY: 0, ridgeY: 2, ridgeInset: 3 }), "alongX");
  });
  it("winds outward with the ridge along z", () => {
    expectOutward(hipPrismGeometry({ w: 4, d: 10, eaveY: 0, ridgeY: 2, ridgeInset: 3 }), "alongZ");
  });
});

describe("temple massing", () => {
  for (const silhouette of ["A", "B"] as const) {
    it(`tower ${silhouette}: loft winds outward, datums physically present`, () => {
      const { group, anchors } = buildTempleMassing({ towerSilhouette: silhouette });

      const shaft = group.getObjectByName("tower-shaft") as THREE.Mesh;
      expect(shaft).toBeTruthy();
      expectOutward(shaft.geometry, `tower-${silhouette}`);

      // the founder's 52 ft binds at the kalasha tip anchor
      expect(anchors?.["kalasha-tip"]?.y).toBeCloseTo(52 * FT, 9);

      // the podium GROUP spans exactly the 52×88 envelope (Float32 → 0.05 mm)
      const podium = group.getObjectByName("podium")!;
      const bb = new THREE.Box3().setFromObject(podium);
      expect(bb.max.x - bb.min.x).toBeCloseTo(envelopes.podiumW.v, 4);
      expect(bb.max.z - bb.min.z).toBeCloseTo(envelopes.podiumD.v, 4);
      expect(bb.max.y).toBeCloseTo(0.9, 4); // terrace datum

      // plate datum: the wall group tops out at 30 ft
      group.updateMatrixWorld(true);
      const body = group.getObjectByName("body")!;
      const bodyBox = new THREE.Box3().setFromObject(body);
      expect(bodyBox.max.y).toBeCloseTo(stations.plateY.v, 4);
      expect(bodyBox.max.x - bodyBox.min.x).toBeCloseTo(envelopes.structuralW.v, 4);
    });
  }
});
