/** View layers.
 *
 * Wireframe = INSTANCED overlay meshes that SHARE the source's geometry
 * and instanceMatrix buffer (the reference app rebuilt only mesh[0] and
 * lost instanced parts — sharing the attribute makes drift impossible).
 * X-ray = a declarative material-state set with saved/restored state.
 * Both REAPPLY after every model attach — layer state survives swaps.
 */
import * as THREE from "three/webgpu";

export interface LayerState {
  wireframe: boolean;
  xray: boolean;
}

interface SavedMat {
  transparent: boolean;
  opacity: number;
  depthWrite: boolean;
}

export interface Layers {
  state: LayerState;
  /** call whenever a new model root is attached */
  attach(root: THREE.Object3D | null): void;
  set(partial: Partial<LayerState>): void;
  overlayCount(): number;
  dispose(): void;
}

export function createLayers(requestRender: () => void): Layers {
  const state: LayerState = { wireframe: false, xray: false };
  let root: THREE.Object3D | null = null;
  const overlays: THREE.Object3D[] = [];
  const saved = new Map<THREE.Material, SavedMat>();

  const wireMat = new THREE.MeshBasicNodeMaterial({
    wireframe: true,
    transparent: true,
    opacity: 0.3,
    depthWrite: false,
  });
  wireMat.color.set(0xc8a15a);
  wireMat.name = "wire-overlay";

  const clearOverlays = () => {
    for (const o of overlays) o.parent?.remove(o);
    overlays.length = 0;
  };

  const buildOverlays = () => {
    if (!root) return;
    const sources: (THREE.Mesh | THREE.InstancedMesh)[] = [];
    root.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (mesh.isMesh && mesh.material !== wireMat) sources.push(mesh);
    });
    for (const src of sources) {
      let overlay: THREE.Object3D;
      if ((src as THREE.InstancedMesh).isInstancedMesh) {
        const inst = src as THREE.InstancedMesh;
        const o = new THREE.InstancedMesh(inst.geometry, wireMat, inst.count);
        o.instanceMatrix = inst.instanceMatrix; // SHARED buffer — never drifts
        o.boundingBox = inst.boundingBox;
        o.boundingSphere = inst.boundingSphere;
        overlay = o;
      } else {
        overlay = new THREE.Mesh(src.geometry, wireMat);
      }
      overlay.name = `${src.name}-wire`;
      overlay.renderOrder = 10;
      overlay.castShadow = false;
      overlay.receiveShadow = false;
      src.add(overlay); // inherits the source transform exactly
      overlays.push(overlay);
    }
  };

  const applyXray = (on: boolean) => {
    if (!root) return;
    root.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (!mesh.isMesh) return;
      const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const m of mats) {
        if (m === wireMat) continue;
        if (on) {
          if (!saved.has(m)) {
            saved.set(m, { transparent: m.transparent, opacity: m.opacity, depthWrite: m.depthWrite });
          }
          m.transparent = true;
          m.opacity = 0.28;
          m.depthWrite = false;
          m.needsUpdate = true;
        } else {
          const s = saved.get(m);
          if (s) {
            m.transparent = s.transparent;
            m.opacity = s.opacity;
            m.depthWrite = s.depthWrite;
            m.needsUpdate = true;
          }
        }
      }
    });
    if (!on) saved.clear();
  };

  const reapply = () => {
    clearOverlays();
    if (state.wireframe) buildOverlays();
    applyXray(state.xray);
    requestRender();
  };

  return {
    state,
    attach(newRoot) {
      // restore any mutated materials on the OLD root before letting go
      applyXray(false);
      clearOverlays();
      root = newRoot;
      reapply();
    },
    set(partial) {
      if (partial.wireframe !== undefined) state.wireframe = partial.wireframe;
      if (partial.xray !== undefined) {
        state.xray = partial.xray;
        applyXray(partial.xray);
      }
      clearOverlays();
      if (state.wireframe) buildOverlays();
      requestRender();
    },
    overlayCount: () => overlays.length,
    dispose() {
      applyXray(false);
      clearOverlays();
      wireMat.dispose();
    },
  };
}
