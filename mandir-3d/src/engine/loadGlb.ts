/** GLB loading. parseGlb serves the M3 round-trip proof (export clone →
 * reimport → same bounds); loadGlbUrl serves Track A at M11 (Draco
 * decoder wired then, BASE_URL-safe).
 */
import * as THREE from "three/webgpu";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

export async function parseGlb(buf: ArrayBuffer): Promise<THREE.Group> {
  const loader = new GLTFLoader();
  const gltf = await loader.parseAsync(buf, "");
  const scene = gltf.scene as THREE.Group;
  scene.traverse((obj) => {
    const mesh = obj as THREE.Mesh;
    if (mesh.isMesh) {
      mesh.castShadow = true;
      mesh.receiveShadow = true;
    }
  });
  return scene;
}
