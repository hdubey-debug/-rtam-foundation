/** Camera rig: spherical view state + OrbitControls + GSAP flights.
 * The single source of truth after user input is the CONTROLS — state is
 * synced FROM the controls' change event (the reference app read it the
 * other way and drifted).
 */
import * as THREE from "three/webgpu";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import gsap from "gsap";
import type { ViewDef } from "../qa/views";

export interface CameraRig {
  camera: THREE.PerspectiveCamera;
  controls: OrbitControls;
  applyView(def: ViewDef, stageBounds: THREE.Box3, instant: boolean): void;
  /** closeup: orbit an explicit stage-space point at a stage distance */
  applyAnchorView(def: ViewDef, point: THREE.Vector3, stageDist: number, instant: boolean): void;
  dispose(): void;
}

export function createCameraRig(
  canvas: HTMLCanvasElement,
  requestRender: () => void,
  interactive: boolean,
): CameraRig {
  const camera = new THREE.PerspectiveCamera(34, 1, 0.02, 60);
  camera.position.set(0, 1.2, 4.2);

  const controls = new OrbitControls(camera, canvas);
  controls.enabled = interactive;
  controls.enableDamping = interactive;
  controls.dampingFactor = 0.08;
  controls.minDistance = 0.6;
  controls.maxDistance = 14;
  controls.maxPolarAngle = (88 * Math.PI) / 180;
  controls.addEventListener("change", requestRender);

  let flight: gsap.core.Tween | null = null;

  function fitDistance(def: ViewDef, bounds: THREE.Box3): { target: THREE.Vector3; pos: THREE.Vector3 } {
    const sphere = bounds.getBoundingSphere(new THREE.Sphere());
    const r = Math.max(sphere.radius, 0.001);
    const vFov = (camera.fov * Math.PI) / 180;
    const hFov = 2 * Math.atan(Math.tan(vFov / 2) * camera.aspect);
    const fov = Math.min(vFov, hFov);
    const dist = (def.fit * r) / Math.sin(fov / 2);

    const az = (def.azimuthDeg * Math.PI) / 180;
    const el = (def.elevationDeg * Math.PI) / 180;
    const pos = new THREE.Vector3(
      Math.sin(az) * Math.cos(el) * dist,
      Math.sin(el) * dist,
      Math.cos(az) * Math.cos(el) * dist,
    ).add(sphere.center);
    return { target: sphere.center.clone(), pos };
  }

  const flyTo = (target: THREE.Vector3, pos: THREE.Vector3, instant: boolean) => {
    flight?.kill();
    if (instant) {
      camera.position.copy(pos);
      controls.target.copy(target);
      controls.update();
      requestRender();
      return;
    }
    const state = {
      px: camera.position.x, py: camera.position.y, pz: camera.position.z,
      tx: controls.target.x, ty: controls.target.y, tz: controls.target.z,
    };
    flight = gsap.to(state, {
      px: pos.x, py: pos.y, pz: pos.z,
      tx: target.x, ty: target.y, tz: target.z,
      duration: 1.1,
      ease: "power3.inOut",
      onUpdate: () => {
        camera.position.set(state.px, state.py, state.pz);
        controls.target.set(state.tx, state.ty, state.tz);
        controls.update();
        requestRender();
      },
    });
  };

  const sphericalPos = (def: ViewDef, center: THREE.Vector3, dist: number): THREE.Vector3 => {
    const az = (def.azimuthDeg * Math.PI) / 180;
    const el = (def.elevationDeg * Math.PI) / 180;
    return new THREE.Vector3(
      Math.sin(az) * Math.cos(el) * dist,
      Math.sin(el) * dist,
      Math.cos(az) * Math.cos(el) * dist,
    ).add(center);
  };

  return {
    camera,
    controls,
    applyAnchorView(def, point, stageDist, instant) {
      flyTo(point.clone(), sphericalPos(def, point, stageDist), instant);
    },
    applyView(def, stageBounds, instant) {
      const { target, pos } = fitDistance(def, stageBounds);
      flyTo(target, pos, instant);
    },
    dispose() {
      flight?.kill();
      controls.removeEventListener("change", requestRender);
      controls.dispose();
    },
  };
}
