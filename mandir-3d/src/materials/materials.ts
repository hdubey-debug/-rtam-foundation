/** The material library. Every material is a MeshStandardNodeMaterial
 * with subtle TSL world-space tonal variation AND an explicit
 * userData.exportPBR record — the export clone reads the record because
 * node materials don't survive GLTFExporter as PBR in r185.
 * Deep variation work (block joints, plaster wash) is the M9 polish;
 * these are the stable bases.
 */
import * as THREE from "three/webgpu";
import { color, mix, positionWorld } from "three/tsl";

export interface MaterialSpec {
  name: string;
  color: number;
  colorLight: number;
  roughness: number;
  metalness: number;
  /** variation strength 0..1 */
  variation?: number;
  /** world-space noise frequency (stage units) */
  frequency?: number;
}

function varied(spec: MaterialSpec): THREE.MeshStandardNodeMaterial {
  const mat = new THREE.MeshStandardNodeMaterial({
    color: spec.color,
    roughness: spec.roughness,
    metalness: spec.metalness,
  });
  const f = spec.frequency ?? 6;
  const n = positionWorld.x
    .mul(f * 1.21)
    .sin()
    .mul(positionWorld.z.mul(f * 0.83).sin())
    .mul(positionWorld.y.mul(f * 1.07).sin())
    .mul(0.5)
    .add(0.5);
  mat.colorNode = mix(color(spec.color), color(spec.colorLight), n.mul(spec.variation ?? 0.3));
  mat.name = spec.name;
  mat.userData.exportPBR = { color: spec.color, roughness: spec.roughness, metalness: spec.metalness };
  return mat;
}

/** ONE library instance per model build — materials are shared across
 * components so instancing/merging stays material-homogeneous. */
export interface MaterialLib {
  granite: THREE.MeshStandardNodeMaterial;
  graniteDark: THREE.MeshStandardNodeMaterial;
  plaster: THREE.MeshStandardNodeMaterial;
  terracotta: THREE.MeshStandardNodeMaterial;
  sandstone: THREE.MeshStandardNodeMaterial;
  gilt: THREE.MeshStandardNodeMaterial;
  teak: THREE.MeshStandardNodeMaterial;
  bronze: THREE.MeshStandardNodeMaterial;
  jaliDark: THREE.MeshStandardNodeMaterial;
}

export function createMaterialLib(): MaterialLib {
  return {
    granite: varied({
      name: "granite",
      color: 0x6b6760,
      colorLight: 0x7d7970,
      roughness: 0.92,
      metalness: 0,
      variation: 0.3,
      frequency: 9,
    }),
    graniteDark: varied({
      name: "granite-dark",
      color: 0x57534d,
      colorLight: 0x66625b,
      roughness: 0.94,
      metalness: 0,
      variation: 0.25,
      frequency: 9,
    }),
    plaster: varied({
      name: "lime-plaster",
      color: 0xddd2bc,
      colorLight: 0xeae1cf,
      roughness: 0.85,
      metalness: 0,
      variation: 0.28,
      frequency: 4,
    }),
    terracotta: varied({
      name: "terracotta",
      color: 0x96482f,
      colorLight: 0xa85a3d,
      roughness: 0.78,
      metalness: 0,
      variation: 0.32,
      frequency: 7,
    }),
    sandstone: varied({
      name: "sandstone",
      color: 0xc9b188,
      colorLight: 0xd8c09a,
      roughness: 0.88,
      metalness: 0,
      variation: 0.3,
      frequency: 5,
    }),
    gilt: varied({
      name: "gilt",
      color: 0xc8a15a,
      colorLight: 0xe0bc74,
      roughness: 0.32,
      metalness: 0.9,
      variation: 0.2,
      frequency: 12,
    }),
    teak: varied({
      name: "teak",
      color: 0x5a3a24,
      colorLight: 0x6b4830,
      roughness: 0.7,
      metalness: 0,
      variation: 0.35,
      frequency: 14,
    }),
    bronze: varied({
      name: "bronze",
      color: 0x8a6a3a,
      colorLight: 0x9b7a45,
      roughness: 0.45,
      metalness: 0.85,
      variation: 0.2,
      frequency: 10,
    }),
    jaliDark: varied({
      name: "jali-dark",
      color: 0x2e2a24,
      colorLight: 0x3a352d,
      roughness: 0.9,
      metalness: 0,
      variation: 0.2,
      frequency: 8,
    }),
  };
}

export function disposeMaterialLib(lib: MaterialLib): void {
  Object.values(lib).forEach((m) => m.dispose());
}
