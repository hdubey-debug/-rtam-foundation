/** The dvāra (doc §2.5): ~1.8 × 3.4 m clear, THREE stepped jambs, plain
 * stepped head, teak leaves set into the reveal, bronze ring pulls.
 * NO twelve-sun lintel (deferred v3.3); the chandraśilā sits with the
 * stair. Origin: opening center at x=0, THRESHOLD at y=0, wall exterior
 * face at z=0; jambs step INWARD toward the leaves.
 */
import * as THREE from "three/webgpu";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import type { MaterialLib } from "../materials/materials";
import { doorParts, doorSpec } from "./dimensions";
import type { BuiltPart } from "./podium";

const box = (w: number, h: number, d: number, x: number, y: number, z: number): THREE.BufferGeometry => {
  const g = new THREE.BoxGeometry(w, h, d);
  g.translate(x, y, z);
  return g;
};

export function buildDoor(lib: MaterialLib): BuiltPart {
  const group = new THREE.Group();
  group.name = "door";

  const w = doorSpec.w.v;
  const h = doorSpec.h.v;
  const p = doorParts;

  // ---- three stepped jambs: OUTERMOST PROUDEST, stepping IN toward the
  // leaves (GEO audit fixed the reversed order). Jambs stop UNDER their
  // head band; heads tile upward — no member passes through another.
  const jambParts: THREE.BufferGeometry[] = [];
  const jw = p.jambStepW;
  for (let i = 0; i < p.jambSteps; i++) {
    const inset = i * jw; // i=0 innermost frame at the opening
    const proud = (i + 1) * p.jambStepProud; // outermost (i=2) proudest
    const left = -(w / 2 + inset + jw / 2);
    const right = w / 2 + inset + jw / 2;
    const jambTop = h + i * jw; // stop under this frame's head band
    jambParts.push(box(jw, jambTop, proud, left, jambTop / 2, proud / 2));
    jambParts.push(box(jw, jambTop, proud, right, jambTop / 2, proud / 2));
    // head band spans the full frame width ABOVE the jambs
    const headW = w + 2 * inset + 2 * jw;
    jambParts.push(box(headW, jw, proud, 0, jambTop + jw / 2, proud / 2));
  }
  // plain stepped head cap above the outermost head band
  const outerW = w + 2 * (p.jambSteps * jw);
  const headY = h + p.jambSteps * jw;
  jambParts.push(
    box(outerW + 0.06, p.headStepH, p.jambSteps * p.jambStepProud, 0, headY + p.headStepH / 2, (p.jambSteps * p.jambStepProud) / 2),
  );

  const jambs = new THREE.Mesh(mergeGeometries(jambParts)!, lib.plaster);
  jambParts.forEach((g) => g.dispose());
  jambs.name = "door-jambs";
  jambs.castShadow = true;
  jambs.receiveShadow = true;
  group.add(jambs);

  // ---- teak leaves in the reveal; the FRONT FACE sits at −leafRecess
  // (GEO audit: the old center-placement claimed a depth it didn't have)
  const leafParts: THREE.BufferGeometry[] = [];
  const leafW = w / 2 - 0.01;
  const leafZ = -p.leafRecess - p.leafT / 2;
  for (const side of [-1, 1]) {
    leafParts.push(box(leafW, h - 0.04, p.leafT, side * (leafW / 2 + 0.01), h / 2, leafZ));
  }
  leafParts.push(box(0.09, h - 0.04, p.leafT + 0.02, 0, h / 2, leafZ)); // meeting stile
  const leaves = new THREE.Mesh(mergeGeometries(leafParts)!, lib.teak);
  leafParts.forEach((g) => g.dispose());
  leaves.name = "door-leaves";
  leaves.castShadow = false; // inside the reveal
  leaves.receiveShadow = true;
  group.add(leaves);

  // ---- bronze ring pulls
  const pullGeo = new THREE.TorusGeometry(p.pullR, 0.016, 10, 24);
  const pulls: THREE.BufferGeometry[] = [];
  for (const side of [-1, 1]) {
    const g = pullGeo.clone();
    // ring rests ON the leaf front face (tube back touches the teak)
    g.translate(side * 0.32, p.pullAtH, -p.leafRecess + 0.016);
    pulls.push(g);
  }
  pullGeo.dispose();
  const pullMesh = new THREE.Mesh(mergeGeometries(pulls)!, lib.bronze);
  pulls.forEach((g) => g.dispose());
  pullMesh.name = "door-pulls";
  pullMesh.castShadow = false;
  pullMesh.receiveShadow = true;
  group.add(pullMesh);

  const anchors: Record<string, THREE.Vector3> = {
    "door-pull": new THREE.Vector3(0.32, p.pullAtH, 0),
  };
  return { group, anchors };
}
