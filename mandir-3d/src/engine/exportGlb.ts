/** EXPORT CLONE — r185's GLTFExporter does not recognize node materials as
 * PBR (they'd export as metallic 0 / roughness 1 defaults), so the export
 * path never sends the live scene. It rebuilds:
 *   · every material  → a real MeshStandardMaterial from userData.exportPBR
 *   · every InstancedMesh → ONE merged geometry per mesh (not thousands of
 *     nodes, and no EXT_mesh_gpu_instancing — Blender-safe)
 *   · every transform → baked relative to the model root, so the GLB is in
 *     REAL METERS no matter how the stage wrapper is scaled.
 */
import * as THREE from "three/webgpu";
import { GLTFExporter } from "three/addons/exporters/GLTFExporter.js";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";

export interface ExportPBR {
  color: number;
  roughness: number;
  metalness: number;
}

function exportMaterialFor(
  src: THREE.Material,
  cache: Map<THREE.Material, THREE.MeshStandardMaterial>,
): THREE.MeshStandardMaterial {
  const hit = cache.get(src);
  if (hit) return hit;
  const pbr = (src.userData?.exportPBR ?? {}) as Partial<ExportPBR>;
  const anySrc = src as unknown as {
    color?: THREE.Color;
    roughness?: number;
    metalness?: number;
  };
  const mat = new THREE.MeshStandardMaterial({
    color: pbr.color ?? anySrc.color?.getHex() ?? 0xffffff,
    roughness: pbr.roughness ?? anySrc.roughness ?? 1,
    metalness: pbr.metalness ?? anySrc.metalness ?? 0,
  });
  mat.name = src.name || "material";
  cache.set(src, mat);
  return mat;
}

function firstMaterial(m: THREE.Material | THREE.Material[]): THREE.Material {
  return Array.isArray(m) ? m[0] : m;
}

/** Build the exportable clone of `real` (a real-meters model root). */
export function buildExportClone(real: THREE.Object3D): THREE.Group {
  real.updateWorldMatrix(true, true);
  const invRoot = real.matrixWorld.clone().invert();
  const out = new THREE.Group();
  out.name = (real.name || "model") + "-export";
  const matCache = new Map<THREE.Material, THREE.MeshStandardMaterial>();

  real.traverse((obj) => {
    if (!(obj as THREE.Mesh).isMesh) return;
    const rel = invRoot.clone().multiply(obj.matrixWorld);

    if ((obj as THREE.InstancedMesh).isInstancedMesh) {
      const inst = obj as THREE.InstancedMesh;
      const parts: THREE.BufferGeometry[] = [];
      const im = new THREE.Matrix4();
      for (let i = 0; i < inst.count; i++) {
        inst.getMatrixAt(i, im);
        const g = inst.geometry.clone();
        g.applyMatrix4(rel.clone().multiply(im));
        parts.push(g);
      }
      const merged = mergeGeometries(parts);
      parts.forEach((g) => g.dispose());
      if (!merged) return;
      const mesh = new THREE.Mesh(merged, exportMaterialFor(firstMaterial(inst.material), matCache));
      mesh.name = inst.name || "instanced";
      out.add(mesh);
      return;
    }

    const m = obj as THREE.Mesh;
    const g = m.geometry.clone().applyMatrix4(rel);
    const mesh = new THREE.Mesh(g, exportMaterialFor(firstMaterial(m.material), matCache));
    mesh.name = m.name || "mesh";
    out.add(mesh);
  });

  return out;
}

function disposeClone(clone: THREE.Group): void {
  clone.traverse((obj) => {
    const mesh = obj as THREE.Mesh;
    if (mesh.isMesh) {
      mesh.geometry.dispose();
      firstMaterial(mesh.material).dispose();
    }
  });
}

export async function exportGlb(real: THREE.Object3D): Promise<ArrayBuffer> {
  const clone = buildExportClone(real);
  try {
    const exporter = new GLTFExporter();
    const result = await exporter.parseAsync(clone, { binary: true });
    return result as ArrayBuffer;
  } finally {
    disposeClone(clone);
  }
}
