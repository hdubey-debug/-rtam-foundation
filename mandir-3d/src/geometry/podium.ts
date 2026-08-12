/** The podium — the five doc-locked courses as ONE rectProfileRing around
 * the founder envelope (upāna rough foot · jagatī world-face · kumuda
 * smooth torus · kaṇṭha pearl-course recess · kapota cap + drip) plus the
 * terrace slab. The kaṇṭha's Ø60 boss course arrives at M6; the kumuda
 * roll stays UNCARVED (canon: petal roll reserved).
 *
 * Binding: the ring's dx=0 plane IS the 52 × 88 ft outside finished
 * envelope; every course offsets inward. Real meters, centered origin.
 */
import * as THREE from "three/webgpu";
import type { MaterialLib } from "../materials/materials";
import { envelopes, podiumCourses, podiumProfile } from "./dimensions";
import { rectProfileRing, type ProfileSample } from "./lib/rectProfileRing";

export interface BuiltPart {
  group: THREE.Group;
  anchors: Record<string, THREE.Vector3>;
}

/** the podium section, bottom → top */
export function podiumSectionProfile(): ProfileSample[] {
  const c = podiumCourses;
  const p = podiumProfile;
  const y1 = c.upana.v; // 0.15
  const y2 = y1 + c.jagati.v; // 0.45
  const y3 = y2 + c.kumuda.v; // 0.60
  const y4 = y3 + c.kantha.v; // 0.75
  const y5 = y4 + c.kapota.v; // 0.90

  const profile: ProfileSample[] = [
    { dx: 0, dy: 0 },
    { dx: 0, dy: y1 }, // upāna face, plumb at the envelope
    { dx: -p.jagatiInset.v, dy: y1 }, // ONE step in to the jagatī face
    { dx: -p.jagatiInset.v, dy: y2 }, // jagatī tall plain face
  ];
  // kumuda — TRUE half-ellipse torus roll: horizontal takeoff at both
  // ends, apex flush − kumudaApexInset at mid-height (codex GEO: the sin
  // bulge had diagonal endpoint tangents; a torus springs horizontally)
  const n = podiumProfile.arcSamples;
  const inset = p.jagatiInset.v;
  const bulge = inset - p.kumudaApexInset.v;
  for (let i = 1; i <= n; i++) {
    const th = (Math.PI * i) / n;
    profile.push({
      dx: -inset + bulge * Math.sin(th), // ellipse horizontal component
      dy: y2 + (c.kumuda.v / 2) * (1 - Math.cos(th)), // vertical — horizontal takeoff at both ends
    });
  }
  // kaṇṭha — the recess (boss course home)
  profile.push({ dx: -p.kanthaRecess.v, dy: y3 });
  profile.push({ dx: -p.kanthaRecess.v, dy: y4 });
  // kapota underside with the REAL drip: soffit out → groove up/over/down
  // → lip → face. Water tracking the soffit falls at the groove.
  const face = -p.kapotaFaceInset.v;
  const lipInner = face - p.dripLipW.v;
  const grooveInner = lipInner - p.dripGrooveW.v;
  profile.push({ dx: grooveInner, dy: y4 }); // soffit out to the groove
  profile.push({ dx: grooveInner, dy: y4 + p.dripGrooveDepth.v }); // groove inner wall
  profile.push({ dx: lipInner, dy: y4 + p.dripGrooveDepth.v }); // groove ceiling
  profile.push({ dx: lipInner, dy: y4 }); // groove outer wall (the drip)
  profile.push({ dx: face, dy: y4 }); // the lip
  profile.push({ dx: face, dy: y5 - 0.02 }); // kapota fascia
  profile.push({ dx: -p.kapotaTopInset.v, dy: y5 }); // top chamfer sheds
  return profile;
}

export function buildPodium(lib: MaterialLib): BuiltPart {
  const group = new THREE.Group();
  group.name = "podium";

  const w = envelopes.podiumW.v;
  const d = envelopes.podiumD.v;

  const ring = new THREE.Mesh(
    rectProfileRing({ w, d, baseY: 0, profile: podiumSectionProfile(), capBottom: true }),
    lib.granite,
  );
  ring.name = "podium-ring";
  ring.castShadow = true;
  ring.receiveShadow = true;
  group.add(ring);

  // terrace slab fills the ring's top opening
  const topInset = podiumProfile.kapotaTopInset.v;
  const slabT = 0.06;
  const slab = new THREE.Mesh(
    new THREE.BoxGeometry(w - 2 * topInset + 0.02, slabT, d - 2 * topInset + 0.02),
    lib.graniteDark,
  );
  slab.name = "terrace-slab";
  slab.position.y = 0.9 - slabT / 2;
  slab.receiveShadow = true;
  group.add(slab);

  // anchors ON their surfaces (codex GEO: the old ones floated off-plan)
  const topInsetA = podiumProfile.kapotaTopInset.v;
  const apex = podiumProfile.kumudaApexInset.v;
  const anchors: Record<string, THREE.Vector3> = {
    "podium-corner": new THREE.Vector3(w / 2 - topInsetA, 0.9, d / 2 - topInsetA),
    "kumuda-edge": new THREE.Vector3(w / 2 - apex, 0.525, d / 2 - apex),
  };
  return { group, anchors };
}
