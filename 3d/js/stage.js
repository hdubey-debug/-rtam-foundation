// The 3D stage: the temple and the Nandi mandapa with their night baked into the texture (shown unlit, so the colours
// are exactly the posters'), mirrored in a polished dark floor, and a camera that walks the pradakshina path.
import * as THREE from 'three';
import { GLTFLoader } from '../lib/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from '../lib/addons/loaders/DRACOLoader.js';

const GROUND = new THREE.Color(0x141414);
// Nandi's mandapa before the temple's door, facing it (placement from the approved viewer, in the temple's units)
const NANDI = { scale: 0.2014, x: 0.0176, z: 0.98, turn: Math.PI };

// The walk, clockwise (keeping the temple on the right). Each stop: the camera's azimuth around the temple's centre
// (degrees, measured from +x toward +z, increasing = clockwise from above), its horizontal distance and height, where it
// looks, and how much of the scene's width it frames.
export const STOPS = [
  { id: 'poster', az: 60.34, r: 1.4961, h: .0658, look: [.0184, .1272, .144], span: .8004 },   // the film's last frame, solved on its lamps (solve_view.py)
  { id: 'door', az: 90, r: .80, h: .125, look: [.006, .10, .33], span: .42, near: true },
  { id: 'jali', az: 158, r: 1.04, h: .19, look: [-.06, .15, .02], span: .92 },
  { id: 'tower', az: 232, r: 1.02, h: .34, look: [0, .31, -.2], span: .78 },
  { id: 'side', az: 318, r: 1.20, h: .23, look: [.06, .17, 0], span: 1.0 },
  { id: 'nandi', az: 447, r: 1.10, h: .06, look: [.006, .11, .334], span: .34, near: true },   // over Nandi's shoulder, at his eye
];
// the Nandi posters' entry: facing Nandi as the film does (calibrated on its last frame), then a crane up beside the
// mandapa's corner (clear of its roof and pillars) and down behind his shoulder, to see what he sees
export const NANDI_FRONT = { az: 93.14, r: .7098, h: .0501, look: [.0176, .0601, .98], span: .2462 };
export const NANDI_CRANE = [
  { az: 78, r: 1.32, h: .34, look: [.006, .10, .334], span: .70 },                         // looking at the door throughout
  { az: 87, r: 1.10, h: .06, look: [.006, .11, .334], span: .34 },
];
const ease = (t) => t * t * (3 - 2 * t);
const lerp = (a, b, t) => a + (b - a) * t;

export class Stage {
  constructor(canvas, { tier = 'lo', base = '', breathe = true } = {}) {
    this.canvas = canvas; this.tier = tier; this.base = base;
    // a living camera: at rest it breathes (a slow dolly and sway), so nothing is ever frozen; it rests after a minute
    this.breathe = breathe; this.awakeUntil = 0; this.lastBreath = 0; this.uNow = 0; this.onframe = null; this.now = 0;
    this.ext = document.documentElement.dataset.models || '.glb';
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: tier === 'hi', alpha: false, powerPreference: 'high-performance' });
    this.renderer.setClearColor(GROUND, 1);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.NoToneMapping;
    this.scene = new THREE.Scene(); this.scene.background = GROUND;
    this.camera = new THREE.PerspectiveCamera(30, 1, .01, 30);
    this.frame = { x: 0, y: 0, w: 1, h: 1 };              // the picture area, in CSS px
    this.view = this.pose(STOPS[0]);                       // the camera's current pose
    this.zoom = 1; this.dirty = true; this.anim = null; this.u = 0;
    this.groups = { temple: new THREE.Group(), nandi: new THREE.Group(), mirror: new THREE.Group() };
    this.groups.nandi.position.set(NANDI.x, 0, NANDI.z); this.groups.nandi.rotation.y = NANDI.turn; this.groups.nandi.scale.setScalar(NANDI.scale);
    this.groups.mirror.scale.y = -1;
    for (const g of Object.values(this.groups)) this.scene.add(g);
    const draco = new DRACOLoader().setDecoderPath(base + 'lib/draco/');
    let wasm = typeof WebAssembly === 'object';           // some hosts forbid compiling WebAssembly: use the JS decoder there
    try { new WebAssembly.Module(Uint8Array.of(0, 97, 115, 109, 1, 0, 0, 0)); } catch (e) { wasm = false; }
    draco.setDecoderConfig({ type: wasm ? 'wasm' : 'js' });
    this.loader = new GLTFLoader().setDRACOLoader(draco);
    if (this.ext !== '.glb') this.loader.register((parser) => {  // on the review host, textures go through <img>, not fetch(blob:)
      parser.textureLoader = new THREE.TextureLoader(parser.options.manager); return { name: 'rtam_img_textures' };
    });
    this.resize();
    this.loop = this.loop.bind(this); requestAnimationFrame(this.loop);
    if (/[?&]test\b/.test(location.search)) window.__stage = this;
    document.addEventListener('visibilitychange', () => { this.dirty = true; });
  }

  // ---------------------------------------------------------------- models
  material(src, mirror) {
    const map = src.map; if (map) { map.colorSpace = THREE.SRGBColorSpace; map.anisotropy = this.tier === 'hi' ? Math.min(8, this.renderer.capabilities.getMaxAnisotropy()) : 1; }
    const m = new THREE.MeshBasicMaterial({ map });
    if (mirror) {
      // the reflection: the same picture mirrored, fading into the ground with depth (as on the posters, about a third)
      m.onBeforeCompile = (sh) => {
        sh.uniforms.uGround = { value: new THREE.Vector3(20 / 255, 20 / 255, 20 / 255) }; sh.uniforms.uK = { value: .28 }; sh.uniforms.uLen = { value: .16 };
        sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying float vWY;')
          .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWY = (modelMatrix * vec4(transformed, 1.0)).y;');
        sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying float vWY;\nuniform vec3 uGround; uniform float uK; uniform float uLen;')
          .replace('#include <dithering_fragment>', '#include <dithering_fragment>\nfloat k = uK * pow(clamp(1.0 + vWY / uLen, 0.0, 1.0), 1.3);\ngl_FragColor.rgb = mix(uGround, gl_FragColor.rgb, k);');
      };
      m.customProgramCacheKey = () => 'mirror';
    }
    return m;
  }

  async loadModel(url, onProgress) {
    const gltf = url.endsWith('.txt') ? await this.loadText(url, onProgress)
                                      : await new Promise((res, rej) => this.loader.load(url, res, onProgress, rej));
    let mesh = null; gltf.scene.traverse((o) => { if (o.isMesh && !mesh) mesh = o; });
    mesh.updateWorldMatrix(true, false);
    const g = mesh.geometry.clone().applyMatrix4(mesh.matrixWorld);
    return { geometry: g, map: mesh.material.map };
  }

  // the same GLB carried as base64 text, for hosts that serve no .glb (the review package): fetch, decode, parse
  async loadText(url, onProgress) {
    const r = await fetch(url); if (!r.ok) throw new Error(url + ' ' + r.status);
    const total = +r.headers.get('content-length') || 0, reader = r.body.getReader(), parts = []; let loaded = 0;
    for (;;) {
      const { done, value } = await reader.read(); if (done) break;
      parts.push(value); loaded += value.length; onProgress && onProgress({ loaded, total: Math.max(total, loaded) });
    }
    const text = await new Blob(parts).text(), s = atob(text.trim()), bin = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i++) bin[i] = s.charCodeAt(i);
    return new Promise((res, rej) => this.loader.parse(bin.buffer, this.base + 'models/', res, rej));
  }

  place(name, model, { mirror = true } = {}) {
    const grp = this.groups[name];
    grp.clear(); grp.add(new THREE.Mesh(model.geometry, this.material(model, false)));
    if (mirror) {
      this.groups.mirror.children.filter((c) => c.userData.of === name).forEach((c) => this.groups.mirror.remove(c));
      const m = new THREE.Mesh(model.geometry, this.material(model, true)); m.userData.of = name;
      if (name === 'nandi') { m.position.copy(this.groups.nandi.position); m.rotation.copy(this.groups.nandi.rotation); m.scale.copy(this.groups.nandi.scale); }
      this.groups.mirror.add(m);
    }
    this.dirty = true;
  }

  async load(onProgress) {
    const prog = { temple: [0, 1], nandi: [0, 1] };
    const report = () => onProgress && onProgress((prog.temple[0] + prog.nandi[0]) / Math.max(1, prog.temple[1] + prog.nandi[1]));
    const p = (k) => (e) => { prog[k] = [e.loaded, e.total || e.loaded || 1]; report(); };
    const [t, n] = await Promise.all([this.loadModel(this.base + 'models/temple-lo' + this.ext, p('temple')),
                                      this.loadModel(this.base + 'models/nandi-lo' + this.ext, p('nandi'))]);
    this.place('temple', t); this.place('nandi', n);
    this.lo = { t, n };
    this.ready = true;
  }

  async upgrade() {                                       // the sharper models for capable phones; the reflection keeps the light ones
    try {
      const [t, n] = await Promise.all([this.loadModel(this.base + 'models/temple-hi' + this.ext), this.loadModel(this.base + 'models/nandi-hi' + this.ext)]);
      this.place('temple', t, { mirror: false }); this.place('nandi', n, { mirror: false });
    } catch (e) { /* the light models stay */ }
  }

  // ---------------------------------------------------------------- camera
  pose(s) { return { az: s.az, r: s.r, h: s.h, look: s.look.slice(), span: s.span }; }
  mix(a, b, t) {
    return { az: lerp(a.az, b.az, t), r: lerp(a.r, b.r, t), h: lerp(a.h, b.h, t),
             look: a.look.map((v, i) => lerp(v, b.look[i], t)), span: lerp(a.span, b.span, t) };
  }
  // the path between stops: walking around the temple at a distance, never through it
  at(u) {
    const n = STOPS.length - 1; const i = Math.max(0, Math.min(n - 1, Math.floor(u))); const t = Math.max(0, Math.min(1, u - i));
    return this.mix(this.pose(STOPS[i]), this.pose(STOPS[i + 1]), ease(t));
  }
  // walk along the path to stop u1 (never cutting across the temple)
  goU(u1, dur = 1600, done) {
    const u0 = this.anim && this.anim.kind === 'u' ? this.uNow : this.u; u1 = Math.max(0, Math.min(STOPS.length - 1, u1));
    this.anim = { kind: 'u', u0, u1, t0: performance.now(), dur: dur * Math.max(.6, Math.min(2.4, Math.abs(u1 - u0))), done };
    this.u = u1; this.dirty = true;
  }
  // move through a list of poses (off the path: the finale)
  goPoses(poses, dur = 2400, done) {
    const from = { ...this.view, look: this.view.look.slice() };
    this.anim = { kind: 'poses', list: [from, ...poses], t0: performance.now(), dur, done }; this.dirty = true;
  }
  scrub(u) { this.anim = null; this.u = this.uNow = Math.max(0, Math.min(STOPS.length - 1, u)); this.view = this.at(this.u); this.dirty = true; this.wake(); }
  wake() { this.awakeUntil = performance.now() + 60000; }

  apply() {
    const v = this.view, cam = this.camera;
    let az = v.az, r = v.r * this.zoom;
    if (this.breathing) {                                   // ±0.4% dolly, ±0.15° sway, a 7 s breath
      const w = this.now / 7000 * Math.PI * 2; r *= 1 + .004 * Math.sin(w); az += .15 * Math.sin(w * .5 + 1.3);
    }
    const a = THREE.MathUtils.degToRad(az);
    cam.position.set(Math.cos(a) * r, v.h + (this.zoom - 1) * .05, Math.sin(a) * r);
    cam.lookAt(v.look[0], v.look[1], v.look[2]);
    // frame: the stop's span fills the picture area's width (or its height, if the area is narrow and tall)
    const W = this.size.w, H = this.size.h, f = this.frame;
    const aspect = f.w / f.h;
    const dist = cam.position.distanceTo(new THREE.Vector3(...v.look));
    const hfov = 2 * Math.atan((v.span * .5) / dist);
    let vfov = 2 * Math.atan(Math.tan(hfov / 2) / aspect);
    vfov = Math.min(vfov, THREE.MathUtils.degToRad(72));
    // the full canvas uses the same focal length; its centre is moved onto the picture area's centre
    cam.fov = THREE.MathUtils.radToDeg(2 * Math.atan(Math.tan(vfov / 2) * (H / f.h)));
    cam.aspect = W / H; cam.updateProjectionMatrix();
    const sx = ((f.x + f.w / 2) - W / 2) / (W / 2), sy = -((f.y + f.h / 2) - H / 2) / (H / 2);
    cam.projectionMatrix.elements[8] = -sx; cam.projectionMatrix.elements[9] = -sy;
    cam.projectionMatrixInverse.copy(cam.projectionMatrix).invert();
  }

  setFrame(rect) { this.frame = rect; this.dirty = true; }
  resize() {
    const w = this.canvas.clientWidth || innerWidth, h = this.canvas.clientHeight || innerHeight;
    const dpr = Math.min(devicePixelRatio || 1, this.tier === 'hi' ? 2 : 1.25);
    this.renderer.setPixelRatio(dpr); this.renderer.setSize(w, h, false);
    this.size = { w, h }; this.dirty = true;
  }
  // where a world point lands on screen (CSS px)
  project(p) {
    this.apply(); const v = p.clone().project(this.camera);
    return { x: (v.x + 1) / 2 * this.size.w, y: (1 - v.y) / 2 * this.size.h };
  }

  loop(now) {
    requestAnimationFrame(this.loop);
    if (document.hidden) return;
    this.now = now;
    if (this.anim) {
      const A = this.anim, t = Math.min(1, (now - A.t0) / A.dur);
      if (A.kind === 'u') { this.uNow = lerp(A.u0, A.u1, ease(t)); this.view = this.at(this.uNow); }
      else {
        const n = A.list.length - 1, x = ease(t) * n, i = Math.min(n - 1, Math.floor(x));
        this.view = this.mix(A.list[i], A.list[i + 1], ease(Math.min(1, x - i)));
      }
      this.dirty = true;
      if (t >= 1) { this.anim = null; this.wake(); A.done && A.done(); }
    }
    // the breath: only at rest, while the page is looked at; drawn at about 25 frames a second
    this.breathing = this.breathe && !this.anim && now < this.awakeUntil;
    if (this.breathing && now - this.lastBreath > 40) { this.dirty = true; this.lastBreath = now; }
    if (!this.dirty || !this.ready) return;
    this.apply(); this.renderer.render(this.scene, this.camera); this.dirty = false;
    this.onframe && this.onframe(this.uNow);
  }
}
