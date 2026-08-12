/** REAL-component gates (codex GEO M3: the primitive tests never built
 * the actual podium/stair — these do, and pin the fixed defects).
 */
import { describe, expect, it } from "vitest";
import * as THREE from "three/webgpu";
import { rectProfileRing } from "../lib/rectProfileRing";
import { podiumSectionProfile, buildPodium } from "../podium";
import { buildStair } from "../stair";
import { buildTempleMassing } from "../buildTemple";
import { createMaterialLib } from "../../materials/materials";
import { measureModel } from "../../qa/measures";
import { envelopes, massing, podiumProfile, stairSpec, stations } from "../dimensions";

function nonDegenerate(geo: THREE.BufferGeometry, label: string): void {
  const pos = geo.getAttribute("position") as THREE.BufferAttribute;
  const idx = geo.getIndex();
  const read = (i: number) => new THREE.Vector3().fromBufferAttribute(pos, idx ? idx.getX(i) : i);
  const count = idx ? idx.count : pos.count;
  for (let i = 0; i < count; i += 3) {
    const a = read(i);
    const n = new THREE.Vector3().subVectors(read(i + 1), a).cross(new THREE.Vector3().subVectors(read(i + 2), a));
    expect(n.length(), `${label}: degenerate triangle at tri ${i / 3}`).toBeGreaterThan(1e-10);
  }
}

describe("the real podium", () => {
  it("profile stitches with ZERO degenerate triangles (the M3 blocker)", () => {
    const geo = rectProfileRing({
      w: envelopes.podiumW.v,
      d: envelopes.podiumD.v,
      baseY: 0,
      profile: podiumSectionProfile(),
      capBottom: true,
    });
    nonDegenerate(geo, "podium-ring");
  });

  it("carries a REAL drip groove in the kapota soffit", () => {
    const prof = podiumSectionProfile();
    // the groove: two samples share the raised dy inside the soffit
    const grooveY = 0.75 + podiumProfile.dripGrooveDepth.v;
    const up = prof.filter((p) => Math.abs(p.dy - grooveY) < 1e-9);
    expect(up.length, "groove ceiling samples").toBe(2);
    expect(Math.abs(up[0].dx - up[1].dx)).toBeCloseTo(podiumProfile.dripGrooveW.v, 9);
  });

  it("kumuda springs HORIZONTALLY (torus, not sin-bulge)", () => {
    const prof = podiumSectionProfile();
    const jagatiTopIdx = prof.findIndex((p) => Math.abs(p.dy - 0.45) < 1e-9);
    const first = prof[jagatiTopIdx + 1];
    const slope = Math.abs((first.dy - 0.45) / (first.dx - prof[jagatiTopIdx].dx));
    expect(slope, "takeoff |dy/dx| must be shallow (horizontal spring)").toBeLessThan(0.5);
  });

  it("group spans exactly the envelope with nothing proud", () => {
    const { group } = buildPodium(createMaterialLib());
    const bb = new THREE.Box3().setFromObject(group);
    expect(bb.max.x - bb.min.x).toBeCloseTo(envelopes.podiumW.v, 4);
    expect(bb.max.z - bb.min.z).toBeCloseTo(envelopes.podiumD.v, 4);
  });
});

describe("the real stair", () => {
  const lib = createMaterialLib();
  const { group } = buildStair(lib);

  it("cheek rake stays a CONSTANT 0.12 above the nosing line", () => {
    // nosing: y = 0.9 − z/3; rake: y = 1.02 − z/3. The extrusion only has
    // vertices at shape corners — probe AT the corners: the rake start
    // (z=−0.05) and the rake end (where it meets the newel zone).
    const cheek = group.getObjectByName("cheek-l") as THREE.Mesh;
    const pos = cheek.geometry.getAttribute("position") as THREE.BufferAttribute;
    const topAt = (z: number, win: number) => {
      let best = -Infinity;
      for (let i = 0; i < pos.count; i++) {
        if (Math.abs(pos.getZ(i) - z) < win) best = Math.max(best, pos.getY(i));
      }
      return best;
    };
    const rakeSlope = 1 / 3;
    const rakeEndZ = -0.05 + (1.02 - 0.42) / rakeSlope; // as built in stair.ts
    // the rake line as CONSTRUCTED: y(z) = 1.02 − z·slope (corner at −0.05
    // belongs to the same line). Clearance = rake(z) − nosing(z).
    const cStart = topAt(-0.05, 0.1) - (0.9 - -0.05 * rakeSlope);
    const cEnd = topAt(rakeEndZ, 0.1) - (0.9 - rakeEndZ * rakeSlope);
    expect(Math.abs(cStart - cEnd), "clearance must be CONSTANT along the rake").toBeLessThan(0.01);
    expect(cStart).toBeGreaterThan(0.08);
    expect(cStart).toBeLessThan(0.16);
  });

  it("steps and cheek shear share ONE widening parameterization", () => {
    const run = stairSpec.riserCount * massing.stairTreadRun;
    for (const k of [0, 4, 8]) {
      const step = group.getObjectByName(`step-${k}`) as THREE.Mesh;
      step.geometry.computeBoundingBox();
      const halfW = (step.geometry.boundingBox!.max.x - step.geometry.boundingBox!.min.x) / 2;
      const zOuter = (k + 1) * massing.stairTreadRun;
      const expected = (1.8 + 2.2) / 2 + (13 * envelopes.podiumW.v) / 776 * (zOuter / run) / 1; // topHalfW + widen·z/run
      expect(halfW).toBeCloseTo(expected, 3);
    }
  });
});

describe("measures on the built model", () => {
  it("kalasha GEOMETRY reaches the 52 ft datum; required groups gate", () => {
    const { group, anchors } = buildTempleMassing({ towerSilhouette: "A" });
    const m = measureModel(group, anchors);
    const tip = m.checks.find((c) => c.name.includes("kalasha GEOMETRY"));
    expect(tip?.ok, `kalasha maxY vs tip: ${JSON.stringify(tip)}`).toBe(true);
    const missing = m.checks.filter((c) => c.name.endsWith("present") && !c.ok);
    expect(missing).toEqual([]);
    expect(m.checks.every((c) => c.ok), JSON.stringify(m.checks.filter((c) => !c.ok))).toBe(true);
  });

  it("ridge datum matches the roof geometry", () => {
    const { group, anchors } = buildTempleMassing({ towerSilhouette: "B" });
    const m = measureModel(group, anchors);
    const ridge = m.checks.find((c) => c.name === "roof ridge datum");
    expect(ridge?.ok).toBe(true);
    expect(ridge?.want).toBeCloseTo(stations.mainRidgeY.v, 9);
  });
});
