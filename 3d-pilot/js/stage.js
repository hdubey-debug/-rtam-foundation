// The 3D stage: the temple and the Nandi mandapa with their night baked into the texture (shown unlit, so the colours
// are exactly the posters'), mirrored in a polished dark floor, and a camera that walks round whichever is chosen: the
// temple, Nandi's mandapa, or the whole complex, a full circle each way.
import * as THREE from 'three';
import { GLTFLoader } from '../lib/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from '../lib/addons/loaders/DRACOLoader.js';

const GROUND = new THREE.Color(0x141414);
// Nandi's mandapa before the temple's door, facing it (placement from the approved viewer, in the temple's units)
const NANDI = { scale: 0.2014, x: 0.0176, z: 0.98, turn: Math.PI };

// What one can walk round. Each: the orbit's centre (x, z), the camera's distance and height, the height it looks at,
// what is shown, the footprint whose width the picture keeps framed as it turns (and the least it frames, so the tower
// or the roof is never cut), and where it starts. Azimuths in degrees from +x toward +z (increasing = clockwise from
// above, the temple on one's right: pradakshina). `front` is the side the building faces (the dial's top).
// At its `anchor` the view is exactly the film's last frame: the temple's solved on its lamps (solve_view.py), the
// mandapa's calibrated on its silhouette; turning away, the view eases onto the orbit's centre.
export const MODES = {
  temple: { c: [0, 0], r: 1.4961, h: .0658, ly: .1272, show: { temple: true, nandi: false }, front: 90, home: 60.34,
            box: [.488, 1.078], least: .78, anchor: { az: 60.34, look: [.0184, .1272, .144], span: .8004 } },
  nandi: { c: [NANDI.x, NANDI.z], r: .43, h: .085, ly: .062, show: { temple: false, nandi: true }, front: 258.24, home: 258.24,
           box: [.19, .19], least: .23, k: 1.2, anchor: { az: 258.24, r: .2771, h: .0501, look: [NANDI.x, .0601, NANDI.z], span: .2462 } },
  complex: { c: [0, .30], r: 2.6, h: .64, ly: .09, show: { temple: true, nandi: true }, front: 90, home: 52,
             box: [.50, 1.57], least: .85, k: 1.12 },
};
const wrap = (a) => ((a % 360) + 360) % 360;
const near = (a, ref) => ref + ((((a - ref) % 360) + 540) % 360) - 180;      // a, as the equivalent angle nearest ref
// the width of a footprint (dx, dz) seen from azimuth az, across the line of sight
const across = (box, az) => { const a = az * Math.PI / 180; return Math.abs(Math.sin(a)) * box[0] + Math.abs(Math.cos(a)) * box[1]; };
// settle (0..1) blends the film's framing into the walk's: one size at every angle (walkSpan, fitted to the subject's
// widest view on this screen) and the orbit's own centre, so turning never zooms. 0 is the framing the live pages use.
export function orbitView(name, az, settle = 0, walkSpan = null) {
  const M = MODES[name], A = M.anchor;
  const k = M.k || A.span / across(M.box, A.az);
  let span = Math.max(M.least, k * across(M.box, az)), look = [M.c[0], M.ly, M.c[1]], r = M.r, h = M.h;
  if (A) {                                            // near the anchor, ease onto the film's own framing
    const w = Math.pow(Math.max(0, Math.cos((az - A.az) * Math.PI / 180)), 8);
    look = look.map((v, i) => v + (A.look[i] - v) * w); span = span + (A.span - span) * w;
    if (A.r) { r = r + (A.r - r) * w; h = h + (A.h - h) * w; }
  }
  if (settle > 0 && walkSpan) {
    const lw = [M.c[0], M.ly, M.c[1]];
    look = look.map((v, i) => v + (lw[i] - v) * settle); span += (walkSpan - span) * settle;
    r += (M.r - r) * settle; h += (M.h - h) * settle;
  }
  return { c: M.c.slice(), az, r, h, look, span };
}
const ease = (t) => t * t * (3 - 2 * t);
const lerp = (a, b, t) => a + (b - a) * t;

export class Stage {
  constructor(canvas, { tier = 'lo', base = '', breathe = true } = {}) {
    this.canvas = canvas; this.tier = tier; this.base = base;
    // a living camera: at rest it breathes (a slow dolly and sway), so nothing is ever frozen; it rests after a minute
    this.breathe = breathe; this.awakeUntil = 0; this.lastBreath = 0; this.onframe = null; this.now = 0; this.last = 0;
    this.mode = 'temple'; this.az = MODES.temple.home; this.vel = 0; this.spinning = 0; this.spun = 0; this.onspinend = null;
    this.ext = document.documentElement.dataset.models || '.glb';
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setClearColor(GROUND, 0);                 // see-through: the page's own black shows where there is no stone
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.NoToneMapping;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(30, 1, .01, 30);
    this.frame = { x: 0, y: 0, w: 1, h: 1 };              // the picture area, in CSS px
    this.view = orbitView('temple', this.az);             // the camera's current pose
    this.zoom = 1; this.dirty = true; this.anim = null;
    this.settle = 0; this.walkFit = {}; this.hull = null; this.fitKey = ''; this.band = null;   // the walk's framing (see orbitView)
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
    const map = src.map; if (map) { map.colorSpace = THREE.SRGBColorSpace; map.anisotropy = Math.min(this.tier === 'hi' ? 8 : 4, this.renderer.capabilities.getMaxAnisotropy()); }
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
    grp.children.filter((o) => o.isMesh).forEach((o) => grp.remove(o)); grp.add(new THREE.Mesh(model.geometry, this.material(model, false)));
    if (mirror) {
      this.groups.mirror.children.filter((c) => c.userData.of === name).forEach((c) => this.groups.mirror.remove(c));
      const m = new THREE.Mesh(model.geometry, this.material(model, true)); m.userData.of = name;
      if (name === 'nandi') { m.position.copy(this.groups.nandi.position); m.rotation.copy(this.groups.nandi.rotation); m.scale.copy(this.groups.nandi.scale); }
      this.groups.mirror.add(m);
    }
    this.dirty = true;
  }

  // the lamps' glow, drawn over the stone as the posters' bloom: a soft warm halo on each jali window, the door's thread,
  // the lamp under the mandapa's ceiling (added light; the stone in front of a lamp hides it)
  async glow() {
    const L = await fetch(this.base + 'media/lights.json').then((r) => r.json()).catch(() => null); if (!L) return;
    const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
    const rg = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    rg.addColorStop(0, 'rgba(255,236,190,1)'); rg.addColorStop(.25, 'rgba(255,214,150,.55)'); rg.addColorStop(.6, 'rgba(243,190,120,.14)'); rg.addColorStop(1, 'rgba(243,190,120,0)');
    g.fillStyle = rg; g.fillRect(0, 0, 128, 128);
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
    const mat = (o) => new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: o, depthWrite: false, blending: THREE.AdditiveBlending });
    const win = mat(.42), door = mat(.6), lamp = mat(.5);
    for (const [x, y, z, nx, nz, w, h] of L.temple.windows) {
      const sp = new THREE.Sprite(win); sp.position.set(x + nx * .012, y, z + nz * .012); sp.scale.set(w * 2.4, h * 2.4, 1); this.groups.temple.add(sp);
    }
    const [dx, dy, dz, dh] = L.temple.door;
    const sd = new THREE.Sprite(door); sd.position.set(dx, dy, dz + .012); sd.scale.set(.02, dh * 1.25, 1); this.groups.temple.add(sd);
    const [lx, ly, lz, ls] = L.nandi.lamp;
    const sl = new THREE.Sprite(lamp); sl.position.set(lx, ly, lz); sl.scale.set(ls, ls * .55, 1); this.groups.nandi.add(sl);
    this.glows = [win, door, lamp]; this.dirty = true;
  }

  async load(onProgress) {
    const prog = { temple: [0, 1], nandi: [0, 1] };
    const report = () => onProgress && onProgress((prog.temple[0] + prog.nandi[0]) / Math.max(1, prog.temple[1] + prog.nandi[1]));
    const p = (k) => (e) => { prog[k] = [e.loaded, e.total || e.loaded || 1]; report(); };
    const [t, n] = await Promise.all([this.loadModel(this.base + 'models/temple-lo' + this.ext, p('temple')),
                                      this.loadModel(this.base + 'models/nandi-lo' + this.ext, p('nandi'))]);
    this.place('temple', t); this.place('nandi', n);
    this.lo = { t, n }; await this.glow();
    // the subjects' extreme points (test/hull.cjs), for the walk's one size and its centring
    const H = await fetch(this.base + 'media/hull.json').then((r) => r.json()).catch(() => null);
    if (H) {
      this.groups.nandi.updateMatrixWorld(true);
      this.hull = { temple: H.temple.map((p) => new THREE.Vector3(...p)),
                    nandi: H.nandi.map((p) => new THREE.Vector3(...p).applyMatrix4(this.groups.nandi.matrixWorld)) };
      this.hull.complex = this.hull.temple.concat(this.hull.nandi);
      this.fitKey = ''; this.fitWalk();
    }
    this.ready = true;
  }

  async upgrade() {                                       // the sharper models for capable phones; the reflection keeps the light ones
    try {
      const [t, n] = await Promise.all([this.loadModel(this.base + 'models/temple-hi' + this.ext), this.loadModel(this.base + 'models/nandi-hi' + this.ext)]);
      this.place('temple', t, { mirror: false }); this.place('nandi', n, { mirror: false });
    } catch (e) { /* the light models stay */ }
  }

  // ---------------------------------------------------------------- camera
  // choose what to walk round: shows it (and hides the rest), and stands at azimuth az (default: where that walk starts)
  setMode(name, az) {
    const M = MODES[name]; this.mode = name; this.vel = 0; this.stopSpin();
    this.groups.temple.visible = M.show.temple; this.groups.nandi.visible = M.show.nandi;
    for (const m of this.groups.mirror.children) m.visible = M.show[m.userData.of];
    this.az = az === undefined ? M.home : az; this.zoom = 1;
    this.view = this.viewAt(this.az); this.dirty = true; this.wake();
  }
  viewAt(az) { const w = this.walkFit[this.mode]; return orbitView(this.mode, az, this.settle, w && w.span); }
  setSettle(k) { this.settle = k; this.view = this.viewAt(this.az); this.dirty = true; this.wake(); }
  // the walk's one size per subject on this screen: its widest view fills 96 % of the picture area's width, and from the
  // tower's top to its base it fits the band the stone is seen in (between the name and the controls), at every angle,
  // seen from the walk's own orbit. Its height in that band is fixed too (no bobbing as it turns).
  setBand(band) { this.band = band; this.fitWalk(); }
  fitWalk() {
    if (!this.hull) return;
    const fr = this.frame, band = this.band || { top: fr.y, bottom: fr.y + fr.h };
    const key = [fr.x, fr.y, fr.w, fr.h, band.top, band.bottom].map(Math.round).join(','); if (key === this.fitKey) return; this.fitKey = key;
    if (!this.extents) this.extents = this.measureExtents();          // the sweep round each subject: once, not per layout frame
    const Hb = Math.max(40, band.bottom - band.top), bandCy = (band.top + band.bottom) / 2, frameCy = fr.y + fr.h / 2;
    for (const name of Object.keys(MODES)) {
      const { U, Vt, Vb, dist } = this.extents[name];
      const span = Math.max(U * dist / .96, (Vt + Vb) * fr.w * dist / (Hb * .9));
      const k = fr.w * dist / span;                                         // px per unit of tan, at zoom 1
      this.walkFit[name] = { span, dy: bandCy - (frameCy - (Vt - Vb) / 2 * k) };   // dy: px to move it down, onto the band
    }
    this.view = this.viewAt(this.az); this.dirty = true;
  }
  // each subject's widest angular extent (U), and its reach above (Vt) and below (Vb) the line of sight, over a full
  // circle of the walk's own orbit: independent of the screen, so it is measured once
  measureExtents() {
    const out = {}, up = new THREE.Vector3(0, 1, 0), C = new THREE.Vector3(), L = new THREE.Vector3(), f = new THREE.Vector3(),
      rt = new THREE.Vector3(), u = new THREE.Vector3(), d = new THREE.Vector3();
    for (const name of Object.keys(MODES)) {
      const M = MODES[name], pts = this.hull[name]; let U = 0, Vt = 0, Vb = 0, dist = 1;
      for (let a = 0; a < 360; a += 3) {
        const ar = a * Math.PI / 180; C.set(M.c[0] + Math.cos(ar) * M.r, M.h, M.c[1] + Math.sin(ar) * M.r); L.set(M.c[0], M.ly, M.c[1]);
        f.subVectors(L, C); dist = f.length(); f.normalize(); rt.crossVectors(f, up).normalize(); u.crossVectors(rt, f);
        let u0 = Infinity, u1 = -Infinity, v0 = Infinity, v1 = -Infinity;
        for (const p of pts) { d.subVectors(p, C); const z = d.dot(f); const x = d.dot(rt) / z, y = d.dot(u) / z;
          if (x < u0) u0 = x; if (x > u1) u1 = x; if (y < v0) v0 = y; if (y > v1) v1 = y; }
        U = Math.max(U, u1 - u0); Vt = Math.max(Vt, v1); Vb = Math.max(Vb, -v0);
      }
      out[name] = { U, Vt, Vb, dist };
    }
    return out;
  }
  // where the film's picture must move, and how much it must shrink, to sit exactly on the walk's view of the same stone
  // (one size, centred), from the subject's extreme points seen through both cameras: a least-squares fit of a scale
  // and a shift, in CSS px about the picture area's centre. The hand-over plays it on the picture, so the 3D rises in
  // place and never zooms afterwards.
  pictureFit() {
    if (!this.hull || !this.walkFit[this.mode]) return null;
    const keep = { settle: this.settle, view: this.view, zoom: this.zoom, breathing: this.breathing }, mode = this.mode, home = MODES[mode].home;
    const cx0 = this.frame.x + this.frame.w / 2, cy0 = this.frame.y + this.frame.h / 2;
    const seen = (k) => {
      this.settle = k; this.zoom = 1; this.breathing = false; this.view = orbitView(mode, home, k, this.walkFit[mode].span); this.apply();
      this.camera.updateMatrixWorld();
      return this.hull[mode].map((p) => { const v = p.clone().project(this.camera); return [(v.x + 1) / 2 * this.size.w - cx0, (1 - v.y) / 2 * this.size.h - cy0]; });
    };
    const a = seen(0), b = seen(1); Object.assign(this, keep); this.dirty = true;
    const n = a.length, ma = [0, 0], mb = [0, 0];
    for (let i = 0; i < n; i++) { ma[0] += a[i][0] / n; ma[1] += a[i][1] / n; mb[0] += b[i][0] / n; mb[1] += b[i][1] / n; }
    let num = 0, den = 0;
    for (let i = 0; i < n; i++) { const ax = a[i][0] - ma[0], ay = a[i][1] - ma[1]; num += ax * (b[i][0] - mb[0]) + ay * (b[i][1] - mb[1]); den += ax * ax + ay * ay; }
    const k = num / den; return { scale: k, x: mb[0] - k * ma[0], y: mb[1] - k * ma[1] };
  }
  // turn by d degrees (a drag), let go with a velocity (a flick, in degrees per second), or walk round once (pradakshina)
  rotate(d) { this.az += d; this.view = this.viewAt(this.az); this.dirty = true; this.wake(); }
  fling(v) { this.vel = Math.max(-240, Math.min(240, v)); this.wake(); }
  // walk round (pradakshina): `turns` circles at dps, easing in over rampIn s and out over rampOut s (0, 0: at once)
  spin(dps = 16, turns = 1, rampIn = 0, rampOut = 0) {
    this.vel = 0; this.spinning = dps; this.spun = 0; this.spinTo = 360 * turns; this.rampIn = rampIn; this.rampOut = rampOut; this.spinT = 0; this.wake();
  }
  // stop the walk: at once, or (soft) slowing to a halt over about 0.8 s
  stopSpin(soft) {
    if (soft && this.spinning) { this.rampOut = .8; this.spinTo = this.spun + this.spinV * .4; return; }
    const was = this.spinning; this.spinning = 0; if (was && this.onspinend) this.onspinend();
  }
  wake() { this.awakeUntil = performance.now() + 60000; }
  // the azimuth relative to the building's front (0 = facing its front), for the dial and the captions
  facing() { return wrap(this.az - MODES[this.mode].front + 180) - 180; }

  apply() {
    const v = this.view, cam = this.camera, c = v.c || [0, 0];
    let az = v.az, r = v.r;
    if (this.breathing) {                                   // ±0.4% dolly, ±0.15° sway, a 7 s breath
      const w = this.now / 7000 * Math.PI * 2; r *= 1 + .004 * Math.sin(w); az += .15 * Math.sin(w * .5 + 1.3);
    }
    const a = THREE.MathUtils.degToRad(az);
    cam.position.set(c[0] + Math.cos(a) * r, v.h, c[1] + Math.sin(a) * r);
    cam.lookAt(v.look[0], v.look[1], v.look[2]);
    // frame: the view's span fills the picture area's width (or its height, if the area is narrow and tall); a pinch
    // narrows it (magnifies)
    const W = this.size.w, H = this.size.h, f = this.frame;
    const aspect = f.w / f.h;
    const dist = cam.position.distanceTo(new THREE.Vector3(...v.look));
    const hfov = 2 * Math.atan((v.span / this.zoom * .5) / dist);
    let vfov = 2 * Math.atan(Math.tan(hfov / 2) / aspect);
    vfov = Math.min(vfov, THREE.MathUtils.degToRad(72));
    // the full canvas uses the same focal length; its centre is moved onto the picture area's centre
    cam.fov = THREE.MathUtils.radToDeg(2 * Math.atan(Math.tan(vfov / 2) * (H / f.h)));
    cam.aspect = W / H; cam.updateProjectionMatrix();
    const sx = ((f.x + f.w / 2) - W / 2) / (W / 2), sy = -((f.y + f.h / 2) - H / 2) / (H / 2);
    let cx = 0;                                             // the walk keeps the subject centred: equal gaps left and right
    if (this.settle > 0 && this.hull) {
      const pts = this.hull[this.mode], C = cam.position, fd = new THREE.Vector3(...v.look).sub(C).normalize();
      const rt = new THREE.Vector3().crossVectors(fd, cam.up).normalize(), d = new THREE.Vector3(); let u0 = Infinity, u1 = -Infinity;
      for (const p of pts) { d.subVectors(p, C); const x = d.dot(rt) / d.dot(fd); if (x < u0) u0 = x; if (x > u1) u1 = x; }
      cx = (u0 + u1) / 2 / (Math.tan(vfov / 2) * aspect) * (f.w / W) * this.settle;     // in the canvas's NDC (vfov may be clamped)
    }
    const fit = this.walkFit[this.mode], dy = fit && this.settle > 0 ? fit.dy * this.settle : 0;
    cam.projectionMatrix.elements[8] = -sx + cx; cam.projectionMatrix.elements[9] = -sy + dy / (H / 2);
    cam.projectionMatrixInverse.copy(cam.projectionMatrix).invert();
  }

  setFrame(rect) { this.frame = rect; this.dirty = true; this.fitWalk(); }
  resize() {
    const w = this.canvas.clientWidth || innerWidth, h = this.canvas.clientHeight || innerHeight;
    const dpr = Math.min(devicePixelRatio || 1, this.tier === 'hi' ? 2 : 1.6);
    // only when something changed: resizing the canvas resets it and forces the page's layout again (a dropped frame,
    // every frame, while the layout follows a transition)
    if (this.size && this.size.w === w && this.size.h === h && this.dpr === dpr) return;
    this.renderer.setPixelRatio(dpr); this.renderer.setSize(w, h, false); this.dpr = dpr;
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
    const dt = Math.min(.05, (now - (this.last || now)) / 1000); this.last = now; this.now = now;
    if (this.spinning) {                                    // the walk round: then it stops where it began
      this.spinT += dt; const left = this.spinTo - this.spun; let v = this.spinning;
      if (this.rampIn) v *= ease(Math.min(1, this.spinT / this.rampIn));
      if (this.rampOut) { const brake = this.spinning * this.rampOut / 2; if (left < brake) v = Math.min(v, this.spinning * Math.sqrt(Math.max(0, left) / brake)); }
      this.spinV = v; const d = Math.min(v * dt, left); this.spun += d; this.rotate(d);
      if (this.spun >= this.spinTo - (this.rampOut ? .02 : 0)) { if (this.spinTo > this.spun) this.rotate(this.spinTo - this.spun); this.spun = this.spinTo; this.stopSpin(); }
    } else if (Math.abs(this.vel) > 1) {                    // a flick carries on, slowing
      this.rotate(this.vel * dt); this.vel *= Math.exp(-dt / .45);
    } else this.vel = 0;
    // the breath: only at rest, while the page is looked at; drawn at about 25 frames a second
    this.breathing = this.breathe && !this.spinning && !this.vel && now < this.awakeUntil;
    if (this.breathing && now - this.lastBreath > 40) { this.dirty = true; this.lastBreath = now; }
    if (!this.dirty || !this.ready) return;
    this.apply(); this.renderer.render(this.scene, this.camera); this.dirty = false;
    this.onframe && this.onframe(this.az);
  }
}
