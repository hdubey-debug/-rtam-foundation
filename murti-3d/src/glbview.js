/** Minimal GLB reference viewer for headless study shots (?view=front|quarter|top). */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setClearColor(0xf7f3e9, 1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.style.margin = "0";
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xfffdf4, 0xcfc7b4, 1.2));
const d1 = new THREE.DirectionalLight(0xfff6e6, 0.8); d1.position.set(2, 3, 1.5); scene.add(d1);
const d2 = new THREE.DirectionalLight(0xf0ead9, 0.3); d2.position.set(-2.5, 1.5, -2); scene.add(d2);
const camera = new THREE.PerspectiveCamera(30, innerWidth / innerHeight, 0.01, 100);

console.log("fetching model...");
new GLTFLoader().load("/model.glb", (g) => {
  console.log("gltf parsed");
  const obj = g.scene;
  scene.add(obj);
  const box = new THREE.Box3().setFromObject(obj);
  const c = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const R = Math.max(size.x, size.z) / 2, H = size.y;
  c.y -= H * 0.04;
  const fit = Math.max(H, 2 * R) * 2.45;
  const view = new URLSearchParams(location.search).get("view") || "quarter";
  const V = {
    front: { az: 0, el: 8 }, quarter: { az: -35, el: 18 }, top: { az: 0, el: 88 },
  }[view] || { az: -35, el: 18 };
  const phi = ((90 - V.el) * Math.PI) / 180, th = (V.az * Math.PI) / 180;
  camera.position.set(c.x + fit * Math.sin(phi) * Math.sin(th), c.y + fit * Math.cos(phi), c.z + fit * Math.sin(phi) * Math.cos(th));
  camera.lookAt(c);
  let n = 0;
  const tick = () => { renderer.render(scene, camera); if (++n < 4) requestAnimationFrame(tick); else { console.log("rendered"); window.__glbShot = { done: true }; } };
  requestAnimationFrame(tick);
}, (xhr) => console.log("progress", xhr.loaded), (err) => console.error("GLTF ERROR:", String(err && (err.message || err)).slice(0, 300)));
