/** Dark-stage lighting: hemisphere base + one warm key (the sole shadow
 * caster, 2048 fitted ortho, on-demand updates) + cool fill + rim.
 * Shadow map autoUpdate is OFF — the engine bumps needsUpdate via its
 * dirty counter whenever the scene actually changes.
 */
import * as THREE from "three/webgpu";

export interface Lighting {
  group: THREE.Group;
  key: THREE.DirectionalLight;
  /** fit the key's ortho frustum + bias to the current item */
  fitTo(stageBounds: THREE.Box3, toStage: (m: number) => number): void;
  dispose(): void;
}

function fromSpherical(azimuthDeg: number, elevationDeg: number, dist: number): THREE.Vector3 {
  const az = (azimuthDeg * Math.PI) / 180;
  const el = (elevationDeg * Math.PI) / 180;
  return new THREE.Vector3(
    Math.sin(az) * Math.cos(el) * dist,
    Math.sin(el) * dist,
    Math.cos(az) * Math.cos(el) * dist,
  );
}

export function buildLighting(scene: THREE.Scene): Lighting {
  const group = new THREE.Group();
  group.name = "lighting";

  const hemi = new THREE.HemisphereLight(0x4c4e56, 0x2f2820, 0.7);

  const key = new THREE.DirectionalLight(0xffdfae, 2.6);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.near = 0.1;
  key.shadow.camera.far = 20;

  const fill = new THREE.DirectionalLight(0x9fb2c8, 0.6);
  const rim = new THREE.DirectionalLight(0xfff2dc, 0.7);

  group.add(hemi, key, key.target, fill, rim);
  scene.add(group);

  return {
    group,
    key,
    fitTo(stageBounds, toStage) {
      const sphere = stageBounds.getBoundingSphere(new THREE.Sphere());
      const c = sphere.center;
      const r = Math.max(sphere.radius, 0.001);

      key.position.copy(fromSpherical(-42, 41, r * 3)).add(c);
      key.target.position.copy(c);
      fill.position.copy(fromSpherical(74, 22, r * 3)).add(c);
      rim.position.copy(fromSpherical(158, 32, r * 3)).add(c);

      const cam = key.shadow.camera;
      const half = r * 1.15;
      cam.left = -half;
      cam.right = half;
      cam.top = half;
      cam.bottom = -half;
      cam.near = r * 1.2;
      cam.far = r * 5;
      cam.updateProjectionMatrix();

      // bias in physical units: ~18mm normal offset at item scale
      key.shadow.normalBias = toStage(0.018);
      key.shadow.bias = -0.00015;
    },
    dispose() {
      scene.remove(group);
    },
  };
}
