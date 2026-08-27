import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

declare global {
  interface Window {
    __turntable?: {
      ready: boolean;
      error?: string;
      meta?: Record<string, unknown>;
      renderFrame?: (frame: number, total: number) => void;
    };
  }
}

const canvas = document.querySelector<HTMLCanvasElement>("#stage")!;
const fade = document.querySelector<HTMLDivElement>("#fade")!;
const renderer = new THREE.WebGLRenderer({
  canvas,
  alpha: true,
  antialias: true,
  preserveDrawingBuffer: true,
  powerPreference: "high-performance",
});

renderer.setPixelRatio(1);
renderer.setSize(window.innerWidth, window.innerHeight, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(33, window.innerWidth / window.innerHeight, 0.001, 100);

const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
pmrem.dispose();

scene.add(new THREE.HemisphereLight(0xffefd5, 0x3d4650, 2.25));

const key = new THREE.DirectionalLight(0xffe3bc, 3.5);
key.position.set(4, 6, 5);
scene.add(key);

const fill = new THREE.DirectionalLight(0xbfd5ff, 2.1);
fill.position.set(-5, 2.5, 2);
scene.add(fill);

const rim = new THREE.DirectionalLight(0xffc777, 2.4);
rim.position.set(1, -4, -5);
scene.add(rim);

window.__turntable = { ready: false };

const smoothstep = (x: number) => x * x * (3 - 2 * x);
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const radians = (degrees: number) => (degrees * Math.PI) / 180;

function segment(t: number, start: number, end: number): number {
  return smoothstep(Math.min(1, Math.max(0, (t - start) / (end - start))));
}

function cameraPose(t: number): { azimuth: number; elevation: number } {
  // 10-second level orbit, followed by overhead and underside reveals.
  if (t < 2 / 3) {
    const p = t / (2 / 3);
    return { azimuth: lerp(22, 382, p), elevation: 20 };
  }
  if (t < 0.77) {
    const p = segment(t, 2 / 3, 0.77);
    return { azimuth: lerp(382, 430, p), elevation: lerp(20, 78, p) };
  }
  if (t < 0.84) {
    const p = (t - 0.77) / 0.07;
    return { azimuth: lerp(430, 470, p), elevation: 78 };
  }
  if (t < 0.94) {
    const p = segment(t, 0.84, 0.94);
    return { azimuth: lerp(470, 525, p), elevation: lerp(78, -55, p) };
  }
  const p = (t - 0.94) / 0.06;
  return { azimuth: lerp(525, 555, p), elevation: -55 };
}

async function boot() {
  try {
    const params = new URLSearchParams(window.location.search);
    const modelUrl = params.get("model") ?? "/indian%20temple%203d%20model.glb";
    const fit = Number(params.get("fit") ?? "1.18");
    const gltf = await new GLTFLoader().loadAsync(modelUrl);
    const model = gltf.scene;

    model.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (!mesh.isMesh) return;
      mesh.frustumCulled = false;
      const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const material of materials) {
        const standard = material as THREE.MeshStandardMaterial;
        if (standard.map) standard.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
        standard.needsUpdate = true;
      }
    });

    const originalBounds = new THREE.Box3().setFromObject(model);
    const center = originalBounds.getCenter(new THREE.Vector3());
    model.position.sub(center);
    scene.add(model);

    const bounds = new THREE.Box3().setFromObject(model);
    const sphere = bounds.getBoundingSphere(new THREE.Sphere());
    const verticalFov = radians(camera.fov);
    const horizontalFov = 2 * Math.atan(Math.tan(verticalFov / 2) * camera.aspect);
    const limitingFov = Math.min(verticalFov, horizontalFov);
    const distance = (sphere.radius * fit) / Math.sin(limitingFov / 2);
    camera.near = Math.max(0.001, distance - sphere.radius * 1.8);
    camera.far = distance + sphere.radius * 2.5;
    camera.updateProjectionMatrix();

    const renderFrame = (frame: number, total: number) => {
      const t = total <= 1 ? 0 : frame / (total - 1);
      const pose = cameraPose(t);
      const azimuth = radians(pose.azimuth);
      const elevation = radians(pose.elevation);
      camera.position.set(
        Math.sin(azimuth) * Math.cos(elevation) * distance,
        Math.sin(elevation) * distance,
        Math.cos(azimuth) * Math.cos(elevation) * distance,
      );
      camera.lookAt(0, 0, 0);

      // A gentle fade gives the generated clip a clean ending.
      fade.style.opacity = t > 0.985 ? String(smoothstep((t - 0.985) / 0.015)) : "0";
      renderer.render(scene, camera);
    };

    renderFrame(0, 360);
    window.__turntable = {
      ready: true,
      renderFrame,
      meta: {
        boundsMin: bounds.min.toArray(),
        boundsMax: bounds.max.toArray(),
        radius: sphere.radius,
        distance,
        renderer: renderer.info.render,
      },
    };
  } catch (error) {
    const message = error instanceof Error ? error.stack ?? error.message : String(error);
    window.__turntable = { ready: false, error: message };
    throw error;
  }
}

void boot();
