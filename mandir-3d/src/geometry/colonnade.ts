/** The verandah colonnade: six columns = five porch bays, instanced as
 * two material-homogeneous InstancedMeshes (granite pedestals / plaster
 * stacks). Built at origin: columns stand on y=0 (the terrace), axis line
 * along x, z=0 at the column centers — the CALLER places the group.
 */
import * as THREE from "three/webgpu";
import type { MaterialLib } from "../materials/materials";
import { verandah } from "./dimensions";
import { buildColumnGeometry } from "./column";
import type { BuiltPart } from "./podium";

export const COLONNADE_COUNT = 6; // six posts = five bays (non-system count)

export function buildColonnade(lib: MaterialLib): BuiltPart {
  const group = new THREE.Group();
  group.name = "colonnade";

  const { pedestal, upper, totalH } = buildColumnGeometry();
  const span = verandah.width.v;

  const make = (geo: THREE.BufferGeometry, mat: THREE.Material, name: string): THREE.InstancedMesh => {
    const inst = new THREE.InstancedMesh(geo, mat, COLONNADE_COUNT);
    inst.name = name;
    inst.castShadow = true;
    inst.receiveShadow = true;
    const m = new THREE.Matrix4();
    for (let i = 0; i < COLONNADE_COUNT; i++) {
      const x = -span / 2 + (i * span) / (COLONNADE_COUNT - 1);
      m.makeTranslation(x, 0, 0);
      inst.setMatrixAt(i, m);
    }
    inst.instanceMatrix.needsUpdate = true;
    inst.computeBoundingBox();
    inst.computeBoundingSphere();
    group.add(inst);
    return inst;
  };

  make(pedestal, lib.granite, "colonnade-pedestals");
  make(upper, lib.plaster, "colonnade-stacks");

  const anchors: Record<string, THREE.Vector3> = {
    column: new THREE.Vector3(-span / 2, totalH * 0.55, 0),
  };
  return { group, anchors };
}
