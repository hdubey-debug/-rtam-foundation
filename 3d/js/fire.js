// अग्नि · the lamp's fire (Harsh, 25 Oct 2026, of the reference GIFs he chose: "This is what I was looking for to begin
// with"; then "these are really good"). Drawn as an effects animator draws fire, not simulated: a rounded base and a
// column, and tongues born up its sides that rise, hook outward, stretch, neck off and float away as pieces; ragged edges
// from rising flow noise; one soft heat (a red-orange skin, orange, yellow, a pale heart low down) or, blue, his second
// GIF's (a cyan skin, a violet heart). Redrawn 12 times a second, as the references are drawn on twos.
// Put out, it collapses and grey smoke rises in its place, puffs that swell and drift as they climb; relit, it catches.
//
// One fragment shader, one triangle, WebGL 1, no textures, no requests. It writes premultiplied light (and the smoke's
// grey) over the page's own ground, so it needs no blending mode and shows no box. Its life is a pure function of time
// and the hand's events, so a recording can paint any moment: fire.render(t).
const G = 20 / 255;                                   // the page's ground, #141414
const N = 12, S = 12;                                 // tongues, smoke puffs

const VS = 'attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}';
const FS = (blue) => `#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
#define PAL ${blue ? '1.' : '0.'}
uniform vec3 uMap;                                    // the root's pixel (x, y) and fire units per pixel
uniform float uT, uH, uW, uGlow, uHeat, uAmp, uFade, uFire, uSmoke;
uniform vec4 uB[${N}];                                // tongues: x, y, radius, stretch
uniform float uBw[${N}];                              // their weights
uniform vec4 uP[${S}];                                // smoke puffs: x, y, radius, alpha
vec2 hash22(vec2 p) { vec3 q = fract(vec3(p.xyx) * vec3(.1031, .1030, .0973)); q += dot(q, q.yzx + 33.33); return fract((q.xx + q.yz) * q.zy); }
float hash12(vec2 p) { vec3 q = fract(vec3(p.xyx) * .1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
// gradient noise with a quintic fade, periodic in y every 8 cells (time wraps, never losing precision)
float gn(vec2 p) {
  vec2 i = floor(p), f = fract(p), u = f * f * f * (f * (f * 6. - 15.) + 10.);
  float y0 = mod(i.y, 8.), y1 = mod(i.y + 1., 8.);
  float a = dot(hash22(vec2(i.x, y0)) * 2. - 1., f);
  float b = dot(hash22(vec2(i.x + 1., y0)) * 2. - 1., f - vec2(1., 0.));
  float c = dot(hash22(vec2(i.x, y1)) * 2. - 1., f - vec2(0., 1.));
  float d = dot(hash22(vec2(i.x + 1., y1)) * 2. - 1., f - vec2(1.));
  return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}
// the fire: its base and its column (weighted by uFire: put out, they sink), and the tongues, as soft metaballs, so
// where a tongue leaves the body the bridge thins into a neck and parts by itself
float field(vec2 q) {
  vec2 d0 = (q - vec2(0., .2)) / vec2(.17, .17);
  vec2 d1 = (q - vec2(.025 * sin(uT * 1.7), .42)) / vec2(.085, .23);
  float F = uFire * (exp(-dot(d0, d0)) + .62 * exp(-dot(d1, d1)));
  for (int i = 0; i < ${N}; i++) { vec2 d = (q - uB[i].xy) / vec2(uB[i].z, uB[i].z * uB[i].w); F += uBw[i] * exp(-dot(d, d)); }
  return F;
}
float smoke(vec2 q) {
  float s = 0.;
  for (int i = 0; i < ${S}; i++) { vec2 d = (q - uP[i].xy) / uP[i].z; s += uP[i].w * exp(-dot(d, d)); }
  return s;
}
void main() {
  vec2 p = (gl_FragCoord.xy - uMap.xy) * uMap.z;
  float y = p.y / uH, x = p.x / uW;
  float up = smoothstep(.08, .9, y);
  // ragged, living edges: the sample point pushed about by rising flow noise, more as it climbs
  float ty = mod(uT * 1.4, 8.), ty2 = mod(uT * 2.24, 8.);
  vec2 w = vec2(gn(vec2(x * 5.5, y * 4.4 - ty)), gn(vec2(x * 5.5 + 5.2, y * 4.4 - ty + 3.1)))
         + .5 * vec2(gn(vec2(x * 11.55 + 1.7, y * 9.35 - ty2)), gn(vec2(x * 11.55 + 8.3, y * 9.35 - ty2 + 6.2)));
  vec2 q = vec2(x, y) + w * (.03 + .15 * up);
  float f = (field(q) - .5) * uAmp;                    // > 0 inside the fire
  // a soft skin and one continuous heat: no bands
  float a = smoothstep(-.045, .027, f);
  float low = 1. - smoothstep(.12, .7, y);
  float heat = min(1., clamp(f / .8, 0., 1.) * (.55 + .45 * low) * 1.1 + .12 * uHeat);
  vec3 k0 = PAL < .5 ? vec3(.88, .24, .07) : vec3(.2, .78, 1.);
  vec3 k1 = PAL < .5 ? vec3(1., .52, .12) : vec3(.25, .58, 1.);
  vec3 k2 = PAL < .5 ? vec3(1., .78, .2) : vec3(.33, .45, 1.);
  vec3 k3 = PAL < .5 ? vec3(1., .9, .38) : vec3(.32, .4, .98);
  vec3 k4 = PAL < .5 ? vec3(1., .93, .45) : vec3(.36, .3, .9);
  vec3 kc = PAL < .5 ? vec3(.8, .2, .06) : vec3(.18, .85, 1.);
  vec3 c = mix(k0, k1, smoothstep(.02, .25, heat));
  c = mix(c, k2, smoothstep(.22, .48, heat));
  c = mix(c, k3, smoothstep(.45, .72, heat));
  c = mix(c, k4, smoothstep(.7, .95, heat));
  // flames rising inside the body (lighter in the yellow, darker in the blue, as in his two GIFs)
  float st = gn(vec2(x * 7., y * 2.4 - mod(uT * 1.3, 8.)));
  c = min(c * (1. + (PAL < .5 ? .3 : -.42) * st * smoothstep(.25, .6, heat)), 1.);
  // as it climbs it cools and thins: its pieces redden (or turn cyan) and fade
  float cool = smoothstep(.3, 1.15, y);
  c = mix(c, kc, cool * (1. - smoothstep(.35, .7, heat)) * .95);
  a *= 1. - .35 * cool * (1. - smoothstep(.2, .5, heat));
  // its glow, zero long before the canvas's edges
  vec2 e = vec2(x / .55, (y - .35) / .85);
  float win = 1. - smoothstep(.4, 1., length(e));
  float bl = exp(-10. * max(-f, 0.)) * win;
  vec3 L = (c * a + (PAL < .5 ? vec3(1., .45, .12) : vec3(.2, .6, 1.)) * (.3 * bl + .05 * win * win) * uGlow * (1. - a)) * uFade;
  float lum = max(L.r, max(L.g, L.b));
  L = max(L + (hash12(gl_FragCoord.xy + fract(uT * 7.) * 97.) - .5) / 255. * step(.004, lum), 0.);
  // the fire as light over the ground, premultiplied with the least alpha
  float fa = max(L.r, max(L.g, L.b));
  vec4 fire = vec4(L * (1. - ${G.toFixed(6)}) + fa * ${G.toFixed(6)}, fa);
  // the smoke under it: a warm grey, soft, its edges pushed about by the same flow
  // (a thread from where the flame was, curling as it climbs and widening; gone before the canvas's top and sides)
  float sa = smoothstep(.12, .8, smoke(vec2(x, y) + w * .12)) * .85 * uSmoke * (1. - smoothstep(1.45, 2.05, y)) * (1. - smoothstep(.45, .75, abs(x)));
  vec3 sc = vec3(.42, .4, .38);
  gl_FragColor = fire + vec4(sc * sa, sa) * (1. - fire.a);
}`;

// ---------------------------------------------------------------- its life (pure functions of t and the hand's events)
const TAU = Math.PI * 2;
const h1 = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const vn = (x) => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return (h1(i) * (1 - u) + h1(i + 1) * u) * 2 - 1; };
const clamp01 = (v) => Math.max(0, Math.min(1, v));
const outCubic = (u) => 1 - Math.pow(1 - clamp01(u), 3);
const sine = (u) => 0.5 - 0.5 * Math.cos(Math.PI * clamp01(u));

export class Life {
  constructor() { this.pressT = this.releaseT = this.tapT = null; this.lit = true; this.switchT = -1e9; }
  press(t) { if (this.tapT == null) { this.pressT = t; this.releaseT = null; } }
  release(t) { if (this.pressT != null && this.releaseT == null) this.releaseT = t; }
  tap(t) { if (this.tapT == null) { this.tapT = t; if (this.pressT != null && this.releaseT == null) this.releaseT = t; } }
  // put out (lit false) or relit (lit true) at t: the smoke comes in 0.6 s as the fire sinks; the fire catches in 0.6 s
  set(lit, t) { if (lit !== this.lit) { this.lit = lit; this.switchT = t; } }
  pressAmt(t) {
    if (this.pressT == null || t < this.pressT) return 0;
    const inn = clamp01((t - this.pressT) / 0.09);
    return this.releaseT == null || t < this.releaseT ? inn : inn * (1 - clamp01((t - this.releaseT) / 0.22));
  }
  roar(t) { return this.tapT == null || t < this.tapT ? 0 : outCubic((t - this.tapT) / 0.45); }
  fireAmt(t) { const u = t - this.switchT; return this.lit ? outCubic(u / 0.6) : 1 - sine(u / 0.6); }
  // the tongues: born inside the base on their own cycles (0.75–1.25 s), up the column's sides at different heights (a
  // side tongue curls out, then up: a hook) or at its top; each rises (quickening), stretches, shrinks and sways, its
  // weight easing in and out; every cycle re-seeded, so no second repeats. The roar makes them bigger and quicker
  tongues(t, ro, k) {
    const B = new Float32Array(N * 4), Bw = new Float32Array(N);
    for (let i = 0; i < N; i++) {
      const P = (0.75 + 0.5 * h1(i * 7.3 + 1.1)) / (1 + 0.6 * ro), ph = (i / N + 0.37 * h1(i * 3.9)) * P;
      const q = (t + ph) / P, c = Math.floor(q), u = q - c;
      const s1 = h1(i * 17.1 + c * 3.17), s2 = h1(i * 5.3 + c * 7.71 + 2.2), s3 = h1(i * 9.7 + c * 1.93 + 4.4);
      const side = s1 < 0.5 ? -1 : 1, top = s3 < 0.35;
      const x0 = top ? (s1 - 0.5) * 0.12 : side * (0.05 + 0.07 * s2), y0 = top ? 0.42 : 0.2 + 0.22 * s3;
      const y = y0 + (0.7 + 0.5 * s2) * (1 + 0.35 * ro) * Math.pow(u, 1.15);
      const x = x0 + (top ? 0 : side * 0.09 * Math.sin(Math.PI * Math.min(1, u * 1.6))) + (0.04 + 0.05 * s3) * Math.sin(TAU * (0.75 * u + s2)) * u;
      const r = (0.062 + 0.032 * s3) * (1 + 0.25 * ro) * (1 - 0.66 * u) * (0.35 + 0.65 * k);
      B.set([x, y, r, 1.4 + 1.9 * u], i * 4);
      Bw[i] = (0.75 + 0.3 * s1) * Math.min(1, u / 0.1) * (1 - Math.max(0, (u - 0.75) / 0.25)) * k;
    }
    return { B, Bw };
  }
  // the smoke: a thread rising from where the flame was, its puffs born at the root one after another (2.0–2.6 s each),
  // curling as they climb, widening and thinning; only puffs born since the fire went out, so the plume grows up from
  // the root (and fades with the smoke as the fire catches again)
  puffs(t) {
    const P4 = new Float32Array(S * 4);
    for (let i = 0; i < S; i++) {
      const P = 2.0 + 0.6 * h1(i * 4.1 + 0.3), ph = (i / S) * P, q = (t + ph) / P, c = Math.floor(q), u = q - c;
      const s1 = h1(i * 13.3 + c * 2.9), s2 = h1(i * 3.7 + c * 5.3 + 1.7);
      const born = c * P - ph, since = this.lit ? 1 : clamp01((born - this.switchT + 0.15) / 0.3);
      const x = 0.03 * (s1 - 0.5) + (0.04 + 0.1 * u) * Math.sin(TAU * (0.6 * u + s2)) + 0.12 * u * u * (s2 - 0.5);
      P4.set([x, 0.1 + 1.8 * Math.pow(u, 1.25), 0.05 + 0.15 * u, (1 - u) * Math.min(1, u / 0.08) * since], i * 4);
    }
    return P4;
  }
  at(t) {
    // the breath that invites: every 4.4 s it draws up and brightens, never twice alike
    const ph = (t + 1.2) / 4.4, kk = ph - Math.floor(ph), cyc = Math.floor(ph);
    const swell = Math.pow(Math.sin(Math.PI * kk), 4) * (0.8 + 0.4 * h1(cyc * 3.7));
    const flick = vn(t * 1.7) * 0.6 + vn(t * 4.3 + 9) * 0.4;
    const pr = this.pressAmt(t), ro = this.roar(t), k = this.fireAmt(t);
    const tg = this.tongues(t, ro, k);
    return {
      B: tg.B, Bw: tg.Bw, P: this.puffs(t), fire: k, smoke: 1 - k,
      T: t * (1 + 0.8 * ro),
      H: (1 + 0.06 * swell + 0.02 * flick - 0.05 * pr) * (1 + 0.42 * ro),
      W: (1 + 0.03 * swell - 0.03 * pr) * (1 + 0.08 * ro),
      glow: (1 + 0.22 * swell + 0.06 * flick - 0.1 * pr) * (1 + 0.8 * ro) * k,
      heat: 0.35 * swell + 0.1 * flick - 0.4 * pr + 0.35 * ro,
      amp: 1 + 0.15 * ro,
      fade: 1,
    };
  }
  done(t) { return this.tapT != null && t >= this.tapT + 1.35; }
}

// ---------------------------------------------------------------- the fire on its canvas
// The canvas spans the fire's units x ∈ ±(its aspect × SPAN / 2), y ∈ [−BELOW, ABOVE] about the root, so its pieces can
// fly well above it. Its CSS: height = SPAN × the fire's height, the root BELOW × that over its bottom.
export const BELOW = 0.42, ABOVE = 2.2, SPAN = BELOW + ABOVE;
export class Fire {
  constructor(canvas, { maxDpr = 2, draw = 12, blue = false, keep = false } = {}) {
    this.cv = canvas; this.maxDpr = maxDpr; this.draw = draw; this.life = new Life();
    const gl = canvas.getContext('webgl', { alpha: true, premultipliedAlpha: true, antialias: false, depth: false, stencil: false, preserveDrawingBuffer: keep, powerPreference: 'low-power' });
    if (!gl) throw new Error('no webgl');
    this.gl = gl;
    const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
    const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS(blue)));
    gl.bindAttribLocation(pr, 0, 'a'); gl.linkProgram(pr);
    if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pr));
    gl.useProgram(pr);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    this.u = {}; for (const k of ['uMap', 'uT', 'uH', 'uW', 'uGlow', 'uHeat', 'uAmp', 'uFade', 'uFire', 'uSmoke', 'uB', 'uBw', 'uP']) this.u[k] = gl.getUniformLocation(pr, k);
    this.t0 = performance.now(); this.raf = 0; this.last = -1; this.want = false; this.gone = false;
    this.tick = this.tick.bind(this);
    this.resize();
  }
  resize() {
    const r = this.cv.getBoundingClientRect(), d = Math.min(this.maxDpr, window.devicePixelRatio || 1);
    const w = Math.max(1, Math.round(r.width * d)), h = Math.max(1, Math.round(r.height * d));
    if (this.cv.width !== w || this.cv.height !== h) { this.cv.width = w; this.cv.height = h; this.last = -1; }
    this.gl.viewport(0, 0, w, h);
    const unit = h / SPAN;                                      // pixels per fire unit (the fire's height)
    this.map = [w / 2, BELOW * unit, 1 / unit];
    if (!this.raf && !this.gone && this.last >= 0) this.render(this.now);   // (a resize clears the canvas)
  }
  // a drawing for time t: the fire is redrawn `draw` times a second, as the references are drawn on twos
  render(t) {
    const td = Math.floor(t * this.draw + 1e-6) / this.draw;
    const gl = this.gl, u = this.u, s = this.life.at(td);
    gl.uniform3f(u.uMap, this.map[0], this.map[1], this.map[2]);
    gl.uniform1f(u.uT, s.T); gl.uniform1f(u.uH, s.H); gl.uniform1f(u.uW, s.W); gl.uniform1f(u.uGlow, s.glow);
    gl.uniform1f(u.uHeat, s.heat); gl.uniform1f(u.uAmp, s.amp); gl.uniform1f(u.uFade, s.fade);
    gl.uniform1f(u.uFire, s.fire); gl.uniform1f(u.uSmoke, s.smoke);
    gl.uniform4fv(u.uB, s.B); gl.uniform1fv(u.uBw, s.Bw); gl.uniform4fv(u.uP, s.P);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    this.last = td;
  }
  get now() { return (performance.now() - this.t0) / 1000; }
  // live: it burns while it is wanted and the page is in view, and sleeps otherwise; a new drawing only when one is due
  run(on) { this.want = on; this.cv.dataset.state = on ? 'burning' : 'asleep'; if (on) this.wake(); else this.sleep(); }
  wake() { if (this.want && !this.gone && !this.raf && !document.hidden) this.raf = requestAnimationFrame(this.tick); }
  sleep() { if (this.raf) cancelAnimationFrame(this.raf); this.raf = 0; }
  tick() {
    this.raf = 0;
    if (!this.want || document.hidden || this.gone) return;
    const t = this.now;
    if (Math.floor(t * this.draw + 1e-6) / this.draw !== this.last) this.render(t);
    this.raf = requestAnimationFrame(this.tick);
  }
  press() { this.life.press(this.now); this.wake(); }
  release() { this.life.release(this.now); }
  light() { this.life.tap(this.now); this.want = true; this.wake(); }        // the landing's tap: the roar
  set(lit) { this.life.set(lit, this.now); this.wake(); }                    // the walk's lamp: out (smoke) or relit
  free() { this.sleep(); this.gone = true; this.cv.dataset.state = 'gone'; const x = this.gl.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); }
}
