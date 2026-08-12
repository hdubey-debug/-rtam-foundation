/** Resize handling with a pixel budget: dpr ≤ 2, and never more than
 * ~3.5M physical pixels (large 4K windows drop dpr instead of frying the
 * GPU). Shot mode forces dpr 1 for reproducible captures.
 */
import type * as THREE from "three/webgpu";

export function attachResize(
  container: HTMLElement,
  renderer: THREE.WebGPURenderer,
  camera: THREE.PerspectiveCamera,
  requestRender: () => void,
  forceDpr?: number,
): () => void {
  const apply = () => {
    const w = Math.max(1, container.clientWidth);
    const h = Math.max(1, container.clientHeight);
    let dpr = forceDpr ?? Math.min(window.devicePixelRatio || 1, 2);
    if (w * h * dpr * dpr > 3.5e6) dpr = Math.sqrt(3.5e6 / (w * h));
    renderer.setPixelRatio(dpr);
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    requestRender();
  };
  const ro = new ResizeObserver(apply);
  ro.observe(container);
  apply();
  return () => ro.disconnect();
}
