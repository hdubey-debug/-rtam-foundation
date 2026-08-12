/** M0 TECHNICAL SPIKE FIXTURE — a deliberately crude mini-temple whose only
 * job is to exercise every engine risk at once on SwiftShader:
 *   TSL node materials (world-space variation) · InstancedMesh (columns,
 *   boss course) · shadow casting policy (small bosses do NOT cast) ·
 *   transparent-canvas composite · warm-up RT · export-clone GLB.
 * It is NOT the temple. buildTemple() replaces it from M2 on; this file
 * then retires into the QA fixtures.
 *
 * Real meters. Deterministic — no randomness anywhere.
 */
import * as THREE from "three/webgpu";
import { color, mix, positionWorld } from "three/tsl";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import type { StageModel } from "../engine/createEngine";

interface PBRSpec {
  color: number;
  colorLight: number;
  roughness: number;
  metalness: number;
  name: string;
}

/** Standard node material with subtle world-space tonal variation and an
 * explicit export-PBR record (the export clone reads userData.exportPBR —
 * node materials don't survive GLTFExporter as PBR in r185). */
function variedMaterial(spec: PBRSpec): THREE.MeshStandardNodeMaterial {
  const mat = new THREE.MeshStandardNodeMaterial({
    color: spec.color,
    roughness: spec.roughness,
    metalness: spec.metalness,
  });
  const n = positionWorld.x
    .mul(7.3)
    .sin()
    .mul(positionWorld.z.mul(5.1).sin())
    .mul(positionWorld.y.mul(6.7).sin())
    .mul(0.5)
    .add(0.5);
  mat.colorNode = mix(color(spec.color), color(spec.colorLight), n.mul(0.35));
  mat.name = spec.name;
  mat.userData.exportPBR = {
    color: spec.color,
    roughness: spec.roughness,
    metalness: spec.metalness,
  };
  return mat;
}

export function buildFixture(): StageModel {
  const group = new THREE.Group();
  group.name = "m0-fixture";

  const granite = variedMaterial({
    name: "granite",
    color: 0x66625b,
    colorLight: 0x7d7970,
    roughness: 0.92,
    metalness: 0.0,
  });
  const plaster = variedMaterial({
    name: "lime-plaster",
    color: 0xddd2bc,
    colorLight: 0xeae1cf,
    roughness: 0.85,
    metalness: 0.0,
  });
  const terracotta = variedMaterial({
    name: "terracotta",
    color: 0x96482f,
    colorLight: 0xa85a3d,
    roughness: 0.78,
    metalness: 0.0,
  });
  const sandstone = variedMaterial({
    name: "sandstone",
    color: 0xc4a97e,
    colorLight: 0xd2ba92,
    roughness: 0.88,
    metalness: 0.0,
  });
  const gold = variedMaterial({
    name: "gilt",
    color: 0xc8a15a,
    colorLight: 0xe0bc74,
    roughness: 0.32,
    metalness: 0.9,
  });

  const solid = (
    geo: THREE.BufferGeometry,
    mat: THREE.Material,
    name: string,
    x = 0,
    y = 0,
    z = 0,
  ): THREE.Mesh => {
    const mesh = new THREE.Mesh(geo, mat);
    mesh.name = name;
    mesh.position.set(x, y, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    group.add(mesh);
    return mesh;
  };

  // ---- podium: 12 × 0.9 × 8 m
  solid(new THREE.BoxGeometry(12, 0.9, 8), granite, "podium", 0, 0.45, 0);

  // ---- body: two-story block on the podium
  solid(new THREE.BoxGeometry(9.6, 3.4, 5.6), plaster, "body", 0, 0.9 + 1.7, 0);

  // ---- roof: rectangular hip (4-sided cone, squashed)
  const roofGeo = new THREE.ConeGeometry(1, 1, 4, 1);
  roofGeo.rotateY(Math.PI / 4);
  roofGeo.scale(7.4, 1.5, 4.6);
  const roof = solid(roofGeo, terracotta, "roof", 0, 0.9 + 3.4 + 0.75, 0);
  roof.castShadow = true;

  // ---- colonnade: 6 columns, ONE merged geometry → InstancedMesh
  const columnParts: THREE.BufferGeometry[] = [];
  {
    const pedestal = new THREE.BoxGeometry(0.5, 0.45, 0.5);
    pedestal.translate(0, 0.225, 0);
    const shaft = new THREE.CylinderGeometry(0.16, 0.18, 1.9, 12);
    shaft.translate(0, 0.45 + 0.95, 0);
    const abacus = new THREE.BoxGeometry(0.46, 0.22, 0.46);
    abacus.translate(0, 0.45 + 1.9 + 0.11, 0);
    columnParts.push(pedestal, shaft, abacus);
  }
  const columnGeo = mergeGeometries(columnParts)!;
  columnParts.forEach((g) => g.dispose());
  const columns = new THREE.InstancedMesh(columnGeo, plaster, 6);
  columns.name = "colonnade";
  columns.castShadow = true;
  columns.receiveShadow = true;
  {
    const m = new THREE.Matrix4();
    for (let i = 0; i < 6; i++) {
      const x = -4.1 + i * 1.64;
      m.makeTranslation(x, 0.9, 3.5); // proud of the wall — a porch line
      columns.setMatrixAt(i, m);
    }
    columns.instanceMatrix.needsUpdate = true;
    columns.computeBoundingBox();
    columns.computeBoundingSphere();
  }
  group.add(columns);

  // ---- boss course along the front beam: Ø90 @ 180 mm — instanced
  // hemispheres. Small bosses do NOT cast shadows (1–3 texels in a 2048
  // map would shimmer); they still receive light and shade.
  const bossGeo = new THREE.SphereGeometry(0.045, 12, 6, 0, Math.PI * 2, 0, Math.PI / 2);
  bossGeo.rotateX(Math.PI / 2); // dome points +Z, out of the wall
  const bossCount = 53; // 9.6 m front / 0.18 m pitch — a non-system count
  const bosses = new THREE.InstancedMesh(bossGeo, sandstone, bossCount);
  bosses.name = "boss-course-front";
  bosses.castShadow = false;
  bosses.receiveShadow = true;
  {
    const m = new THREE.Matrix4();
    for (let i = 0; i < bossCount; i++) {
      const x = -0.18 * ((bossCount - 1) / 2) + i * 0.18;
      m.makeTranslation(x, 0.9 + 3.05, 2.8);
      bosses.setMatrixAt(i, m);
    }
    bosses.instanceMatrix.needsUpdate = true;
    bosses.computeBoundingBox();
    bosses.computeBoundingSphere();
  }
  group.add(bosses);

  // ---- tower at the rear: 4-sided taper, flat-faceted, PENETRATING the
  // roof (base at the body top, not floating on the roof surface)
  const towerBaseY = 0.9 + 3.4;
  const towerH = 3.6;
  let towerGeo: THREE.BufferGeometry = new THREE.CylinderGeometry(0.62, 1.15, towerH, 4, 1);
  towerGeo.rotateY(Math.PI / 4);
  towerGeo = towerGeo.toNonIndexed();
  towerGeo.computeVertexNormals(); // flat facets — 4 faces must READ as 4 faces
  const towerTopY = towerBaseY + towerH;
  solid(towerGeo, sandstone, "tower", 0, towerBaseY + towerH / 2, -1.2);

  const amalakaGeo = new THREE.SphereGeometry(0.55, 20, 12);
  amalakaGeo.scale(1, 0.38, 1);
  solid(amalakaGeo, sandstone, "amalaka", 0, towerTopY + 0.18, -1.2);

  const kalashaTipY = towerTopY + 0.36 + 0.55;
  const kalashaGeo = new THREE.ConeGeometry(0.16, 0.55, 12);
  solid(kalashaGeo, gold, "kalasha", 0, towerTopY + 0.36 + 0.275, -1.2);

  return {
    group,
    anchors: {
      "kalasha-tip": new THREE.Vector3(0, kalashaTipY, -1.2),
      "stair-front": new THREE.Vector3(0, 0.9, 2.8),
      "cornice-boss": new THREE.Vector3(0, 0.9 + 3.05, 2.8),
    },
  };
}
