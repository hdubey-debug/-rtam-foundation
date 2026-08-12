/** buildTemple — the parametric model, driven ENTIRELY by dimensions.ts.
 * M2 stage: MASSING — plain volumes at real meters, including roof
 * envelopes and the tower (two silhouette candidates). Components replace
 * volumes milestone by milestone (M3 podium, M4 columns, …).
 */
import * as THREE from "three/webgpu";
import type { StageModel } from "../engine/createEngine";
import { createMaterialLib } from "../materials/materials";
import {
  bodyDepth,
  envelopes,
  massing,
  podiumHeight,
  stations,
  towerSpec,
  verandah,
  windowSpec,
  doorSpec,
} from "./dimensions";
import { hipPrismGeometry, pushTriOutward } from "./lib/hipPrism";
import { buildPodium } from "./podium";
import { buildStair } from "./stair";
import { buildColonnade } from "./colonnade";
import { buildWalls } from "./walls";
import { buildMoldings } from "./moldings";
import { buildBosses } from "./bosses";

export type TowerSilhouette = "A" | "B";

export interface TempleOptions {
  /** A = straight fourfold taper · B = curved nagara profile */
  towerSilhouette: TowerSilhouette;
}

/** fourfold tower contour half-width at parameter t (0 = spring, 1 = top).
 * A: linear taper. B: nagara curve (slow at the base, tightening toward
 * the crown — quadratic bezier pulled outward).
 */
function towerHalfWidth(t: number, silhouette: TowerSilhouette, base: number, top: number): number {
  if (silhouette === "A") return base + (top - base) * t;
  // B: quadratic bezier with control point holding the base width longer
  const c = base * 0.96;
  const u = 1 - t;
  return u * u * base + 2 * u * t * c + t * t * top;
}

export function buildTempleMassing(opts: TempleOptions): StageModel {
  const group = new THREE.Group();
  group.name = `massing-${opts.towerSilhouette.toLowerCase()}`;

  const lib = createMaterialLib();
  const { terracotta, sandstone } = lib;
  const gold = lib.gilt;

  const allAnchors: Record<string, THREE.Vector3> = {};
  const merge = (part: { group: THREE.Group; anchors: Record<string, THREE.Vector3> }, offset?: THREE.Vector3) => {
    if (offset) part.group.position.copy(offset);
    group.add(part.group);
    for (const [k, v] of Object.entries(part.anchors)) {
      allAnchors[k] = offset ? v.clone().add(offset) : v.clone();
    }
  };

  const add = (geo: THREE.BufferGeometry, mat: THREE.Material, name: string, y = 0, z = 0, x = 0) => {
    const mesh = new THREE.Mesh(geo, mat);
    mesh.name = name;
    mesh.position.set(x, y, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    group.add(mesh);
    return mesh;
  };

  const podD = envelopes.podiumD.v;
  const podH = podiumHeight.v;
  const bodyW = envelopes.structuralW.v;
  const bodyD = bodyDepth.v;
  const plateY = stations.plateY.v;

  // ---- podium: the five-course ring (M3 component, real profile)
  merge(buildPodium(lib));

  // depth closure: walk · porch · ten-bay body · walk (all derived)
  const frontWallZ = podD / 2 - envelopes.walk.v - verandah.projection.v;
  const bodyCenterZ = frontWallZ - bodyD / 2;

  // ---- walls + windows + door (M5): the opening schedule drives it
  merge(buildWalls(lib), new THREE.Vector3(0, 0, bodyCenterZ));

  // ---- beam band + cornice rings (M6) + the three boss courses
  merge(buildMoldings(lib), new THREE.Vector3(0, 0, bodyCenterZ));
  merge(buildBosses(lib)); // model frame: podium + body courses inside

  // ---- axial stair (M3 component): terrace edge = the podium front face
  merge(buildStair(lib), new THREE.Vector3(0, 0, podD / 2));

  // ---- verandah: the REAL colonnade (M4) at the walk line, + its roof
  const porchZ = podD / 2 - envelopes.walk.v;
  merge(buildColonnade(lib), new THREE.Vector3(0, podH, porchZ - massing.porchPostSize / 2));
  {
    const roofW = verandah.width.v + 2 * massing.verandahRoofSideOverhang;
    const roofD = verandah.projection.v + massing.verandahRoofFrontOverhang + massing.verandahRoofBackReturn;
    const roof = hipPrismGeometry({
      w: roofW,
      d: roofD,
      eaveY: 0,
      ridgeY: verandah.ridgeY.v - verandah.eaveY.v,
      ridgeInset: roofD * 0.45,
    });
    add(roof, terracotta, "verandah-roof", verandah.eaveY.v, frontWallZ - massing.verandahRoofBackReturn + roofD / 2);
  }

  // ---- main hip roof envelope
  const eaveW = bodyW + 2 * envelopes.eaveOverhang.v;
  const eaveD = bodyD + 2 * envelopes.eaveOverhang.v;
  {
    const roof = hipPrismGeometry({
      w: eaveW,
      d: eaveD,
      eaveY: 0,
      ridgeY: stations.mainRidgeY.v - plateY,
      ridgeInset: eaveW * massing.mainRoofRidgeInsetFactor,
    });
    add(roof, terracotta, "main-roof", plateY, bodyCenterZ);
  }

  // ---- tower: fourfold loft from the visible spring to the amalaka seat
  const towerZ = bodyCenterZ - bodyD / 2 + towerSpec.structuralBaseW.v / 2 + massing.towerRearGap;
  const springY = stations.towerSpringY.v;
  const amalakaRy = towerSpec.amalakaRx.v * towerSpec.amalakaRyOverRx;
  const amalakaCenterY = stations.amalakaTopY.v - amalakaRy;
  const loftTopY = amalakaCenterY - amalakaRy * 0.55;
  {
    // curb: plate → spring, hidden mostly inside the roof
    const curb = new THREE.BoxGeometry(towerSpec.roofCurbW.v, springY - plateY + 0.4, towerSpec.roofCurbW.v);
    add(curb, sandstone, "tower-curb", plateY + (springY - plateY) / 2, towerZ);

    // fourfold loft, constant vertex count per slice; winding forced
    // outward via radial hints (no hand-derived orders)
    type V3 = [number, number, number];
    const slices = 7;
    const halfBase = towerSpec.visibleSpringW.v / 2;
    const halfTop = towerSpec.towerTopW.v / 2;
    const positions: number[] = [];
    const ring = (t: number): V3[] => {
      const h = towerHalfWidth(t, opts.towerSilhouette, halfBase, halfTop);
      const y = springY + (loftTopY - springY) * t;
      return [
        [-h, y, -h],
        [h, y, -h],
        [h, y, h],
        [-h, y, h],
      ];
    };
    const sideHints: V3[] = [
      [0, 0, -1],
      [1, 0, 0],
      [0, 0, 1],
      [-1, 0, 0],
    ];
    for (let s = 0; s < slices - 1; s++) {
      const a = ring(s / (slices - 1));
      const b = ring((s + 1) / (slices - 1));
      for (let i = 0; i < 4; i++) {
        const j = (i + 1) % 4;
        pushTriOutward(positions, a[i], a[j], b[j], sideHints[i]);
        pushTriOutward(positions, a[i], b[j], b[i], sideHints[i]);
      }
    }
    const top = ring(1);
    pushTriOutward(positions, top[0], top[1], top[2], [0, 1, 0]);
    pushTriOutward(positions, top[0], top[2], top[3], [0, 1, 0]);
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(positions), 3));
    geo.computeVertexNormals();
    add(geo, sandstone, "tower-shaft", 0, towerZ);
  }

  // ---- crown: amalaka (ellipsoid massing) + kalasha to the LOCKED tip
  {
    const amalaka = new THREE.SphereGeometry(towerSpec.amalakaRx.v, 24, 12);
    amalaka.scale(1, towerSpec.amalakaRyOverRx, 1);
    add(amalaka, sandstone, "amalaka", amalakaCenterY, towerZ);

    const kalashaH = towerSpec.kalashaH.v;
    const tipY = stations.kalashaTipY.v;
    const kalasha = new THREE.ConeGeometry(0.34, kalashaH, 16);
    add(kalasha, gold, "kalasha", tipY - kalashaH / 2, towerZ);

    // dhvaja — reported only, excluded from the 52 ft
    const pole = new THREE.CylinderGeometry(0.03, 0.03, stations.dhvajaTopY.v - tipY + 0.6, 8);
    add(pole, gold, "dhvaja-pole", tipY + (stations.dhvajaTopY.v - tipY + 0.6) / 2 - 0.6, towerZ);
  }

  Object.assign(allAnchors, {
    "kalasha-tip": new THREE.Vector3(0, stations.kalashaTipY.v, towerZ),
    "door-center": new THREE.Vector3(0, podH + doorSpec.h.v / 2, frontWallZ),
    "tower-spring": new THREE.Vector3(towerSpec.visibleSpringW.v / 2, springY, towerZ),
    "main-eave": new THREE.Vector3(eaveW / 2, plateY, bodyCenterZ),
    "verandah-eave": new THREE.Vector3(0, verandah.eaveY.v, porchZ),
    "beam-band": new THREE.Vector3(bodyW / 2, (stations.beamBandBottomY.v + stations.beamBandTopY.v) / 2, bodyCenterZ),
    "l1-window-sill": new THREE.Vector3(bodyW / 2, stations.l1SillY.v, bodyCenterZ),
  });

  void windowSpec; // window volumes join the massing at M5 via openings.ts

  return { group, anchors: allAnchors };
}
