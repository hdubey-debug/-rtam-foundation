/** Warm-up: compile all pipelines off-screen, then render once into a tiny
 * render target (16×16) with a forced shadow pass — so the first visible
 * frame carries no compilation hitch and shadows are already resolved.
 */
import * as THREE from "three/webgpu";

export async function warmup(
  renderer: THREE.WebGPURenderer,
  scene: THREE.Scene,
  camera: THREE.Camera,
): Promise<void> {
  await renderer.compileAsync(scene, camera);

  const rt = new THREE.RenderTarget(16, 16);
  const prev = renderer.getRenderTarget();
  renderer.setRenderTarget(rt);
  // needsUpdate is absent from this renderer's shadowMap typing — set it
  // opportunistically (see createEngine's shadow note).
  (renderer.shadowMap as unknown as { needsUpdate?: boolean }).needsUpdate = true;
  await renderer.renderAsync(scene, camera);
  renderer.setRenderTarget(prev);
  rt.dispose();
}
