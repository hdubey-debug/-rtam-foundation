// The 3D stage: the temple and the Nandi mandapa with their night baked into the texture (shown unlit, so the colours
// are exactly the posters'), mirrored in a polished dark floor, and a camera that walks round whichever is chosen: the
// temple, Nandi's mandapa, or the whole complex, a full circle each way. What it walks round, the camera's poses, the
// round's easing and the framing are pure functions in motion.js (tested in test/motion.test.mjs).
import * as THREE from 'three';
import { GLTFLoader } from '../lib/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from '../lib/addons/loaders/DRACOLoader.js';
import { MODES, wrap, orbitView, worldHull, fitCentring, centreAt, walkExtents, roundAt, roundDuration, softStop } from './motion.js';

export { MODES };
const GROUND = new THREE.Color(0x141414);

export class Stage {
  constructor(canvas, { tier = 'lo', base = '' } = {}) {
    // the draw loop sleeps: a frame is asked for only when something changed (dirty) or is moving
    this.loop = this.loop.bind(this); this.raf = 0; this._dirty = false; this.last = 0;
    this.canvas = canvas; this.tier = tier; this.base = base; this.onframe = null; this.onspinend = null; this.onlost = null;
    this.mode = 'temple'; this.az = MODES.temple.home; this.vel = 0; this.walk = null;
    this.shown = false;                                   // nothing is drawn until the page shows the 3D (app.js: the hand-over)
    this.ext = document.documentElement.dataset.models || '.glb';
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setClearColor(GROUND, 0);                 // see-through: the page's own black shows where there is no stone
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.NoToneMapping;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(30, 1, .01, 30);
    this.frame = { x: 0, y: 0, w: 1, h: 1 };              // the picture area, in CSS px
    this.view = orbitView('temple', this.az);             // the camera's current pose
    this.zoom = 1; this.anim = null;
    this.settle = 0; this.walkFit = {}; this.hull = null; this.centring = null; this.extents = null; this.fitKey = ''; this.band = null;   // the walk's framing
    this.groups = { temple: new THREE.Group(), nandi: new THREE.Group(), mirror: new THREE.Group() };
    const N = { x: .0176, z: .98, scale: .2014, turn: Math.PI };    // motion.js NANDI: the mandapa before the door, facing it
    this.groups.nandi.position.set(N.x, 0, N.z); this.groups.nandi.rotation.y = N.turn; this.groups.nandi.scale.setScalar(N.scale);
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
    // the phone took the GPU back (memory, a call, the page put away): the page carries on without the 3D
    canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); this.lost = true; this.walk = null; this.onlost && this.onlost(); });
    this.resize();
    if (/[?&]test\b/.test(location.search)) window.__stage = this;
    document.addEventListener('visibilitychange', () => { this.dirty = true; });
  }
  get dirty() { return this._dirty; }
  set dirty(v) { this._dirty = v; if (v) this.request(); }
  request() { if (!this.raf && !this.lost) this.raf = requestAnimationFrame(this.loop); }
  wake() { this.request(); }
  // the page has given up on the 3D (app.js lost()): no more frames, and the GPU given back
  stop() { this.lost = true; this.walk = null; cancelAnimationFrame(this.raf); this.raf = 0; try { this.renderer.dispose(); } catch (e) { /* already gone */ } }

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

  place(name, model) {
    const grp = this.groups[name];
    grp.children.filter((o) => o.isMesh).forEach((o) => grp.remove(o)); grp.add(new THREE.Mesh(model.geometry, this.material(model, false)));
    this.groups.mirror.children.filter((c) => c.userData.of === name).forEach((c) => this.groups.mirror.remove(c));
    const m = new THREE.Mesh(model.geometry, this.material(model, true)); m.userData.of = name;
    if (name === 'nandi') { m.position.copy(this.groups.nandi.position); m.rotation.copy(this.groups.nandi.rotation); m.scale.copy(this.groups.nandi.scale); }
    this.groups.mirror.add(m);
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
    const win = mat(.42), lamp = mat(.5);
    for (const [x, y, z, nx, nz, w, h] of L.temple.windows) {
      const sp = new THREE.Sprite(win); sp.position.set(x + nx * .012, y, z + nz * .012); sp.scale.set(w * 2.4, h * 2.4, 1); this.groups.temple.add(sp);
    }
    // the door's light is the landing's thread: a thin vertical line of lamplight in the gap of the door, fading at its
    // ends (a round glow there read as nothing at all)
    const t = document.createElement('canvas'); t.width = 32; t.height = 128; const tg = t.getContext('2d'), td = tg.createImageData(32, 128);
    const ss = (u) => (u <= 0 ? 0 : u >= 1 ? 1 : u * u * (3 - 2 * u));
    for (let y = 0; y < 128; y++) for (let x = 0; x < 32; x++) {
      const u = (x + .5) / 32 - .5, v = (y + .5) / 128, end = ss(v / .22) * ss((1 - v) / .22);
      const core = Math.exp(-((u / .05) ** 2)), soft = .35 * Math.exp(-((u / .2) ** 2)), a = Math.min(1, (core + soft) * end), o = (y * 32 + x) * 4;
      td.data[o] = 255; td.data[o + 1] = Math.round(206 + 30 * core); td.data[o + 2] = Math.round(140 + 50 * core); td.data[o + 3] = Math.round(255 * a);
    }
    tg.putImageData(td, 0, 0);
    const tt = new THREE.CanvasTexture(t); tt.colorSpace = THREE.SRGBColorSpace;
    const doorLight = new THREE.SpriteMaterial({ map: tt, transparent: true, opacity: .6, depthWrite: false, blending: THREE.AdditiveBlending });
    const [dx, dy, dz, dh] = L.temple.door;
    const sd = new THREE.Sprite(doorLight); sd.position.set(dx, dy, dz + .012); sd.scale.set(.02, dh * 1.25, 1); this.groups.temple.add(sd);
    const [lx, ly, lz, ls] = L.nandi.lamp;
    const sl = new THREE.Sprite(lamp); sl.position.set(lx, ly, lz); sl.scale.set(ls, ls * .55, 1); this.groups.nandi.add(sl);
    this.glows = [win, doorLight, lamp]; this.dirty = true;
  }

  // one set of models for the whole visit, never swapped mid-walk: the sharp ones on a desktop, the light ones on phones
  async load(onProgress) {
    const prog = { temple: [0, 1], nandi: [0, 1] }, q = this.tier === 'hi' ? '-hi' : '-lo';
    const report = () => onProgress && onProgress((prog.temple[0] + prog.nandi[0]) / Math.max(1, prog.temple[1] + prog.nandi[1]));
    const p = (k) => (e) => { prog[k] = [e.loaded, e.total || e.loaded || 1]; report(); };
    const [t, n] = await Promise.all([this.loadModel(this.base + 'models/temple' + q + this.ext, p('temple')),
                                      this.loadModel(this.base + 'models/nandi' + q + this.ext, p('nandi'))]);
    this.place('temple', t); this.place('nandi', n);
    await this.glow();
    // the subjects' extreme points (test/hull.cjs): the walk's one size and its centring, measured once (motion.js)
    const H = await fetch(this.base + 'media/hull.json').then((r) => r.json()).catch(() => null);
    if (H) {
      const hull = worldHull(H); this.centring = {}; this.extents = {};
      this.hull = Object.fromEntries(Object.entries(hull).map(([k, pts]) => [k, pts.map((q) => new THREE.Vector3(...q))]));
      for (const name of Object.keys(MODES)) {
        this.centring[name] = fitCentring(name, hull[name]); this.extents[name] = walkExtents(name, hull[name], this.centring[name]);
      }
      this.fitKey = ''; this.fitWalk();
    }
    // every shader compiled and every texture on the GPU now, while the page is still: a material's first frame costs
    // tens of milliseconds, and must never fall in the hand-over
    this.apply(); this.renderer.compile(this.scene, this.camera); this.renderer.render(this.scene, this.camera);
    this.ready = true; this.dirty = true;
  }

  // ---------------------------------------------------------------- camera
  // choose what to walk round: shows it (and hides the rest), and stands at azimuth az (default: where that walk starts)
  setMode(name, az) {
    const M = MODES[name]; this.mode = name; this.vel = 0; this.stopSpin();
    this.groups.temple.visible = M.show.temple; this.groups.nandi.visible = M.show.nandi;
    for (const m of this.groups.mirror.children) m.visible = M.show[m.userData.of];
    this.az = az === undefined ? M.home : az; this.zoom = 1;
    this.view = this.viewAt(this.az); this.dirty = true;
  }
  viewAt(az) { const w = this.walkFit[this.mode]; return orbitView(this.mode, az, this.settle, w && w.span); }
  setSettle(k) { this.settle = k; this.view = this.viewAt(this.az); this.dirty = true; }
  // the walk's one size per subject on this screen: its widest view, either side of its centre, fills 92 % of the picture
  // area's width, and from the tower's top to its base it fits the band the stone is seen in (between the name and the
  // controls), at every angle, seen from the walk's own orbit. Its height in that band is fixed too (no bobbing).
  setBand(band) { this.band = band; this.fitWalk(); }
  fitWalk() {
    if (!this.extents) return;
    const fr = this.frame, band = this.band || { top: fr.y, bottom: fr.y + fr.h };
    const key = [fr.x, fr.y, fr.w, fr.h, band.top, band.bottom].map(Math.round).join(','); if (key === this.fitKey) return; this.fitKey = key;
    const Hb = Math.max(40, band.bottom - band.top), bandCy = (band.top + band.bottom) / 2, frameCy = fr.y + fr.h / 2;
    for (const name of Object.keys(MODES)) {
      const { U, Vt, Vb, dist } = this.extents[name];
      const span = Math.max(U * dist / .92, (Vt + Vb) * fr.w * dist / (Hb * .9));
      const k = fr.w * dist / span;                                         // px per unit of tan, at zoom 1
      this.walkFit[name] = { span, dy: bandCy - (frameCy - (Vt - Vb) / 2 * k) };   // dy: px to move it down, onto the band
    }
    this.view = this.viewAt(this.az); this.dirty = true;
  }
  // where the film's picture must move, and how much it must shrink, to sit exactly on the walk's view of the same stone
  // (one size, centred), from the subject's extreme points seen through both cameras: a least-squares fit of a scale
  // and a shift, in CSS px about the picture area's centre. The hand-over plays it on the picture, so the 3D rises in
  // place and never zooms afterwards.
  pictureFit() {
    if (!this.hull || !this.walkFit[this.mode]) return null;
    const keep = { settle: this.settle, view: this.view, zoom: this.zoom }, mode = this.mode, home = MODES[mode].home;
    const cx0 = this.frame.x + this.frame.w / 2, cy0 = this.frame.y + this.frame.h / 2;
    const seen = (k) => {
      this.settle = k; this.zoom = 1; this.view = orbitView(mode, home, k, this.walkFit[mode].span); this.apply();
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
  // turn by d degrees (a drag), or let go with a velocity (a flick, in degrees per second)
  rotate(d) { this.setAz(this.az + d); }
  setAz(az) { this.az = az; this.view = this.viewAt(az); this.dirty = true; }
  fling(v) { this.vel = Math.max(-240, Math.min(240, v)); this.request(); }
  // walk round once by itself (S2): easing up to 12°/s and down again, to rest exactly where it began (motion.js)
  spin() { this.vel = 0; this.walk = { az0: this.az, at: roundAt, duration: roundDuration(), t0: null, round: true }; this.request(); }
  get spinning() { return !!this.walk; }
  // seconds left in the round (Infinity if none): the door's lamp brightens in its last moments
  roundLeft() { const w = this.walk; return w && w.round && w.t0 !== null ? w.duration - (performance.now() - w.t0) / 1000 : Infinity; }
  // stop the walk: at once, or softly, its speed falling to rest over about a second
  stopSpin(soft) {
    const w = this.walk; if (!w) return;
    if (soft && w.round && w.t0 !== null) {
      const t = (performance.now() - w.t0) / 1000, v = (w.at(t + .02) - w.at(t - .02)) / .04, s = softStop(v);
      this.walk = { az0: this.az, at: s.at, duration: s.duration, t0: null, round: false }; this.request(); return;
    }
    this.walk = null; this.onspinend && this.onspinend(false);
  }
  // the azimuth relative to the building's front (0 = facing its front), for the dial and the captions
  facing() { return wrap(this.az - MODES[this.mode].front + 180) - 180; }

  apply() {
    const v = this.view, cam = this.camera, c = v.c || [0, 0];
    const a = THREE.MathUtils.degToRad(v.az);
    cam.position.set(c[0] + Math.cos(a) * v.r, v.h, c[1] + Math.sin(a) * v.r);
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
    // the walk keeps the subject centred by a lens shift that follows a smooth curve of the azimuth (motion.js), so the
    // stone turns about a steady axis; in the canvas's NDC (vfov may be clamped)
    const cx = this.settle > 0 && this.centring ? centreAt(this.centring[this.mode], v.az) / (Math.tan(vfov / 2) * aspect) * (f.w / W) * this.settle : 0;
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
    this.raf = 0;
    if (document.hidden) { this.last = 0; return; }        // asleep while put away; coming back marks it dirty
    const dt = Math.min(.05, (now - (this.last || now)) / 1000); this.last = now;
    let moving = false;
    if (this.walk) {                                        // a round, or a soft stop: the angle is a function of time
      const w = this.walk; if (w.t0 === null) w.t0 = now;
      const t = (now - w.t0) / 1000; this.setAz(w.az0 + w.at(t));
      if (t >= w.duration) { this.walk = null; this.onspinend && this.onspinend(w.round); } else moving = true;
    } else if (Math.abs(this.vel) > 1) {                    // a flick carries on, slowing
      this.rotate(this.vel * dt); this.vel *= Math.exp(-dt / .45); moving = true;
    } else this.vel = 0;
    if (this._dirty && this.ready && this.shown) {
      this.apply(); this.renderer.render(this.scene, this.camera); this._dirty = false;
      this.onframe && this.onframe(this.az);
    }
    if (moving) this.request(); else this.last = 0;
  }
}
