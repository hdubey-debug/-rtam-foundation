/** Normalize a real-meters model into the museum frame: footprint
 * (max of width/depth) → 2.0 stage units, base → y=0, centered in x/z.
 *
 * Everything downstream that means a PHYSICAL length (pin lift, ground
 * clearance, shadow normalBias…) is written in meters and converted via
 * `toStage` — never hardcoded in stage units (scale differs per item).
 */
import * as THREE from "three/webgpu";

export const TARGET_FOOTPRINT = 2.0;

export interface NormalizedItem {
  /** stage-space wrapper: scaled, base at y=0, centered */
  root: THREE.Group;
  /** the original real-meters group (export + measures read THIS) */
  real: THREE.Object3D;
  /** stage units per meter */
  scale: number;
  stageBounds: THREE.Box3;
  realBounds: THREE.Box3;
  toStage(meters: number): number;
  /** map a point in the model's ORIGINAL real-meter frame → stage space */
  toStagePoint(v: THREE.Vector3): THREE.Vector3;
}

export function normalizeModel(real: THREE.Object3D): NormalizedItem {
  real.updateWorldMatrix(true, true);
  const realBounds = new THREE.Box3().setFromObject(real);
  const size = realBounds.getSize(new THREE.Vector3());
  const center = realBounds.getCenter(new THREE.Vector3());
  const footprint = Math.max(size.x, size.z);
  const scale = footprint > 0 ? TARGET_FOOTPRINT / footprint : 1;

  // recenter in meters first, then scale the wrapper
  real.position.set(-center.x, -realBounds.min.y, -center.z);

  const root = new THREE.Group();
  root.name = "stage-item";
  root.scale.setScalar(scale);
  root.add(real);
  root.updateWorldMatrix(true, true);

  const stageBounds = new THREE.Box3().setFromObject(root);

  const realOffset = real.position.clone();
  return {
    root,
    real,
    scale,
    stageBounds,
    realBounds,
    toStage: (meters: number) => meters * scale,
    toStagePoint: (v: THREE.Vector3) => v.clone().add(realOffset).multiplyScalar(scale),
  };
}
