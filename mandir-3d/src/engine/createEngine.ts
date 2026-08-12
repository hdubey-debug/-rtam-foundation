/** The stage engine. Renderer is three r185's WebGPURenderer class with
 * forceWebGL — a deliberate WebGL2-always choice for stability; the class
 * is used because TSL node materials need it. Rendering is on-demand
 * (dirty flag), the shadow map updates only when the shadow generation is
 * bumped, and the whole engine is StrictMode-safe: boot is cancellable and
 * dispose is idempotent.
 */
import * as THREE from "three/webgpu";
import { buildLighting, type Lighting } from "./lighting";
import { buildGround, type Ground } from "./ground";
import { createLayers, type Layers, type LayerState } from "./layers";
import { createCameraRig, type CameraRig } from "./cameraRig";
import { normalizeModel, type NormalizedItem } from "./normalize";
import { warmup } from "./warmup";
import { attachResize } from "./resize";
import { exportGlb } from "./exportGlb";
import { VIEWS, DEFAULT_VIEW } from "../qa/views";

export interface StageModel {
  /** real-meters model root */
  group: THREE.Group;
  /** named anchor points in real meters (hotspots snap "exact" to these) */
  anchors?: Record<string, THREE.Vector3>;
}

export interface EngineOpts {
  container: HTMLElement;
  canvas: HTMLCanvasElement;
  /** false in shot mode: controls off, no damping, instant views */
  interactive: boolean;
  /** force a fixed device pixel ratio (shot mode uses 1) */
  forceDpr?: number;
  onContextLost?: () => void;
}

export interface EngineStats {
  drawCalls: number;
  triangles: number;
  frame: number;
  shadowGen: number;
}

export interface Engine {
  renderer: THREE.WebGPURenderer;
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  rendererString: string;
  setModel(model: StageModel): NormalizedItem;
  currentItem(): NormalizedItem | null;
  applyView(name: string, instant: boolean): void;
  setLayers(partial: Partial<LayerState>): void;
  layerState(): LayerState;
  overlayCount(): number;
  requestRender(): void;
  markShadowsDirty(): void;
  /** compile + off-screen warm render + shadow scrub, then n settled frames */
  warmupAndSettle(frames?: number): Promise<void>;
  exportCurrentGlb(): Promise<ArrayBuffer>;
  stats(): EngineStats;
  dispose(): void;
}

/** ONE renderer per canvas, for the page's life. r185's WebGLBackend
 * .dispose() force-loses the canvas context (WEBGL_lose_context.
 * loseContext()) and never restores it — so a StrictMode remount on the
 * same canvas would inherit a dead context. Engine dispose therefore
 * tears down everything EXCEPT the renderer; remounts re-acquire it here.
 */
const rendererCache = new WeakMap<HTMLCanvasElement, Promise<THREE.WebGPURenderer>>();

function acquireRenderer(canvas: HTMLCanvasElement): Promise<THREE.WebGPURenderer> {
  let p = rendererCache.get(canvas);
  if (!p) {
    p = (async () => {
      const renderer = new THREE.WebGPURenderer({
        canvas,
        antialias: true,
        alpha: true,
        forceWebGL: true,
      });
      await renderer.init();
      return renderer;
    })();
    rendererCache.set(canvas, p);
  }
  return p;
}

function readRendererString(renderer: THREE.WebGPURenderer): string {
  try {
    const backend = (renderer as unknown as { backend?: { gl?: WebGL2RenderingContext; isWebGPUBackend?: boolean } }).backend;
    const gl = backend?.gl;
    if (gl) {
      const ext = gl.getExtension("WEBGL_debug_renderer_info");
      if (ext) return String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL));
      return String(gl.getParameter(gl.RENDERER));
    }
    return backend?.isWebGPUBackend ? "WebGPU" : "unknown";
  } catch {
    return "unknown";
  }
}

export async function createEngine(opts: EngineOpts): Promise<Engine> {
  const { container, canvas, interactive } = opts;

  const renderer = await acquireRenderer(canvas);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  // r185's WebGPURenderer shadowMap type has no autoUpdate/needsUpdate —
  // set them anyway (ignored if unsupported → shadows just render per
  // frame, which is correct, only less lazy). The M0 spike shot verifies
  // shadows actually appear.
  const shadowCtl = renderer.shadowMap as unknown as {
    autoUpdate?: boolean;
    needsUpdate?: boolean;
  };
  shadowCtl.autoUpdate = false;
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  scene.background = null;

  let needsRender = true;
  let shadowsDirty = true;
  let shadowGen = 0;
  let frame = 0;
  let drawCalls = 0;
  let triangles = 0;
  let disposed = false;

  const requestRender = () => {
    needsRender = true;
  };

  const rig: CameraRig = createCameraRig(canvas, requestRender, interactive);
  const lighting: Lighting = buildLighting(scene);
  const ground: Ground = buildGround(scene);
  const layers: Layers = createLayers(requestRender);
  const detachResize = attachResize(container, renderer, rig.camera, requestRender, opts.forceDpr);

  const onLost = (e: Event) => {
    e.preventDefault();
    opts.onContextLost?.();
  };
  canvas.addEventListener("webglcontextlost", onLost);

  let item: NormalizedItem | null = null;
  let anchors: Record<string, THREE.Vector3> = {};

  let rafId = 0;
  const loop = () => {
    rafId = requestAnimationFrame(loop);
    if (interactive) rig.controls.update();
    if (!needsRender) return;
    needsRender = false;
    if (shadowsDirty) {
      shadowCtl.needsUpdate = true;
      shadowsDirty = false;
      shadowGen++;
    }
    renderer.render(scene, rig.camera);
    frame++;
    const info = renderer.info as unknown as {
      render?: { drawCalls?: number; calls?: number; triangles?: number };
    };
    drawCalls = info.render?.drawCalls ?? info.render?.calls ?? 0;
    triangles = info.render?.triangles ?? 0;
  };
  rafId = requestAnimationFrame(loop);

  const disposeItem = () => {
    if (!item) return;
    scene.remove(item.root);
    item.root.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (mesh.isMesh) {
        mesh.geometry.dispose();
        const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
        mats.forEach((m) => m.dispose());
      }
    });
    item = null;
  };

  const settleFrames = (n: number) =>
    new Promise<void>((resolve) => {
      let left = n;
      const step = () => {
        requestRender();
        if (--left <= 0) {
          resolve();
          return;
        }
        requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });

  return {
    renderer,
    scene,
    camera: rig.camera,
    rendererString: readRendererString(renderer),
    setModel(model) {
      layers.attach(null); // restore old materials before disposal
      disposeItem();
      const normalized = normalizeModel(model.group);
      item = normalized;
      anchors = model.anchors ?? {};
      scene.add(normalized.root);
      lighting.fitTo(normalized.stageBounds, normalized.toStage);
      layers.attach(normalized.root); // active layers survive the swap
      shadowsDirty = true;
      requestRender();
      return normalized;
    },
    currentItem: () => item,
    applyView(name, instant) {
      const def = VIEWS[name] ?? VIEWS[DEFAULT_VIEW];
      if (def.anchor && def.distM && item && anchors[def.anchor]) {
        rig.applyAnchorView(def, item.toStagePoint(anchors[def.anchor]), item.toStage(def.distM), instant);
        return;
      }
      const bounds =
        item?.stageBounds ??
        new THREE.Box3(new THREE.Vector3(-1, 0, -1), new THREE.Vector3(1, 1.5, 1));
      rig.applyView(def, bounds, instant);
    },
    setLayers(partial) {
      layers.set(partial);
      shadowsDirty = true;
      requestRender();
    },
    layerState: () => ({ ...layers.state }),
    overlayCount: () => layers.overlayCount(),
    requestRender,
    markShadowsDirty() {
      shadowsDirty = true;
      requestRender();
    },
    async warmupAndSettle(frames = 2) {
      await warmup(renderer, scene, rig.camera);
      shadowsDirty = true;
      requestRender();
      await settleFrames(frames);
    },
    exportCurrentGlb() {
      if (!item) return Promise.reject(new Error("no model on stage"));
      return exportGlb(item.real);
    },
    stats: () => ({ drawCalls, triangles, frame, shadowGen }),
    dispose() {
      if (disposed) return;
      disposed = true;
      cancelAnimationFrame(rafId);
      canvas.removeEventListener("webglcontextlost", onLost);
      detachResize();
      rig.dispose();
      lighting.dispose();
      ground.dispose();
      layers.dispose();
      disposeItem();
      // deliberately NOT renderer.dispose() — see rendererCache note above
      renderer.setRenderTarget(null);
    },
  };
}
