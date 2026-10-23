// The tour's motion and framing as pure functions of time and angle: no page, no three.js, so the opening (intro.js),
// the 3D (stage.js), the page (app.js) and the tests (test/motion.test.mjs) all run the same numbers.
// S1, the opening: the Ṛta-chakra turns, then comes to rest upright. S2, the walk: one round that eases up and down,
// and a framing that keeps the stone centred at one size without the camera ever leaving its orbit.

export const smoothstep = (u) => (u <= 0 ? 0 : u >= 1 ? 1 : u * u * (3 - 2 * u));
const rise = (u) => u ** 3 - u ** 4 / 2;                   // ∫ smoothstep: the ground covered while speeding up
const fall = (u) => 2 * u - 2 * u ** 3 + u ** 4;            // ∫ (1 − smoothstep), out of its ½: while slowing to rest

// ---------------------------------------------------------------- S1, the opening
// The chakra turns clockwise at 10°/s from upright. Once the page is ready it brakes, its speed falling as a smoothstep
// over 3 s, which covers exactly 15°; braking only from an angle ≡ 15° (mod 30°), it rests upright (the mark repeats
// every 30°). Those angles come at 1.5, 4.5 and 7.5 s, so it rests at 4.5, 7.5 or 10.5 s: never sooner, never later.
export const TURN = { speed: 10, brake: 3, slots: [1.5, 4.5, 7.5] };
export function brakeAt(readyAt) { return TURN.slots.find((s) => s >= readyAt) ?? TURN.slots[TURN.slots.length - 1]; }
// the chakra's angle (degrees, clockwise) t seconds after it began turning, the page having been ready at readyAt
export function angleAt(t, readyAt = Infinity) {
  const b = brakeAt(readyAt), v = TURN.speed;
  if (t <= b) return v * Math.max(0, t);
  return v * b + v * TURN.brake / 2 * fall(Math.min(1, (t - b) / TURN.brake));
}

// ---------------------------------------------------------------- S2, the walk
// One round, walked by itself: 3 s easing up to 12°/s (a smoothstep in speed), steady, 3 s easing down to rest
// exactly 360° on, where it began. 33 s in all.
export const ROUND = { speed: 12, ramp: 3, turn: 360 };
export const roundDuration = () => ROUND.turn / ROUND.speed + ROUND.ramp;
export function roundAt(t) {
  const { speed: v, ramp: r, turn } = ROUND, T = roundDuration();
  if (t <= 0) return 0;
  if (t >= T) return turn;
  if (t < r) return v * r * rise(t / r);
  if (t > T - r) return turn - v * r * rise((T - t) / r);
  return v * r / 2 + v * (t - r);
}
// stopping softly from v0 °/s: the speed falls as a smoothstep over a second (or less, if slow), covering v0·d/2
export function softStop(v0) {
  const d = Math.min(1, Math.max(.4, Math.abs(v0) / 12));
  return { duration: d, at: (t) => v0 * d / 2 * fall(Math.min(1, Math.max(0, t / d))) };
}

// ---------------------------------------------------------------- what one walks round
// Nandi's mandapa before the temple's door, facing it (placement from the approved viewer, in the temple's units)
export const NANDI = { scale: 0.2014, x: 0.0176, z: 0.98, turn: Math.PI };
// Each walk: the orbit's centre (x, z), the camera's distance and height, the height it looks at, what is shown, the
// footprint whose width the picture keeps framed as it turns (and the least it frames, so the tower or the roof is never
// cut), and where it starts. Azimuths in degrees from +x toward +z (increasing = clockwise from above, the temple on
// one's right: pradakshina). `front` is the side the building faces (the dial's top). At its `anchor` the view is the
// film's last frame (the hand-over draws the 3D through it, exactly over the picture): the temple's solved on its lamps
// (solve_view.py), the mandapa's on its edges and outline (solve_anchor.cjs); turning away, the view eases onto the
// orbit's centre.
export const MODES = {
  temple: { c: [0, 0], r: 1.4961, h: .0658, ly: .1272, show: { temple: true, nandi: false }, front: 90, home: 60.34,
            box: [.488, 1.078], least: .78, anchor: { az: 60.34, look: [.0184, .1272, .144], span: .8004 } },
  // the mandapa's anchor: re-solved 22 Oct 2026 on the film's own edges and outline (build/solve_anchor.cjs), with the
  // film's optical centre (`shift`: its render was larger than its frame); the silhouette fit before left it a pillar off
  nandi: { c: [NANDI.x, NANDI.z], r: .43, h: .085, ly: .062, show: { temple: false, nandi: true }, front: 258.24, home: 251.89,
           box: [.19, .19], least: .23, k: 1.2,
           anchor: { az: 251.89, r: .3111, h: .0676, look: [.0138, .0618, .9842], span: .2489, shift: [.0087, .0077] } },
  complex: { c: [0, .30], r: 2.6, h: .64, ly: .09, show: { temple: true, nandi: true }, front: 90, home: 52,
             box: [.50, 1.57], least: .85, k: 1.12 },
};
export const wrap = (a) => ((a % 360) + 360) % 360;
// the width of a footprint (dx, dz) seen from azimuth az, across the line of sight
const across = (box, az) => { const a = az * Math.PI / 180; return Math.abs(Math.sin(a)) * box[0] + Math.abs(Math.cos(a)) * box[1]; };
// settle (0..1) blends the film's framing into the walk's: one size at every angle (walkSpan, fitted to the subject's
// widest view on this screen) and the orbit's own centre, so turning never zooms. 0 is the film's own framing.
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

// ---------------------------------------------------------------- the walk's framing
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const unit = (a) => { const l = Math.hypot(a[0], a[1], a[2]); return [a[0] / l, a[1] / l, a[2] / l]; };
// the subjects' extreme points (media/hull.json, test/hull.cjs) where they stand: the mandapa moved before the door
export function worldHull(H) {
  const s = NANDI.scale, c = Math.cos(NANDI.turn), n = Math.sin(NANDI.turn);
  const nandi = H.nandi.map(([x, y, z]) => [s * (c * x + n * z) + NANDI.x, s * y, s * (-n * x + c * z) + NANDI.z]);
  return { temple: H.temple, nandi, complex: H.temple.concat(nandi) };
}
// the camera on a walk's own orbit at azimuth az: where it stands, and where it looks
export function orbitCamera(name, az) {
  const M = MODES[name], a = az * Math.PI / 180;
  return { C: [M.c[0] + Math.cos(a) * M.r, M.h, M.c[1] + Math.sin(a) * M.r], L: [M.c[0], M.ly, M.c[1]] };
}
// points seen from C looking at L (up is +y), as tangents across the line of sight (u, to the right) and up it (v)
export function seen(C, L, pts) {
  const f = unit(sub(L, C)), rt = unit(cross(f, [0, 1, 0])), up = cross(rt, f);
  let u0 = Infinity, u1 = -Infinity, v0 = Infinity, v1 = -Infinity;
  for (const p of pts) {
    const d = sub(p, C), z = dot(d, f), x = dot(d, rt) / z, y = dot(d, up) / z;
    if (x < u0) u0 = x; if (x > u1) u1 = x; if (y < v0) v0 = y; if (y > v1) v1 = y;
  }
  return { u0, u1, v0, v1 };
}
// The walk keeps its subject centred with a lens shift (the camera never leaves its orbit, nothing slides in depth):
// the middle of the subject's extreme points, seen at every degree, smoothed into a few harmonics. The raw middle
// kinks wherever another extreme point takes over (about 40 times a round); the harmonics never do. Eight follow the
// square plans of the temple and the mandapa closely enough that the stone stays within 2 % of the centre.
export const HARMONICS = 8;
export function fitCentring(name, pts, K = HARMONICS) {
  const N = 360, mid = new Float64Array(N);
  for (let i = 0; i < N; i++) { const { C, L } = orbitCamera(name, i), s = seen(C, L, pts); mid[i] = (s.u0 + s.u1) / 2; }
  const coef = [];
  for (let k = 0; k <= K; k++) {
    let a = 0, b = 0;
    for (let i = 0; i < N; i++) { const t = k * i * Math.PI / 180; a += mid[i] * Math.cos(t); b += mid[i] * Math.sin(t); }
    coef.push(k ? [2 * a / N, 2 * b / N] : [a / N, 0]);
  }
  return coef;
}
export function centreAt(coef, az) {
  const a = az * Math.PI / 180; let s = coef[0][0];
  for (let k = 1; k < coef.length; k++) s += coef[k][0] * Math.cos(k * a) + coef[k][1] * Math.sin(k * a);
  return s;
}
// what the walk's one size must hold over a full round: the subject's reach either side of the shifted centre (U,
// twice the farther side, so it is never cut), above and below the line of sight (Vt, Vb), and the camera's distance
// to what it looks at (the same all round)
export function walkExtents(name, pts, coef) {
  let U = 0, Vt = 0, Vb = 0;
  for (let az = 0; az < 360; az += .25) {
    const { C, L } = orbitCamera(name, az), s = seen(C, L, pts), c = centreAt(coef, az);
    U = Math.max(U, 2 * Math.max(Math.abs(s.u0 - c), Math.abs(s.u1 - c))); Vt = Math.max(Vt, s.v1); Vb = Math.max(Vb, -s.v0);
  }
  const { C, L } = orbitCamera(name, 0);
  return { U, Vt, Vb, dist: Math.hypot(...sub(L, C)) };
}
