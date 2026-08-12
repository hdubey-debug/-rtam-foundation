/** The molding bands (M6): the inter-floor BEAM BAND and the CORNICE
 * under the plate — closed rectProfileRings around the body envelope.
 * Their faces host the boss courses (bosses.ts). Precise moldings are the
 * exterior's second permitted language (law 4) — profiles only, no
 * ornament here.
 *
 * Local frame: body center at origin (the CALLER offsets to bodyCenterZ).
 */
import * as THREE from "three/webgpu";
import type { MaterialLib } from "../materials/materials";
import { bandSpec, bodyDepth, envelopes, stations } from "./dimensions";
import { rectProfileRing, type ProfileSample } from "./lib/rectProfileRing";
import type { BuiltPart } from "./podium";

export function beamBandProfile(): ProfileSample[] {
  const b0 = stations.beamBandBottomY.v; // 5.05
  const b1 = stations.beamBandTopY.v; // 5.45
  const p = bandSpec.beamProud.v;
  const s = bandSpec.beamStep.v;
  const o = bandSpec.profileSurfaceOffset;
  return [
    { dx: o, dy: b0 }, // hairline off the wall face (never coplanar)
    { dx: p, dy: b0 + s }, // bottom step out
    { dx: p, dy: b1 - s }, // the face carrying the Ø90 course
    { dx: o, dy: b1 }, // top step back
  ];
}

export function corniceProfile(): ProfileSample[] {
  const y0 = bandSpec.corniceBottomY.v; // 8.70
  const plate = stations.plateY.v; // 9.144
  const f = bandSpec.corniceFasciaProud.v;
  const c = bandSpec.coronaProud.v;
  const s = bandSpec.corniceSteps; // NAMED steps — the boss register
  const o = bandSpec.profileSurfaceOffset; // derives from the same values
  return [
    { dx: o, dy: y0 },
    { dx: s.firstStepProud, dy: y0 + s.firstStepRise },
    { dx: s.firstStepProud, dy: y0 + s.grooveTop }, // shadow groove face
    { dx: f, dy: y0 + s.fasciaBottom }, // step to the boss fascia
    { dx: f, dy: y0 + s.fasciaTop }, // the Ø50 course rides here
    { dx: c, dy: y0 + s.coronaBottom }, // corona steps out
    { dx: c - s.dripInset, dy: y0 + s.dripBottom }, // drip notch
    { dx: c, dy: y0 + s.dripTop },
    { dx: c, dy: plate - 0.02 }, // corona face
    { dx: s.plateReturnInset, dy: plate }, // top returns to the plate
  ];
}

export function buildMoldings(lib: MaterialLib): BuiltPart {
  const group = new THREE.Group();
  group.name = "moldings";

  const w = envelopes.structuralW.v;
  const d = bodyDepth.v;

  const beam = new THREE.Mesh(
    rectProfileRing({ w, d, baseY: 0, profile: beamBandProfile() }),
    lib.plaster,
  );
  beam.name = "beam-band";
  beam.castShadow = true;
  beam.receiveShadow = true;
  group.add(beam);

  const cornice = new THREE.Mesh(
    rectProfileRing({ w, d, baseY: 0, profile: corniceProfile() }),
    lib.plaster,
  );
  cornice.name = "cornice";
  cornice.castShadow = true;
  cornice.receiveShadow = true;
  group.add(cornice);

  const anchors: Record<string, THREE.Vector3> = {
    "cornice-boss": new THREE.Vector3(
      w / 2 + bandSpec.corniceFasciaProud.v,
      bandSpec.corniceBossCenterY.v, // the SAME register the bosses use
      0,
    ),
  };
  return { group, anchors };
}
