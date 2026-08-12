/** The axial stair — the dvāra. Nine risers widening toward the ground
 * (+13 du per side over the run), splayed trapezoid cheek walls with
 * sloped caps, ball finials on the newels (locked render, allowlisted),
 * chandraśilā at the approach.
 *
 * Built at origin: the terrace edge is the z=0 plane, steps descend
 * toward +z, top tread flush with the 0.900 terrace. The CALLER places
 * the group at the podium front face.
 */
import * as THREE from "three/webgpu";
import type { MaterialLib } from "../materials/materials";
import { doorSpec, facadeGrid, massing, stairSpec } from "./dimensions";
import type { BuiltPart } from "./podium";

export function buildStair(lib: MaterialLib): BuiltPart {
  const group = new THREE.Group();
  group.name = "stair";

  const risers = stairSpec.riserCount; // 9
  const riserH = stairSpec.riserH.v; // 0.1
  const tread = massing.stairTreadRun; // 0.3
  const run = risers * tread;
  const topHalfW = (doorSpec.w.v + 2.2) / 2; // door + margins at the top
  const widen = stairSpec.widenPerSideDu * facadeGrid.mPerDu.v; // 13 du ≈ 0.2655

  const solid = (geo: THREE.BufferGeometry, mat: THREE.Material, name: string): THREE.Mesh => {
    const mesh = new THREE.Mesh(geo, mat);
    mesh.name = name;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    group.add(mesh);
    return mesh;
  };

  // widening is parameterized ONCE: halfWidthAt(z) — steps and cheek
  // shear share it (codex GEO: two parameterizations drifted ~30 mm)
  const halfWidthAt = (z: number) => topHalfW + (widen * z) / run;

  // ---- steps: solid boxes, each full height from the ground, widening
  for (let k = 0; k < risers; k++) {
    const topY = 0.9 - k * riserH;
    const zOuter = (k + 1) * tread;
    const halfW = halfWidthAt(zOuter);
    const step = solid(new THREE.BoxGeometry(halfW * 2, topY, tread), lib.granite, `step-${k}`);
    step.position.set(0, topY / 2, k * tread + tread / 2);
  }

  // ---- cheek walls: rake PARALLEL to the nosing line (slope −riser/
  // tread, constant 0.12 clearance), then a horizontal newel zone at the
  // bottom — codex GEO: the old rake diverged 109→365 mm
  const cheekT = 0.32;
  const rakeSlope = riserH / tread; // 1/3 — rake top y = 1.02 − slope·z, constant above the nosing
  const newelZoneY = 0.42;
  const rakeStartZ = -0.05;
  // measure from the ACTUAL line start, or the slope tilts off −1/3
  const rakeEndZ = rakeStartZ + (1.02 - newelZoneY) / rakeSlope;
  const cheekEndZ = run - 0.06;
  const rake = new THREE.Shape();
  rake.moveTo(rakeStartZ, 0);
  rake.lineTo(rakeStartZ, 1.02);
  rake.lineTo(rakeEndZ, newelZoneY);
  rake.lineTo(cheekEndZ, newelZoneY);
  rake.lineTo(cheekEndZ, 0);
  rake.closePath();

  // LEFT cheek: shape (run,height) → rotateY(−π/2) puts run along +z,
  // thickness toward −x (det +1, winding intact); shear splays −x outward
  const leftGeo = new THREE.ExtrudeGeometry(rake, { depth: cheekT, bevelEnabled: false });
  leftGeo.rotateY(-Math.PI / 2);
  const splay = widen / run;
  const shear = new THREE.Matrix4();
  shear.set(1, 0, -splay, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1);
  leftGeo.applyMatrix4(shear);

  // RIGHT cheek: mirror across x and RESTORE winding explicitly —
  // positions AND uvs swap together (codex GEO: uv-only-positions bug)
  const mirrorX = (src: THREE.BufferGeometry): THREE.BufferGeometry => {
    const g = src.toNonIndexed();
    g.applyMatrix4(new THREE.Matrix4().makeScale(-1, 1, 1));
    const pos = g.getAttribute("position") as THREE.BufferAttribute;
    const uv = g.getAttribute("uv") as THREE.BufferAttribute | undefined;
    for (let i = 0; i < pos.count; i += 3) {
      for (let c = 0; c < 3; c++) {
        const a = pos.getComponent(i + 1, c);
        pos.setComponent(i + 1, c, pos.getComponent(i + 2, c));
        pos.setComponent(i + 2, c, a);
      }
      if (uv) {
        for (let c = 0; c < 2; c++) {
          const a = uv.getComponent(i + 1, c);
          uv.setComponent(i + 1, c, uv.getComponent(i + 2, c));
          uv.setComponent(i + 2, c, a);
        }
      }
    }
    g.computeVertexNormals();
    return g;
  };
  const rightGeo = mirrorX(leftGeo);

  const cheekL = solid(leftGeo, lib.granite, "cheek-l");
  cheekL.position.x = -topHalfW;
  const cheekR = solid(rightGeo, lib.granite, "cheek-r");
  cheekR.position.x = topHalfW;

  // ---- newel blocks + ball finials at both ends of both cheeks
  const newel = 0.44;
  const ballR = 0.17;
  const finialAt = (x: number, z: number, topY: number, i: number) => {
    const block = solid(new THREE.BoxGeometry(newel, 0.36, newel), lib.granite, `newel-${i}`);
    block.position.set(x, topY + 0.18, z);
    const ball = solid(new THREE.SphereGeometry(ballR, 20, 14), lib.graniteDark, `finial-${i}`);
    ball.position.set(x, topY + 0.36 + ballR * 0.92, z);
  };
  // newel centers ride the SHEARED cheek centerlines exactly
  const cheekMid = (side: -1 | 1, z: number) => side * (topHalfW + cheekT / 2 + (widen * z) / run);
  const zTop = 0.16;
  const zBottom = run - 0.3;
  finialAt(cheekMid(-1, zTop), zTop, 1.02, 0);
  finialAt(cheekMid(1, zTop), zTop, 1.02, 1);
  finialAt(cheekMid(-1, zBottom), zBottom, newelZoneY, 2);
  finialAt(cheekMid(1, zBottom), zBottom, newelZoneY, 3);

  // ---- chandraśilā: half-ellipse threshold slab at the approach
  {
    const rx = topHalfW + widen + 0.15;
    const rz = 0.75;
    const shape = new THREE.Shape();
    shape.moveTo(-rx, 0);
    shape.absellipse(0, 0, rx, rz, Math.PI, 0, true, 0);
    shape.lineTo(-rx, 0);
    const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.14, bevelEnabled: false });
    geo.rotateX(Math.PI / 2); // lay flat; ellipse bulges +z
    const slab = solid(geo, lib.graniteDark, "chandrashila");
    slab.position.set(0, 0.14, run);
  }

  const anchors: Record<string, THREE.Vector3> = {
    "stair-base": new THREE.Vector3(0, 0, run),
    chandrashila: new THREE.Vector3(0, 0.14, run + 0.5),
  };
  return { group, anchors };
}
