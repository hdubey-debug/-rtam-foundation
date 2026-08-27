/**
 * The Murti, Measured — parametric 3D study of the Ṛtambhareśvara murti.
 *
 * One normalized parameter state (R = rim outer radius = 1.0, the grid.json
 * convention) drives the whole solid: linga, collar, lotus tiers, water,
 * drum, medallions, nālī, pool. The codified preset IS
 * brand/iconography/geometry/grid.json; deviations are measured against it
 * and reported, never blocked — the canon is the founder's to move.
 *
 * Engraving discipline (construct.py): charcoal ink on ivory, gold reserved
 * for the god-points (waterline, medallions, the drop), stone-gray guides.
 */
import * as THREE from "three";

/* ───────────────────────── palette ───────────────────────── */
const INK = 0x1a1a1a;
const GOLD = 0xc8a15a;
const STONE_LINE = 0xb8b1a4;
const IVORY = 0xf7f3e9;
const STONE = 0xe9e2d1;
const CHARCOAL = 0x3a3733; // the linga (palette: charcoal = the linga)
const WATER = 0xa8bcc9;    // indigo, desaturated to daylight
const POOL_IN = 0xcdc5b2;

/* ───────────────────────── canon ─────────────────────────── */
// The codified murti — grid.json numbers verbatim, plus the 3D extensions
// grid.json never had to state (collar, dome, tilts…), chosen neutral.
const CANON = {
  counts: { medallions: 12, petalsUpper: 12, petalsLower: 12, tierOffsetDeg: 15 },
  rings: {
    linga: 0.22, jaladhari: 0.32, cupOuter: 0.375, tier1PetalTip: 0.48, tier2PetalTip: 0.62,
    waterOuter: 0.84, medallionCenter: 0.92, medallionRadius: 0.045,
  },
  elev: {
    rimHeight: 0.46, waterlineOverRimHeight: 0.88, lotusCupTopAboveRim: 0.18,
    lingaHeightAboveLotus: 0.92, collarHeight: 0.1, lingaDomeRatio: 1.0,
    plinthHeight: 0.0, basinDepth: 0.4, poolWidth: 0.5, poolDepth: 0.12,
  },
  nali: {
    widthOverR: 0.18, lengthBeyondRimOverR: 0.14, sillBelowWaterline: 0.05,
    style: "weir", stationPolicy: "between", trishul: false, stream: false,
  },
  petal: { tiltLowerDeg: 78, belly: 0.5, cup: 0.5, padThickness: 0.03 },
  display: { guides: false, wireframe: false, material: "canon", measures: false },
};

// The founder's 7·1·4·2 grammar (2026-08-24), inches → R units (R = 93.5 in).
// Verticals: 169 total = podium 31 + jalādhārī-above-rim 29 + liṅga 109;
// floor 22, waterline 29 (proposed: depth 7, freeboard 2). Diameters:
// 187 · 151 · 121 · 109 · 92 · 73 · 58; suns mid-band on Ø169 = (151+187)/2.
// Full audit: GRAMMAR.md.
const GRAMMAR_PRESET = {
  counts: { medallions: 12, petalsUpper: 12, petalsLower: 12, tierOffsetDeg: 15 },
  rings: {
    linga: 0.3102, jaladhari: 0.3904, cupOuter: 0.492, tier1PetalTip: 0.5829, tier2PetalTip: 0.6471,
    waterOuter: 0.8075, medallionCenter: 0.9037, medallionRadius: 0.0535,
  },
  elev: {
    // the silent-nine shift: podium 40 · jalādhārī 29 (20 above rim) — every
    // digit root invariant (±9 ≡ 0 mod 9), cup top stays 60, total stays 169.
    // Waterline 38 in (floor 31 + depth 7, freeboard 2).
    rimHeight: 0.4278, waterlineOverRimHeight: 0.95, lotusCupTopAboveRim: 0.2139,
    lingaHeightAboveLotus: 1.1658, collarHeight: 0.107, lingaDomeRatio: 1.0,
    plinthHeight: 0.0, basinDepth: 0.0963, poolWidth: 0.4599, poolDepth: 0.1176,
  },
  nali: {
    widthOverR: 0.2139, lengthBeyondRimOverR: 0.139, sillBelowWaterline: 0.0214,
    style: "weir", stationPolicy: "between", trishul: false, stream: true,
  },
  petal: { tiltLowerDeg: 80, belly: 0.5, cup: 0.5, padThickness: 0.0428 },
  display: { guides: false, wireframe: false, material: "canon", measures: true },
};

// shivling.png, measured — APPROXIMATE (read off a perspective render).
const IMAGE_PRESET = {
  counts: { medallions: 14, petalsUpper: 30, petalsLower: 26, tierOffsetDeg: 6 },
  rings: {
    linga: 0.3, jaladhari: 0.4, cupOuter: 0.455, tier1PetalTip: 0.57, tier2PetalTip: 0.74,
    waterOuter: 0.86, medallionCenter: 0.92, medallionRadius: 0.042,
  },
  elev: {
    rimHeight: 0.4, waterlineOverRimHeight: 0.7, lotusCupTopAboveRim: 0.27,
    lingaHeightAboveLotus: 1.61, collarHeight: 0.22, lingaDomeRatio: 1.15,
    plinthHeight: 0.15, basinDepth: 0.34, poolWidth: 0.5, poolDepth: 0.12,
  },
  nali: {
    widthOverR: 0.16, lengthBeyondRimOverR: 0.1, sillBelowWaterline: 0.05,
    style: "slot", stationPolicy: "between", trishul: true, stream: true,
  },
  petal: { tiltLowerDeg: 68, belly: 0.62, cup: 0.62, padThickness: 0.045 },
  display: { guides: false, wireframe: false, material: "stone", measures: false },
};

const deep = (o) => JSON.parse(JSON.stringify(o));
let state = deep(CANON);

/* persistence (per-viewer convenience only) */
const LS_KEY = "murti-measured-v1";
try {
  const saved = localStorage.getItem(LS_KEY);
  if (saved) {
    // merge per group so params added in later builds keep their canon value
    const s = JSON.parse(saved);
    state = deep(CANON);
    for (const g of Object.keys(CANON)) Object.assign(state[g], s[g] || {});
  }
} catch (e) { /* storage unavailable — run from canon */ }
function persist() {
  try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch (e) { /* ok */ }
}

/* ─────────────────────── scene setup ─────────────────────── */
const stage = document.getElementById("stage");
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setClearColor(IVORY, 1);
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, 0.05, 60);
// true elevation/plan for the measured views — perspective flatters, ortho testifies
const ocam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.05, 60);
let useOrtho = false;
const activeCam = () => (useOrtho ? ocam : camera);

scene.add(new THREE.HemisphereLight(0xfffdf4, 0xcfc7b4, 1.15));
const sun = new THREE.DirectionalLight(0xfff6e6, 0.55);
sun.position.set(2.2, 3.4, 1.6);
scene.add(sun);
const fill = new THREE.DirectionalLight(0xf0ead9, 0.22);
fill.position.set(-2.6, 1.2, -1.8);
scene.add(fill);

/* materials */
function makeMats() {
  const plain = state.display.material !== "canon";
  return {
    stone: new THREE.MeshLambertMaterial({ color: STONE, side: THREE.DoubleSide }),
    linga: new THREE.MeshLambertMaterial({ color: plain ? STONE : CHARCOAL, side: THREE.DoubleSide }),
    gold: new THREE.MeshLambertMaterial({ color: GOLD, emissive: 0x38290e, emissiveIntensity: 0.55 }),
    water: new THREE.MeshLambertMaterial({ color: WATER, transparent: true, opacity: 0.82, side: THREE.DoubleSide }),
    poolIn: new THREE.MeshLambertMaterial({ color: POOL_IN, side: THREE.DoubleSide }),
    ink: new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity: 0.85 }),
    inkSoft: new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity: 0.4 }),
    guide: new THREE.LineDashedMaterial({ color: STONE_LINE, dashSize: 0.05, gapSize: 0.045, transparent: true, opacity: 0.9 }),
    goldDash: new THREE.LineDashedMaterial({ color: GOLD, dashSize: 0.012, gapSize: 0.05, transparent: true, opacity: 0.8 }),
    goldLine: new THREE.LineBasicMaterial({ color: GOLD, transparent: true, opacity: 0.95 }),
    wire: new THREE.MeshBasicMaterial({ color: INK, wireframe: true, transparent: true, opacity: 0.14 }),
  };
}
let M = makeMats();

/* ─────────────────── geometry helpers ────────────────────── */
// Surface of revolution around +Y. theta measured from +Z (x = r sinθ, z = r cosθ),
// so a gap of gapDeg is centered on +Z — the devotee's side, where the nālī breaks.
function lathe(profile, { gapDeg = 0, seg = 140, capGap = false } = {}) {
  const g = THREE.MathUtils.degToRad(gapDeg) / 2;
  const t0 = gapDeg > 0 ? g : 0;
  const t1 = gapDeg > 0 ? Math.PI * 2 - g : Math.PI * 2;
  const rows = profile.length;
  const pos = [], idx = [];
  for (let i = 0; i <= seg; i++) {
    const th = t0 + ((t1 - t0) * i) / seg;
    const s = Math.sin(th), c = Math.cos(th);
    for (let j = 0; j < rows; j++) {
      const [r, y] = profile[j];
      pos.push(r * s, y, r * c);
    }
  }
  for (let i = 0; i < seg; i++)
    for (let j = 0; j < rows - 1; j++) {
      const a = i * rows + j, b = a + rows;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  const geo = new THREE.BufferGeometry();
  const base = pos.length / 3;
  if (capGap && gapDeg > 0) {
    // close the two cut faces with the profile polygon itself
    const pts2 = profile.map(([r, y]) => new THREE.Vector2(r, y));
    const tris = THREE.ShapeUtils.triangulateShape(pts2, []);
    for (const th of [t0, t1]) {
      const s = Math.sin(th), c = Math.cos(th);
      const start = pos.length / 3;
      for (const [r, y] of profile) pos.push(r * s, y, r * c);
      for (const [a, b, cc] of tris) idx.push(start + a, start + b, start + cc);
    }
  }
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  return geo;
}

// Flat ink circle at height y (torus, hairline). Gap centered on +Z when gapDeg>0.
function inkRing(r, y, { tube = 0.0038, gapDeg = 0, mat = M.ink } = {}) {
  const g = THREE.MathUtils.degToRad(gapDeg);
  const t = new THREE.TorusGeometry(r, tube, 6, 160, Math.PI * 2 - g);
  t.rotateZ(Math.PI / 2 + g / 2);
  t.rotateX(Math.PI / 2);
  t.translate(0, y, 0);
  const mesh = new THREE.Mesh(t, mat === M.ink ? new THREE.MeshBasicMaterial({ color: INK }) :
    new THREE.MeshBasicMaterial({ color: mat === "gold" ? GOLD : INK }));
  if (mat === "gold") mesh.material.color.set(GOLD);
  return mesh;
}

// Dashed construction circle on the ground.
function guideCircle(r, y = 0.004) {
  const pts = [];
  for (let i = 0; i <= 128; i++) {
    const a = (i / 128) * Math.PI * 2;
    pts.push(new THREE.Vector3(r * Math.sin(a), y, r * Math.cos(a)));
  }
  const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), M.guide);
  line.computeLineDistances();
  return line;
}

// One lotus petal as a parametric shell at center-angle 0; instanced per station.
// The centerline is a SPINE (array of [r, z]) — straight for the upright buds,
// an S-curve for pads that bloom under water and flatten on its surface.
// tip: "point" = ogive; "round" = plump kośa bud. thick > 0 adds a slab skirt.
function straightSpine(baseR, baseZ, len, tiltDeg, belly, U = 12) {
  const tilt = THREE.MathUtils.degToRad(tiltDeg);
  const pts = [];
  for (let i = 0; i <= U; i++) {
    const u = i / U;
    pts.push([baseR + Math.sin(tilt) * len * u + belly * 0.16 * len * Math.sin(Math.PI * u),
      baseZ + Math.cos(tilt) * len * u]);
  }
  return pts;
}
function petalGeo({ spine, wArc, cup, tip = "point", thick = 0 }) {
  const U = spine.length - 1, V = 8;
  let L = 0;
  for (let i = 0; i < U; i++) L += Math.hypot(spine[i + 1][0] - spine[i][0], spine[i + 1][1] - spine[i][1]);
  const pos = [], idx = [];
  const width = tip === "round"
    ? (u) => Math.sqrt(Math.max(0.002, 1 - Math.pow(u, 2.6))) * (0.82 + 0.18 * Math.sin(Math.PI * Math.min(u * 2, 1)))
    : (u) => Math.pow(Math.sin(Math.PI * (0.17 + 0.83 * u)), 0.72);
  for (let i = 0; i <= U; i++) {
    const u = i / U;
    const [r0, y] = spine[i];
    const w = wArc * width(u) + 0.002;
    for (let j = 0; j <= V; j++) {
      const v = (j / V) * 2 - 1;
      const rr = r0 + cup * 0.14 * L * (1 - v * v) * Math.sin(Math.PI * Math.min(u * 1.25, 1));
      const th = (v * w) / Math.max(rr, 0.03);
      pos.push(rr * Math.sin(th), y, rr * Math.cos(th));
    }
  }
  for (let i = 0; i < U; i++)
    for (let j = 0; j < V; j++) {
      const a = i * (V + 1) + j, b = a + V + 1;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  const at3 = (i, j) => [pos[3 * (i * (V + 1) + j)], pos[3 * (i * (V + 1) + j) + 1], pos[3 * (i * (V + 1) + j) + 2]];
  if (thick > 0) {
    // slab skirt: the outline extruded downward — stone that floats
    const loop = [];
    for (let i = 0; i <= U; i++) loop.push(at3(i, 0));
    for (let i = U; i >= 0; i--) loop.push(at3(i, V));
    for (let k = 0; k < loop.length - 1; k++) {
      const a = loop[k], b = loop[k + 1];
      const s = pos.length / 3;
      pos.push(a[0], a[1], a[2], b[0], b[1], b[2], b[0], b[1] - thick, b[2], a[0], a[1] - thick, a[2]);
      idx.push(s, s + 1, s + 2, s, s + 2, s + 3);
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(idx);
  geo.computeVertexNormals();
  const edge = [];
  const at = (i, j) => new THREE.Vector3(...at3(i, j));
  for (let i = 0; i < U; i++) { edge.push(at(i, 0), at(i + 1, 0)); edge.push(at(i, V), at(i + 1, V)); }
  for (let j = 0; j < V; j++) { edge.push(at(0, j), at(0, j + 1)); }
  return { geo, edge };
}

function tierGroup(n, offsetDeg, spec, mat) {
  const grp = new THREE.Group();
  if (!spec.spine) spec.spine = straightSpine(spec.baseR, spec.baseZ, spec.len, spec.tiltDeg, spec.belly ?? 0);
  const { geo, edge } = petalGeo(spec);
  const inst = new THREE.InstancedMesh(geo, mat, n);
  const m4 = new THREE.Matrix4();
  const linePts = [];
  const rotPt = new THREE.Vector3();
  for (let k = 0; k < n; k++) {
    const a = THREE.MathUtils.degToRad(offsetDeg + (360 / n) * k);
    m4.makeRotationY(a);
    inst.setMatrixAt(k, m4);
    for (const p of edge) { rotPt.copy(p).applyMatrix4(m4); linePts.push(rotPt.x, rotPt.y, rotPt.z); }
  }
  inst.instanceMatrix.needsUpdate = true;
  grp.add(inst);
  const lg = new THREE.BufferGeometry();
  lg.setAttribute("position", new THREE.Float32BufferAttribute(linePts, 3));
  grp.add(new THREE.LineSegments(lg, M.inkSoft));
  if (state.display.wireframe) grp.add(new THREE.Mesh(geo.clone(), M.wire));
  return grp;
}

function trishulLines(h) {
  // engraved line trident (un-codified — drawn only when toggled)
  const s = h, pts = [];
  const seg = (x1, y1, x2, y2) => pts.push(new THREE.Vector3(x1, y1, 0), new THREE.Vector3(x2, y2, 0));
  seg(0, 0, 0, s * 0.42);                       // shaft
  seg(-s * 0.16, s * 0.5, s * 0.16, s * 0.5);   // crossbar
  seg(0, s * 0.42, 0, s * 0.95);                // mid prong
  for (const d of [-1, 1]) {                    // side prongs, slight flare
    seg(d * s * 0.16, s * 0.5, d * s * 0.2, s * 0.78);
    seg(d * s * 0.2, s * 0.78, d * s * 0.14, s * 0.9);
  }
  const g = new THREE.BufferGeometry().setFromPoints(pts);
  return new THREE.LineSegments(g, M.ink);
}

/* ─────────────────── the murti, built ────────────────────── */
let murti = null;          // root group
let PARTS = {};            // named part groups (explode + labels + heart-fade)
let D = {};                // resolved datums for readouts/labels
const EXPLODE = { plinth: -0.22, drum: 0, water: 0.42, mound: 0.8, cup: 1.15, collar: 1.5, linga: 1.85, pool: 0 };

function resolve() {
  const s = state, r = s.rings, e = s.elev, n = s.nali;
  const z0 = e.plinthHeight;
  const rimTop = z0 + e.rimHeight;
  const zWL = z0 + e.rimHeight * e.waterlineOverRimHeight;
  // basin stone depth (rim top → floor): the grammar's 9 in = 0.0963 R
  const floorZ = Math.max(z0 + 0.02, rimTop - (e.basinDepth ?? e.rimHeight * 0.86));
  const cupTop = rimTop + e.lotusCupTopAboveRim;
  const collarTop = cupTop + e.collarHeight;
  const lingaTop = cupTop + e.lingaHeightAboveLotus;
  const domeH = Math.min(e.lingaDomeRatio * r.linga, (lingaTop - collarTop) * 0.8);
  const cupOuter = r.cupOuter ?? r.jaladhari + 0.055;
  const moundBaseR = Math.min(r.tier2PetalTip + 0.05, r.waterOuter - 0.03);
  const moundTopZ = Math.max(zWL + 0.03, floorZ + 0.1);
  const gapDeg = 2 * THREE.MathUtils.radToDeg(Math.asin(Math.min(0.95, n.widthOverR / 2)));
  const sillZ = n.style === "slot" ? z0 + 0.02 : zWL - n.sillBelowWaterline;
  const poolDist = 1 + n.lengthBeyondRimOverR + e.poolWidth / 2 + 0.16;
  return { z0, rimTop, zWL, floorZ, cupTop, collarTop, lingaTop, domeH, cupOuter, moundBaseR, moundTopZ, gapDeg, sillZ, poolDist };
}

function disposeDeep(obj) {
  obj.traverse((o) => {
    if (o.geometry) o.geometry.dispose();
    if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose());
  });
}

function buildMurti() {
  if (murti) { scene.remove(murti); disposeDeep(murti); }
  ghostCache.clear();
  M = makeMats();
  murti = new THREE.Group();
  PARTS = {};
  const s = state, r = s.rings, e = s.elev, n = s.nali;
  D = resolve();
  const part = (name) => { const g = new THREE.Group(); g.userData.ex = EXPLODE[name] ?? 0; PARTS[name] = g; murti.add(g); return g; };
  const solid = (parent, profile, opts, mat = M.stone) => {
    const geo = lathe(profile, opts);
    parent.add(new THREE.Mesh(geo, mat));
    if (state.display.wireframe) parent.add(new THREE.Mesh(geo.clone(), M.wire));
  };

  /* plinth */
  const plinth = part("plinth");
  if (e.plinthHeight > 0.005) {
    const gp = n.style === "slot" ? { gapDeg: D.gapDeg, capGap: true } : {};
    solid(plinth, [[1.07, 0], [1.07, D.z0 - 0.015], [1.045, D.z0], [0.9, D.z0], [0.9, 0], [1.07, 0]], gp);
    plinth.add(inkRing(1.07, 0.002, { gapDeg: gp.gapDeg || 0 }));
    plinth.add(inkRing(1.07, D.z0 - 0.015, { gapDeg: gp.gapDeg || 0 }));
  }

  /* drum: outer wall, rim band top, inner wall, basin floor.
     weir mode: solid below the sill, the break only above it (water is held);
     slot mode: the cut runs to the ground — the shivling.png condition. */
  const drum = part("drum");
  const floorInner = Math.max(D.moundBaseR - 0.06, 0.1);
  if (n.style === "slot") {
    solid(drum, [
      [1, D.z0], [1, D.rimTop - 0.012], [0.988, D.rimTop],
      [r.waterOuter + 0.012, D.rimTop], [r.waterOuter, D.rimTop - 0.012],
      [r.waterOuter, D.floorZ + 0.02], [r.waterOuter - 0.02, D.floorZ],
      [floorInner, D.floorZ], [floorInner, D.z0], [1, D.z0],
    ], { gapDeg: D.gapDeg, capGap: true });
  } else {
    const sillZ = D.sillZ;
    solid(drum, [
      [1, D.z0], [1, sillZ],
      [r.waterOuter, sillZ], [r.waterOuter, D.floorZ + 0.02],
      [r.waterOuter - 0.02, D.floorZ], [floorInner, D.floorZ],
      [floorInner, D.z0], [1, D.z0],
    ], {});
    solid(drum, [
      [1, sillZ], [1, D.rimTop - 0.012], [0.988, D.rimTop],
      [r.waterOuter + 0.012, D.rimTop], [r.waterOuter, D.rimTop - 0.012],
      [r.waterOuter, sillZ], [1, sillZ],
    ], { gapDeg: D.gapDeg, capGap: true });
  }
  drum.add(inkRing(1, D.z0 + 0.003, { gapDeg: D.gapDeg }));
  drum.add(inkRing(0.995, D.rimTop, { gapDeg: D.gapDeg }));
  drum.add(inkRing(r.waterOuter + 0.008, D.rimTop, { gapDeg: D.gapDeg }));

  /* medallions — the Ādityas, on the rim band */
  const stations = [];
  const nm = s.counts.medallions;
  for (let k = 0; k < nm; k++) {
    const a = n.stationPolicy === "between" ? (k + 0.5) * (360 / nm) : k * (360 / nm);
    if (n.stationPolicy === "replace" && k === 0) continue; // the ring broken toward the devotee
    stations.push(a);
  }
  for (const aDeg of stations) {
    const a = THREE.MathUtils.degToRad(aDeg);
    const x = r.medallionCenter * Math.sin(a), z = r.medallionCenter * Math.cos(a);
    const mr = r.medallionRadius;
    const g1 = new THREE.TorusGeometry(mr, 0.005, 6, 40); g1.rotateX(Math.PI / 2);
    const g2 = new THREE.TorusGeometry(mr * 0.62, 0.0035, 6, 32); g2.rotateX(Math.PI / 2);
    const g3 = new THREE.CircleGeometry(mr * 0.24, 20); g3.rotateX(-Math.PI / 2);
    for (const gg of [g1, g2, g3]) {
      const mm = new THREE.Mesh(gg, M.gold);
      mm.position.set(x, D.rimTop + 0.004, z);
      drum.add(mm);
    }
  }

  /* nālī — the runnel through the break, the spout past the rim, the stream */
  {
    const halfG = THREE.MathUtils.degToRad(D.gapDeg) / 2;
    const zStart = r.waterOuter - 0.03;
    const zEnd = 1 + n.lengthBeyondRimOverR;
    const w = Math.max(0.03, 2 * zStart * Math.sin(halfG) * 0.92);
    // runnel floor inside the break
    const L1 = 1.005 - zStart, t = 0.028;
    const runnel = new THREE.Mesh(new THREE.BoxGeometry(w, t, L1), M.stone);
    runnel.position.set(0, D.sillZ - t / 2, zStart + L1 / 2);
    drum.add(runnel);
    // spout trough past the rim, dipping gently
    const L2 = n.lengthBeyondRimOverR + 0.02;
    const spout = new THREE.Group();
    const fl = new THREE.Mesh(new THREE.BoxGeometry(w, t, L2), M.stone);
    fl.position.set(0, -t / 2, L2 / 2);
    spout.add(fl);
    for (const d of [-1, 1]) {
      const ch = new THREE.Mesh(new THREE.BoxGeometry(0.013, 0.055, L2), M.stone);
      ch.position.set(d * (w / 2 + 0.0065), 0.014, L2 / 2);
      spout.add(ch);
    }
    spout.position.set(0, D.sillZ, 0.998);
    spout.rotation.x = 0.09;
    drum.add(spout);
    const lipY = D.sillZ - Math.sin(0.09) * L2;
    if (n.stream || n.style === "slot") {
      const poolWaterY = 0.004;
      const len = Math.max(0.05, lipY - poolWaterY);
      const st = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.011, len, 10), M.gold);
      st.position.set(0, lipY - len / 2, zEnd - 0.012);
      drum.add(st);
      const drop = new THREE.Mesh(new THREE.SphereGeometry(0.019, 16, 12), M.gold);
      drop.position.set(0, lipY - len * 0.45, zEnd - 0.012);
      drum.add(drop);
    }
    if (n.trishul) {
      const tri = trishulLines(e.rimHeight * 0.6);
      tri.position.set(0, D.z0 + e.rimHeight * 0.16, r.waterOuter + 0.006);
      drum.add(tri);
    }
  }

  /* water — the held offering (weir mode holds; slot mode cannot) */
  const water = part("water");
  if (n.style !== "slot") {
    const mFrac = THREE.MathUtils.clamp((D.zWL - D.floorZ) / Math.max(D.moundTopZ - D.floorZ, 0.001), 0, 1);
    const innerR = D.moundBaseR + (D.cupOuter - D.moundBaseR) * mFrac;
    const ring = new THREE.RingGeometry(Math.max(innerR, 0.05), r.waterOuter - 0.004, 120, 1);
    ring.rotateX(-Math.PI / 2);
    const wm = new THREE.Mesh(ring, M.water);
    wm.position.y = D.zWL;
    water.add(wm);
    water.add(inkRing(r.waterOuter - 0.006, D.zWL + 0.002, { gapDeg: D.gapDeg, mat: "gold" }));
    // the construct.py echo: a gold dashed accent mid-annulus
    const midR = (r.waterOuter + r.tier2PetalTip) / 2;
    const mpts = [];
    for (let i = 0; i <= 120; i++) {
      const a = (i / 120) * Math.PI * 2;
      mpts.push(new THREE.Vector3(midR * Math.sin(a), D.zWL + 0.0025, midR * Math.cos(a)));
    }
    const mid = new THREE.Line(new THREE.BufferGeometry().setFromPoints(mpts), M.goldDash);
    mid.computeLineDistances();
    water.add(mid);
  }

  /* mound + lower tier */
  const mound = part("mound");
  solid(mound, [
    [D.moundBaseR, D.floorZ], [D.moundBaseR * 0.985, D.floorZ + 0.05],
    [D.cupOuter + 0.015, D.moundTopZ],
  ]);
  mound.add(inkRing(D.moundBaseR, D.floorZ + 0.004));
  {
    // the lower tier: BLOOM below the water, FLATTEN on its surface — an
    // S-spine pad with real slab thickness, tips at the lotus-outer circle.
    // In slot mode (dry) it falls back to straight petals on the mound.
    const t = s.petal.padThickness ?? 0.043;
    if (n.style !== "slot") {
      const r0 = D.cupOuter - 0.005;
      const run = Math.max(0.05, r.tier2PetalTip - r0);
      const zDeep = Math.max(D.floorZ + 0.03, D.zWL - 0.075);
      const q = (a, c, b, u) => [ // quadratic bezier in (r,z)
        (1 - u) * (1 - u) * a[0] + 2 * (1 - u) * u * c[0] + u * u * b[0],
        (1 - u) * (1 - u) * a[1] + 2 * (1 - u) * u * c[1] + u * u * b[1]];
      const P0 = [r0, zDeep], C1 = [r0 + 0.3 * run, D.zWL - 0.006], P2 = [r0 + 0.52 * run, D.zWL + t];
      const C2 = [r0 + 0.85 * run, D.zWL + t + 0.004], P3 = [r.tier2PetalTip, D.zWL + t * 0.6];
      const spine = [];
      for (let i = 0; i <= 5; i++) spine.push(q(P0, C1, P2, i / 5));
      for (let i = 1; i <= 7; i++) spine.push(q(P2, C2, P3, i / 7));
      mound.add(tierGroup(s.counts.petalsLower, s.counts.tierOffsetDeg, {
        spine, thick: t, tip: "point",
        wArc: (Math.PI * r0) / s.counts.petalsLower * 0.94,
        cup: s.petal.cup * 0.35,
      }, M.stone));
    } else {
      const baseZ = D.floorZ + (D.moundTopZ - D.floorZ) * 0.55;
      const mFrac = THREE.MathUtils.clamp((baseZ - D.floorZ) / Math.max(D.moundTopZ - D.floorZ, 0.001), 0, 1);
      const baseR = (D.moundBaseR + (D.cupOuter + 0.015 - D.moundBaseR) * mFrac) + 0.005;
      const tilt = THREE.MathUtils.degToRad(s.petal.tiltLowerDeg);
      const len = Math.max(0.08, (r.tier2PetalTip - baseR) / Math.max(Math.sin(tilt), 0.35));
      mound.add(tierGroup(s.counts.petalsLower, s.counts.tierOffsetDeg, {
        baseR, baseZ, len, tiltDeg: s.petal.tiltLowerDeg,
        wArc: (Math.PI * baseR) / s.counts.petalsLower * 0.94,
        belly: s.petal.belly, cup: s.petal.cup * 0.6,
      }, M.stone));
    }
  }

  /* cup + upper tier */
  const cup = part("cup");
  solid(cup, [
    [D.cupOuter, D.moundTopZ - 0.02], [D.cupOuter, D.cupTop - 0.02],
    [D.cupOuter * 0.985, D.cupTop], [r.jaladhari, D.cupTop],
  ]);
  cup.add(inkRing(D.cupOuter * 0.99, D.cupTop, {}));
  {
    // the founder's equality law (supersedes 19+19): THE BUDS RISE EXACTLY AS
    // FAR AS THE PADS REACH — bud height = pad run (tier2 − cup wall). Tip
    // pinned to (tier1PetalTip, cupTop): never above the cup lip, and clamped
    // so the buds never drown in the pads (a warning fires instead).
    const padTop = D.zWL + (s.petal.padThickness ?? 0.043);
    const padRun = Math.max(0.05, r.tier2PetalTip - (D.cupOuter - 0.005));
    const low = n.style !== "slot" ? padTop + 0.012 : D.moundTopZ - 0.05;
    const baseZ = THREE.MathUtils.clamp(D.cupTop - padRun, low, D.cupTop - 0.08);
    const baseR = D.cupOuter - 0.012; // tucked into the cup wall
    const dr = Math.max(0.02, r.tier1PetalTip - baseR);
    const dz = Math.max(0.06, D.cupTop - baseZ);
    const tiltDeg = THREE.MathUtils.radToDeg(Math.atan2(dr, dz));
    const len = Math.hypot(dr, dz);
    D.tier1TipZ = D.cupTop;
    cup.add(tierGroup(s.counts.petalsUpper, 0, {
      baseR, baseZ, len, tiltDeg, tip: "round",
      wArc: (Math.PI * baseR) / s.counts.petalsUpper * 0.99,
      belly: s.petal.belly, cup: s.petal.cup,
    }, M.stone));
  }

  /* collar (jaladhārī throat) */
  const collar = part("collar");
  const collarOuter = (r.jaladhari + r.linga) / 2 + 0.02;
  if (e.collarHeight > 0.004) {
    solid(collar, [
      [collarOuter, D.cupTop], [collarOuter, D.collarTop - 0.015],
      [collarOuter * 0.965, D.collarTop], [r.linga + 0.004, D.collarTop],
    ]);
    collar.add(inkRing(collarOuter * 0.985, D.collarTop, {}));
    // mekhalā — the molded ring where the liṅga meets its seat (GLB reference)
    const mk = new THREE.Mesh(new THREE.TorusGeometry(r.linga + 0.006, 0.009, 10, 80), M.stone);
    mk.rotation.x = Math.PI / 2;
    mk.position.y = D.collarTop + 0.006;
    collar.add(mk);
  }

  /* linga */
  const linga = part("linga");
  {
    const prof = [[r.linga, D.collarTop - 0.06]];
    const domeBase = D.lingaTop - D.domeH;
    prof.push([r.linga, domeBase]);
    for (let i = 1; i <= 20; i++) {
      const a = (i / 20) * Math.PI * 0.5;
      prof.push([r.linga * Math.cos(a), domeBase + D.domeH * Math.sin(a)]);
    }
    solid(linga, prof, { seg: 120 }, M.linga);
  }

  /* pool — the offering returned, toward the devotee. Drawn flush in the
     pavement (plan-style): stone margin, ink edge, gold water square. */
  const pool = part("pool");
  {
    const w = e.poolWidth;
    const margin = new THREE.Mesh(new THREE.PlaneGeometry(w * 1.14, w * 1.14), M.poolIn);
    margin.rotation.x = -Math.PI / 2;
    margin.position.set(0, 0.002, D.poolDist);
    pool.add(margin);
    const wp = new THREE.Mesh(new THREE.PlaneGeometry(w * 0.92, w * 0.92), M.water);
    wp.rotation.x = -Math.PI / 2;
    wp.position.set(0, 0.0035, D.poolDist);
    pool.add(wp);
    const sqAt = (k, y) => [[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]].map(([a, b]) =>
      new THREE.Vector3((a * w * k) / 2, y, D.poolDist + (b * w * k) / 2));
    pool.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(sqAt(1, 0.005)), M.ink));
    pool.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(sqAt(1.14, 0.004)), M.inkSoft));
    pool.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(sqAt(0.92, 0.006)), M.goldLine));
  }

  /* contact shadow */
  {
    const cnv = document.createElement("canvas");
    cnv.width = cnv.height = 256;
    const ctx = cnv.getContext("2d");
    const gr = ctx.createRadialGradient(128, 128, 30, 128, 128, 128);
    gr.addColorStop(0, "rgba(26,26,26,0.36)");
    gr.addColorStop(0.7, "rgba(26,26,26,0.12)");
    gr.addColorStop(1, "rgba(26,26,26,0)");
    ctx.fillStyle = gr; ctx.fillRect(0, 0, 256, 256);
    const tex = new THREE.CanvasTexture(cnv);
    const sh = new THREE.Mesh(new THREE.CircleGeometry(1.52, 48),
      new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }));
    sh.rotation.x = -Math.PI / 2;
    sh.position.y = 0.0012;
    murti.add(sh);
  }

  /* construction guides — the ring table, each circle drawn at the height
     where its radius lives (a measured drawing, not a floor decal) */
  const guides = new THREE.Group();
  guides.visible = state.display.guides;
  const guideAt = {
    linga: D.collarTop + 0.03, jaladhari: D.cupTop + 0.025,
    tier1PetalTip: (D.tier1TipZ || D.cupTop) + 0.012, tier2PetalTip: D.zWL + 0.012,
    waterOuter: D.zWL + 0.012, medallionCenter: D.rimTop + 0.012,
  };
  for (const [key, y] of Object.entries(guideAt)) guides.add(guideCircle(r[key], y));
  guides.add(guideCircle(1.0));
  for (let k = 0; k < 12; k++) {
    const a = (k * Math.PI) / 6;
    const p = [new THREE.Vector3(r.linga * Math.sin(a), 0.004, r.linga * Math.cos(a)),
      new THREE.Vector3(1.06 * Math.sin(a), 0.004, 1.06 * Math.cos(a))];
    const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints(p), M.guide);
    l.computeLineDistances();
    guides.add(l);
  }
  PARTS.guides = guides;
  murti.add(guides);

  /* the measures — the locked triad (Ø187 · 169 · Ø58) as dimension lines */
  {
    const mg = new THREE.Group();
    mg.visible = !!state.display.measures;
    const seg = (a, b) => new THREE.Line(new THREE.BufferGeometry().setFromPoints(
      [new THREE.Vector3(...a), new THREE.Vector3(...b)]), M.goldLine);
    const zd = 1.24, xd = -1.24, yl = D.lingaTop + 0.12;
    mg.add(seg([-1, 0.012, zd], [1, 0.012, zd]));                    // Ø 187
    mg.add(seg([-1, 0.012, zd - 0.045], [-1, 0.012, zd + 0.045]));
    mg.add(seg([1, 0.012, zd - 0.045], [1, 0.012, zd + 0.045]));
    for (const x of [-1, 1]) mg.add(seg([x, 0.012, zd], [x, 0.012, 1.0]));
    mg.add(seg([xd, 0, 0], [xd, D.lingaTop, 0]));                    // 169
    mg.add(seg([xd - 0.045, 0, 0], [xd + 0.045, 0, 0]));
    mg.add(seg([xd - 0.045, D.lingaTop, 0], [xd + 0.045, D.lingaTop, 0]));
    mg.add(seg([xd, D.lingaTop, 0], [-r.linga, D.lingaTop, 0]));
    mg.add(seg([-r.linga, yl, 0], [r.linga, yl, 0]));                // Ø 58
    mg.add(seg([-r.linga, yl, 0], [-r.linga, yl - 0.07, 0]));
    mg.add(seg([r.linga, yl, 0], [r.linga, yl - 0.07, 0]));
    PARTS.measures = mg;
    murti.add(mg);
  }

  /* the axis, gold — visible when exploded */
  {
    const ax = new THREE.Group();
    const pts = [];
    for (let y = -0.05; y < D.lingaTop + 2.6; y += 0.075)
      pts.push(new THREE.Vector3(0, y, 0), new THREE.Vector3(0, y + 0.028, 0));
    ax.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts), M.goldLine));
    const bindu = new THREE.Mesh(new THREE.SphereGeometry(0.024, 16, 12), M.gold);
    bindu.position.y = D.lingaTop + EXPLODE.linga + 0.32;
    ax.add(bindu);
    ax.visible = false;
    PARTS.axis = ax;
    murti.add(ax);
  }

  scene.add(murti);
  applyExplode();
  applyHeartFade();
  reframe();
  dirty = true;
}

/* ─────────────────── explode + labels ────────────────────── */
let explodeT = 0;
const lblHost = [];
function applyExplode() {
  for (const [name, g] of Object.entries(PARTS)) {
    if (name === "guides" || name === "axis") continue;
    g.position.y = (g.userData.ex || 0) * explodeT;
  }
  if (PARTS.axis) PARTS.axis.visible = explodeT > 0.03;
  if (PARTS.measures) PARTS.measures.visible = !!state.display.measures && explodeT < 0.04;
  rebuildLabels();
  reframe();
  dirty = true;
}

function labelDefs() {
  const s = state, c = s.counts;
  const petSum = c.petalsUpper + c.petalsLower;
  const nmShown = s.nali.stationPolicy === "replace" ? c.medallions - 1 : c.medallions;
  return [
    { part: "linga", en: "the drop — bindu", hi: "बिन्दु", at: [0.09, D.lingaTop + 0.34, 0] , ex: EXPLODE.linga },
    { part: "linga", en: "liṅga — the witness", hi: "पुरुषः", at: [state.rings.linga + 0.05, (D.collarTop + D.lingaTop) / 2, 0], ex: EXPLODE.linga },
    { part: "collar", en: "jaladhārī throat", hi: "जलधारी", at: [state.rings.jaladhari + 0.06, (D.cupTop + D.collarTop) / 2, 0], ex: EXPLODE.collar, skip: state.elev.collarHeight <= 0.004 },
    { part: "cup", en: `upper tier — ${c.petalsUpper}`, hi: "द्वादश", at: [state.rings.tier1PetalTip + 0.07, D.cupTop, 0], ex: EXPLODE.cup },
    { part: "mound", en: `lower tier — ${c.petalsLower} · ${petSum} tattvas`, hi: "चतुर्विंशति", at: [state.rings.tier2PetalTip + 0.06, D.floorZ + 0.1, 0], ex: EXPLODE.mound },
    { part: "water", en: "the held offering", hi: "जलम्", at: [-(state.rings.waterOuter - 0.1), D.zWL + 0.02, 0.1], ex: EXPLODE.water, skip: state.nali.style === "slot" },
    { part: "drum", en: `${nmShown} Ādityas on the rim`, hi: "आदित्याः", at: [-(state.rings.medallionCenter * 0.7), D.rimTop + 0.02, -state.rings.medallionCenter * 0.6], ex: 0 },
    { part: "drum", en: "nālī — the one break", hi: "नाली", at: [0.06, D.sillZ, 1 + state.nali.lengthBeyondRimOverR], ex: 0 },
    { part: "pool", en: "returned to the world", hi: "लोकाय", at: [0.06, 0.03, D.poolDist], ex: 0 },
  ].filter((d) => !d.skip);
}
function measureDefs() {
  return [
    { en: "Ø 187 — the field · 7", at: [0.52, 0.06, 1.28], ex: 0 },
    { en: "169 — the whole · 7", at: [-1.28, (D.lingaTop || 1.6) * 0.55, 0], ex: 0 },
    { en: "Ø 58 — the liṅga · 4", at: [0, (D.lingaTop || 1.6) + 0.2, 0], ex: 0 },
  ];
}
function rebuildLabels() {
  for (const l of lblHost) l.el.remove();
  lblHost.length = 0;
  const defs = [];
  if (explodeT >= 0.04) defs.push(...labelDefs());
  if (state.display.measures && explodeT < 0.04) defs.push(...measureDefs());
  if (!defs.length) { dirty = true; return; }
  for (const d of defs) {
    const el = document.createElement("div");
    el.className = "lbl";
    el.innerHTML = d.hi ? `${d.en}<span class="hi">${d.hi}</span>` : d.en;
    document.body.appendChild(el);
    lblHost.push({ el, def: d });
  }
  dirty = true;
}
const _v = new THREE.Vector3();
function placeLabels() {
  for (const { el, def } of lblHost) {
    _v.set(def.at[0], def.at[1] + (def.ex || 0) * explodeT, def.at[2]).applyMatrix4(murti.matrixWorld);
    _v.project(activeCam());
    if (_v.z > 1 || Math.abs(_v.x) > 1.15 || Math.abs(_v.y) > 1.15) { el.style.display = "none"; continue; }
    el.style.display = "flex";
    el.style.left = `${((_v.x + 1) / 2) * innerWidth + 10}px`;
    el.style.top = `${((1 - _v.y) / 2) * innerHeight - 8}px`;
  }
}

/* ─────────────────── heart-view fade ─────────────────────── */
// §3.3 — tighten to the lotus alone: the outer world steps back, the
// lotus and the hub stay crisp. Ghost materials are swapped per mesh so
// shared stone material never leaks the fade onto the lotus itself.
let heartMode = false;
const ghostCache = new Map();
function ghostOf(mat) {
  if (!ghostCache.has(mat.uuid)) {
    const g = mat.clone();
    g.transparent = true;
    g.opacity = 0.09;
    g.depthWrite = false;
    ghostCache.set(mat.uuid, g);
  }
  return ghostCache.get(mat.uuid);
}
function applyHeartFade() {
  const dim = ["drum", "plinth", "pool", "water"];
  for (const name of dim) {
    const g = PARTS[name];
    if (!g) continue;
    g.traverse((o) => {
      if (!o.material) return;
      if (heartMode) {
        if (!o.userData.savedMat) { o.userData.savedMat = o.material; o.material = ghostOf(o.material); }
      } else if (o.userData.savedMat) {
        o.material = o.userData.savedMat;
        delete o.userData.savedMat;
      }
    });
  }
  dirty = true;
}

/* ─────────────────── camera + controls ───────────────────── */
// Views frame the CURRENT murti: distance and target scale with its height
// (the image preset stands a full R taller than the codified one).
let activeView = "study";
function VIEWS() {
  const H = (D.lingaTop || 1.56) + explodeT * 2.1;
  const k = Math.max(1, H / 1.58);
  return {
    study: { az: -33, el: 21, dist: 4.7 * k, ty: H * 0.36 },
    front: { az: 0, el: 9, dist: 5.0 * k, ty: H * 0.37 },
    wheel: { az: 0, el: 88, dist: 4.5 + explodeT * 2.1, ty: 0 },
    heart: { az: 0, el: 88, dist: H + 2.2, ty: 0 },
  };
}
const cam = { az: -33, el: 21, dist: 4.7, ty: 0.55 };
let tween = null;
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
function applyCam() {
  const phi = THREE.MathUtils.degToRad(90 - cam.el);
  const th = THREE.MathUtils.degToRad(cam.az);
  camera.position.set(
    cam.dist * Math.sin(phi) * Math.sin(th),
    cam.ty + cam.dist * Math.cos(phi),
    cam.dist * Math.sin(phi) * Math.cos(th),
  );
  camera.lookAt(0, cam.ty, 0);
  ocam.position.copy(camera.position);
  const halfH = cam.dist * Math.tan(THREE.MathUtils.degToRad(16));
  const halfW = halfH * camera.aspect;
  ocam.left = -halfW; ocam.right = halfW; ocam.top = halfH; ocam.bottom = -halfH;
  ocam.updateProjectionMatrix();
  ocam.lookAt(0, cam.ty, 0);
  dirty = true;
}
function flyTo(view) {
  const to = VIEWS()[view];
  if (!to) return;
  activeView = view;
  useOrtho = view !== "study";
  heartMode = view === "heart";
  applyHeartFade();
  if (reduceMotion) { Object.assign(cam, to); applyCam(); return; }
  tween = { t0: performance.now(), dur: 650, from: { ...cam }, to: { ...to } };
}
// keep a named view framed when the murti's height or explode changes
function reframe() {
  if (!activeView) return;
  const to = VIEWS()[activeView];
  if (tween) { tween.to = { ...to }; return; }
  Object.assign(cam, to);
  applyCam();
}
let dragging = false, lastX = 0, lastY = 0, pinch0 = 0;
stage.addEventListener("pointerdown", (ev) => {
  dragging = true; lastX = ev.clientX; lastY = ev.clientY;
  stage.classList.add("dragging"); stage.setPointerCapture(ev.pointerId);
  activeView = null;
  useOrtho = false;
  setActiveView(null);
});
stage.addEventListener("pointermove", (ev) => {
  if (!dragging) return;
  cam.az -= (ev.clientX - lastX) * 0.35;
  cam.el = THREE.MathUtils.clamp(cam.el + (ev.clientY - lastY) * 0.3, -4, 89);
  lastX = ev.clientX; lastY = ev.clientY;
  tween = null; applyCam();
});
stage.addEventListener("pointerup", (ev) => { dragging = false; stage.classList.remove("dragging"); });
stage.addEventListener("wheel", (ev) => {
  ev.preventDefault();
  cam.dist = THREE.MathUtils.clamp(cam.dist * Math.exp(ev.deltaY * 0.0011), 1.4, 10);
  tween = null; applyCam();
}, { passive: false });
stage.addEventListener("dblclick", () => flyTo("study"));
stage.addEventListener("touchmove", (ev) => {
  if (ev.touches.length === 2) {
    const d = Math.hypot(ev.touches[0].clientX - ev.touches[1].clientX, ev.touches[0].clientY - ev.touches[1].clientY);
    if (pinch0) { cam.dist = THREE.MathUtils.clamp(cam.dist * (pinch0 / d), 1.4, 10); applyCam(); }
    pinch0 = d;
  }
}, { passive: true });
stage.addEventListener("touchend", () => { pinch0 = 0; });

let autorotate = false;

/* ─────────────────── render loop ─────────────────────────── */
let dirty = true;
function resize() {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  applyCam();
  dirty = true;
}
addEventListener("resize", resize);
resize();
applyCam();

let frames = 0;
function loop(now) {
  requestAnimationFrame(loop);
  if (tween) {
    let k = (now - tween.t0) / tween.dur;
    if (k >= 1) { k = 1; }
    const e = 1 - Math.pow(1 - k, 3);
    for (const p of ["az", "el", "dist", "ty"]) cam[p] = tween.from[p] + (tween.to[p] - tween.from[p]) * e;
    if (k === 1) tween = null;
    applyCam();
  }
  if (autorotate) { cam.az += 0.12; applyCam(); }
  if (dirty || lblHost.length) {
    renderer.render(scene, activeCam());
    placeLabels();
    if (!lblHost.length) dirty = false;
    frames++;
  }
}
requestAnimationFrame(loop);

/* ─────────────────── the instrument panel ────────────────── */
const $ = (q) => document.querySelector(q);
const getPath = (o, p) => p.split(".").reduce((a, k) => a[k], o);
const setPath = (o, p, v) => { const ks = p.split("."); ks.slice(0, -1).reduce((a, k) => a[k], o)[ks.at(-1)] = v; };

const ROWS = [
  { g: "counts", p: "counts.medallions", l: "Medallions — Ādityas", min: 6, max: 18, step: 1 },
  { g: "counts", p: "counts.petalsUpper", l: "Petals, upper tier", min: 8, max: 36, step: 1 },
  { g: "counts", p: "counts.petalsLower", l: "Petals, lower tier", min: 8, max: 36, step: 1 },
  { g: "counts", p: "counts.tierOffsetDeg", l: "Tier offset °", min: 0, max: 30, step: 0.5 },
  { g: "rings", p: "rings.linga", l: "Liṅga radius", min: 0.12, max: 0.36, step: 0.005 },
  { g: "rings", p: "rings.jaladhari", l: "Jaladhārī throat", min: 0.2, max: 0.48, step: 0.005 },
  { g: "rings", p: "rings.cupOuter", l: "Cup outer (Ø92 ring)", min: 0.36, max: 0.56, step: 0.005 },
  { g: "rings", p: "rings.tier1PetalTip", l: "Upper petal tips", min: 0.34, max: 0.62, step: 0.005 },
  { g: "rings", p: "rings.tier2PetalTip", l: "Lower petal tips", min: 0.45, max: 0.78, step: 0.005 },
  { g: "rings", p: "rings.waterOuter", l: "Water outer edge", min: 0.68, max: 0.93, step: 0.005 },
  { g: "rings", p: "rings.medallionCenter", l: "Medallion centres", min: 0.86, max: 0.975, step: 0.005 },
  { g: "rings", p: "rings.medallionRadius", l: "Medallion radius", min: 0.02, max: 0.07, step: 0.002 },
  { g: "elev", p: "elev.rimHeight", l: "Rim height", min: 0.28, max: 0.85, step: 0.01 },
  { g: "elev", p: "elev.waterlineOverRimHeight", l: "Waterline (of rim)", min: 0.45, max: 0.97, step: 0.01 },
  { g: "elev", p: "elev.basinDepth", l: "Basin depth (stone)", min: 0.05, max: 0.45, step: 0.005 },
  { g: "elev", p: "elev.lotusCupTopAboveRim", l: "Cup top above rim", min: 0.05, max: 0.4, step: 0.005 },
  { g: "elev", p: "elev.lingaHeightAboveLotus", l: "Liṅga above lotus", min: 0.5, max: 1.75, step: 0.01 },
  { g: "elev", p: "elev.collarHeight", l: "Collar height", min: 0, max: 0.32, step: 0.005 },
  { g: "elev", p: "elev.lingaDomeRatio", l: "Crown fullness", min: 0.6, max: 1.5, step: 0.02 },
  { g: "elev", p: "elev.plinthHeight", l: "Plinth height", min: 0, max: 0.28, step: 0.005 },
  { g: "elev", p: "elev.poolWidth", l: "Pool width", min: 0.3, max: 0.85, step: 0.01 },
  { g: "nali", p: "nali.widthOverR", l: "Channel width", min: 0.08, max: 0.3, step: 0.005 },
  { g: "nali", p: "nali.lengthBeyondRimOverR", l: "Spout past rim", min: 0.04, max: 0.3, step: 0.005 },
  { g: "nali", p: "nali.sillBelowWaterline", l: "Sill below waterline", min: 0.01, max: 0.14, step: 0.005 },
  { g: "nali", p: "nali.style", l: "Break", type: "select", opts: [["weir", "weir at waterline (holds water)"], ["slot", "full slot to ground (as image)"]] },
  { g: "nali", p: "nali.stationPolicy", l: "Station", type: "select", opts: [["replace", "channel takes the front station"], ["between", "channel between stations"]] },
  { g: "nali", p: "nali.trishul", l: "Trishul (un-codified)", type: "check" },
  { g: "nali", p: "nali.stream", l: "Falling stream", type: "check" },
  { g: "petal", p: "petal.padThickness", l: "Pad thickness", min: 0.01, max: 0.09, step: 0.002 },
  { g: "petal", p: "petal.tiltLowerDeg", l: "Lower tilt ° (dry mode)", min: 40, max: 87, step: 1 },
  { g: "petal", p: "petal.belly", l: "Belly", min: 0.15, max: 0.95, step: 0.01 },
  { g: "petal", p: "petal.cup", l: "Cupping", min: 0.1, max: 0.95, step: 0.01 },
  { g: "display", p: "display.measures", l: "The measures — 187 · 169 · 58", type: "check" },
  { g: "display", p: "display.guides", l: "Construction rings", type: "check" },
  { g: "display", p: "display.wireframe", l: "Mesh (wireframe)", type: "check" },
  { g: "display", p: "display.material", l: "Stone", type: "select", opts: [["canon", "canon — charcoal liṅga"], ["stone", "one pale stone (as image)"]] },
];

let rebuildTimer = 0;
function scheduleRebuild() {
  clearTimeout(rebuildTimer);
  rebuildTimer = setTimeout(() => { buildMurti(); refreshText(); persist(); }, 55);
}

const inputs = new Map();
function buildRows() {
  for (const row of ROWS) {
    const host = document.getElementById(`g-${row.g}`);
    const div = document.createElement("div");
    div.className = "row";
    const id = `in-${row.p.replace(/\./g, "-")}`;
    if (row.type === "select") {
      div.innerHTML = `<label for="${id}">${row.l}</label>`;
      const sel = document.createElement("select");
      sel.id = id;
      for (const [v, t] of row.opts) sel.add(new Option(t, v));
      sel.value = String(getPath(state, row.p));
      sel.addEventListener("change", () => { setPath(state, row.p, sel.value); onEdit(); });
      div.appendChild(sel);
      inputs.set(row.p, () => { sel.value = String(getPath(state, row.p)); });
    } else if (row.type === "check") {
      div.innerHTML = `<label for="${id}">${row.l}</label>`;
      const cb = document.createElement("input");
      cb.type = "checkbox"; cb.id = id;
      cb.checked = !!getPath(state, row.p);
      cb.addEventListener("change", () => { setPath(state, row.p, cb.checked); onEdit(); });
      div.appendChild(cb);
      inputs.set(row.p, () => { cb.checked = !!getPath(state, row.p); });
    } else {
      div.innerHTML = `<label for="${id}">${row.l}</label>`;
      const sl = document.createElement("input");
      sl.type = "range"; sl.id = id; sl.min = row.min; sl.max = row.max; sl.step = row.step;
      sl.value = getPath(state, row.p);
      const val = document.createElement("span");
      val.className = "val";
      const fmt = (v) => (row.step >= 1 ? String(Math.round(v)) : (+v).toFixed(row.step < 0.01 ? 3 : 2));
      val.textContent = fmt(sl.value);
      sl.addEventListener("input", () => {
        setPath(state, row.p, row.step >= 1 ? parseInt(sl.value, 10) : parseFloat(sl.value));
        val.textContent = fmt(sl.value);
        markDeviation(div, row);
        onEdit();
      });
      div.appendChild(sl); div.appendChild(val);
      inputs.set(row.p, () => { sl.value = getPath(state, row.p); val.textContent = fmt(sl.value); markDeviation(div, row); });
    }
    markDeviation(div, row);
    host.appendChild(div);
  }
}
function markDeviation(div, row) {
  const canonV = getPath(CANON, row.p);
  const v = getPath(state, row.p);
  const dev = typeof v === "number" ? Math.abs(v - canonV) > (row.step || 0.001) * 0.51 : v !== canonV;
  div.classList.toggle("dev", !!dev);
}
function refreshInputs() { for (const fn of inputs.values()) fn(); }

function onEdit() {
  $("#presetflag").textContent = presetName();
  scheduleRebuild();
}
function presetName() {
  const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const bare = deep(state); // display prefs don't decide the preset
  for (const [name, preset] of [["codified", CANON], ["grammar 7·1·4·2", GRAMMAR_PRESET], ["as shivling.png", IMAGE_PRESET]]) {
    bare.display = preset.display;
    if (eq(bare, deep(preset))) return name;
  }
  return "custom";
}

/* readouts + deviations + chips */
function readouts() {
  const s = state, r = s.rings, e = s.elev;
  const totalH = e.plinthHeight + e.rimHeight + e.lotusCupTopAboveRim + e.lingaHeightAboveLotus;
  const visH = e.lingaHeightAboveLotus - e.collarHeight;
  const hd = visH / (2 * r.linga);
  const annulus = r.waterOuter - r.tier2PetalTip;
  const cup = r.cupOuter ?? r.jaladhari + 0.055;
  const di = (v) => Math.round(v * 187); // grammar scale: Ø in inches (R = 93.5)
  const bi = (a, b) => (((b - a) * 93.5).toFixed(1)).replace(/\.0$/, "");
  return [
    ["Total height ÷ basin width", (totalH / 2).toFixed(2)],
    ["Liṅga visible h : d", hd.toFixed(2)],
    ["Liṅga d ÷ basin width", (r.linga).toFixed(2)],
    ["Water annulus width", annulus.toFixed(2) + " R"],
    ["Rim band width", (1 - r.waterOuter).toFixed(2) + " R"],
    ["Wheel step", (360 / s.counts.medallions).toFixed(1) + "°"],
    ["Tattvas (petals, both tiers)", String(s.counts.petalsUpper + s.counts.petalsLower)],
    ["Pad run = bud rise (the fold)", `${bi(cup - 0.005, r.tier2PetalTip)} in`],
    ["Ø in — liṅga · collar · cup", `${di(r.linga)} · ${di(r.jaladhari)} · ${di(cup)}`],
    ["Ø in — tips · lotus · water · rim", `${di(r.tier1PetalTip)} · ${di(r.tier2PetalTip)} · ${di(r.waterOuter)} · 187`],
    ["Bands in — petal · water · rim", `${bi(cup, r.tier2PetalTip)} · ${bi(r.tier2PetalTip, r.waterOuter)} · ${bi(r.waterOuter, 1)}`],
  ];
}
function deviations() {
  const s = state, out = [];
  const c = s.counts;
  if (c.medallions !== 12) out.push(`Ādityas ≠ 12 (${c.medallions}) — the year loses its stations`);
  if (c.petalsUpper !== 12) out.push(`upper tier ≠ 12 (${c.petalsUpper}) — the wheel loses its spokes`);
  if (c.petalsUpper + c.petalsLower !== 24) out.push(`tattvas ≠ 24 (${c.petalsUpper + c.petalsLower}) — Sāṅkhya broken`);
  if (Math.abs(c.tierOffsetDeg - 15) > 0.26) out.push(`tier offset ≠ 15° (${c.tierOffsetDeg}°) — the half-step lost`);
  if (s.nali.style === "slot") out.push("channel cut to the ground — the basin cannot hold water as drawn (the shivling.png condition)");
  else if (s.elev.waterlineOverRimHeight * s.elev.rimHeight < 0.02) out.push("waterline at the floor — the offering is not held");
  if (s.rings.waterOuter - s.rings.tier2PetalTip < 0.12) out.push("water annulus pinched — the reading of stillness is lost");
  if (s.nali.trishul) out.push("trishul on the nālī — un-codified motif, for the founder + lineage (D1)");
  const cupR = s.rings.cupOuter ?? s.rings.jaladhari + 0.055;
  {
    // the equality law needs air: bud base (cupTop − padRun) must clear the pads
    const zwl = s.elev.plinthHeight + s.elev.rimHeight * s.elev.waterlineOverRimHeight;
    const cupTop = s.elev.plinthHeight + s.elev.rimHeight + s.elev.lotusCupTopAboveRim;
    const padTop = zwl + (s.petal.padThickness ?? 0.043);
    if (s.nali.style !== "slot" && cupTop - (s.rings.tier2PetalTip - cupR + 0.005) < padTop + 0.01)
      out.push("the buds drown in the pads — raise the cup top, or shorten the pad run (lotus outer − cup)");
  }
  if (!(s.rings.jaladhari < cupR && cupR < s.rings.tier1PetalTip
        && s.rings.tier1PetalTip < s.rings.tier2PetalTip && s.rings.tier2PetalTip < s.rings.waterOuter))
    out.push("rings out of order — throat inside cup, cup inside tips, tiers inside the water, water inside the rim");
  for (const k of ["linga", "jaladhari", "tier1PetalTip", "tier2PetalTip", "waterOuter"]) {
    const d = state.rings[k] - CANON.rings[k];
    if (Math.abs(d) > 0.02) out.push(`${k} ${d > 0 ? "+" : ""}${d.toFixed(2)} R off grid.json`);
  }
  const dh = state.elev.lingaHeightAboveLotus - CANON.elev.lingaHeightAboveLotus;
  if (Math.abs(dh) > 0.03) out.push(`liṅga height ${dh > 0 ? "+" : ""}${dh.toFixed(2)} R off grid.json`);
  return out;
}
function refreshText() {
  $("#rolist").innerHTML = readouts().map(([k, v]) => `<div class="ro"><span>${k}</span><b>${v}</b></div>`).join("");
  const devs = deviations();
  $("#devlist").innerHTML = devs.length
    ? devs.map((d) => `<div class="d">◈ ${d}</div>`).join("")
    : `<div class="d ok">holds the canon — 12 · 12+12 · 15° · water held · one break</div>`;
  const chips = [];
  if (state.nali.stationPolicy === "replace")
    chips.push({ note: true, text: "the ring broken toward the devotee — the channel takes the front station, as the door takes a window's place on the temple" });
  for (const d of devs.slice(0, 3)) chips.push({ text: d });
  $("#chips").innerHTML = chips.map((c) => `<div class="chip${c.note ? " note" : ""}">${c.note ? "" : "<b>◈ </b>"}${c.text}</div>`).join("");
  $("#presetflag").textContent = presetName();
}

/* presets */
const PRESETS = { codified: CANON, grammar: GRAMMAR_PRESET, image: IMAGE_PRESET };
for (const btn of document.querySelectorAll("#presets button")) {
  btn.addEventListener("click", () => {
    state = deep(PRESETS[btn.dataset.preset] || CANON);
    refreshInputs(); buildMurti(); refreshText(); persist();
  });
}

/* readings */
function setActiveView(v) {
  for (const b of document.querySelectorAll("#readings button[data-view]"))
    b.classList.toggle("on", b.dataset.view === v);
}
for (const btn of document.querySelectorAll("#readings button")) {
  btn.addEventListener("click", () => {
    const v = btn.dataset.view;
    if (v === "turn") {
      autorotate = !autorotate;
      btn.classList.toggle("on", autorotate);
      btn.setAttribute("aria-pressed", String(autorotate));
      return;
    }
    setActiveView(v);
    flyTo(v);
  });
}

/* explode slider */
$("#explode").addEventListener("input", (ev) => {
  explodeT = parseFloat(ev.target.value);
  applyExplode();
});

/* panel toggle */
$("#panel-toggle").addEventListener("click", () => document.body.classList.toggle("panel-closed"));

/* ─────────────────── drawer: prompt + json ───────────────── */
function currentJSON() {
  const s = state, r4 = (x) => Math.round(x * 10000) / 10000;
  const rings = {}; for (const [k, v] of Object.entries(s.rings)) rings[k] = r4(v);
  rings.rimOuter = 1.0;
  return JSON.stringify({
    $comment: "The Murti, Measured — working numbers (grid.json convention: rim outer radius = 1.0). Feed back into brand/iconography/geometry/grid.json once agreed.",
    counts: {
      medallions: s.counts.medallions,
      // petalsPerTier is what construct.py reads — emitted when the tiers agree
      ...(s.counts.petalsUpper === s.counts.petalsLower ? { petalsPerTier: s.counts.petalsUpper } : {}),
      petalsUpper: s.counts.petalsUpper, petalsLower: s.counts.petalsLower,
      tiers: 2, tattvas: s.counts.petalsUpper + s.counts.petalsLower,
    },
    anglesDeg: { spoke: r4(360 / s.counts.medallions), tierOffset: s.counts.tierOffsetDeg },
    rings,
    nali: {
      widthOverR: r4(s.nali.widthOverR), lengthBeyondRimOverR: r4(s.nali.lengthBeyondRimOverR),
      orientationDeg: 90, sillBelowWaterline: r4(s.nali.sillBelowWaterline),
      style: s.nali.style, stationPolicy: s.nali.stationPolicy, trishul: s.nali.trishul,
    },
    elevation: {
      rimHeight: r4(s.elev.rimHeight), waterlineOverRimHeight: r4(s.elev.waterlineOverRimHeight),
      lotusCupTopAboveRim: r4(s.elev.lotusCupTopAboveRim), lingaHeightAboveLotus: r4(s.elev.lingaHeightAboveLotus),
      poolWidth: r4(s.elev.poolWidth), poolDepth: r4(s.elev.poolDepth),
    },
    murti3d: {
      collarHeight: r4(s.elev.collarHeight), lingaDomeRatio: r4(s.elev.lingaDomeRatio),
      plinthHeight: r4(s.elev.plinthHeight), petal: { ...s.petal },
    },
  }, null, 2);
}

function buildPrompt() {
  const s = state, r = s.rings, e = s.elev, c = s.counts;
  const totalH = e.plinthHeight + e.rimHeight + e.lotusCupTopAboveRim + e.lingaHeightAboveLotus;
  const hd = (e.lingaHeightAboveLotus - e.collarHeight) / (2 * r.linga);
  const nmShown = s.nali.stationPolicy === "replace" ? `${c.medallions - 1} medallions — the front station is taken by the spout channel, the one deliberate break in the wheel` : `${c.medallions} medallions, the spout channel passing between two of them`;
  const water = s.nali.style === "weir"
    ? `The basin is visibly FULL of still water: the water surface sits at ${Math.round(e.waterlineOverRimHeight * 100)}% of the rim height, clearly contained by the raised rim. The spout breaks the rim exactly at the waterline (a weir), never cutting below it`
    : `NOTE: channel cut full-height to the ground (this drains the basin — under review)`;
  const scaleLine = presetName().startsWith("grammar")
    ? `\nREAL SCALE (the 7·1·4·2 grammar, inches): outer basin Ø 187 in (4.75 m) · total height 169 in (4.29 m) · liṅga Ø 58 in, visible 109 in · podium 31 in · water level 29 in (7 in deep) · twelve suns on the Ø 169 in mid-band circle.\n`
    : "";
  return `A sacred Shivalinga fountain-basin ("the Rtambhareshvara murti"), rendered as a single centered object on a plain ivory background.
${scaleLine}
GEOMETRY — follow these measured proportions exactly (unit R = the basin's outer rim radius; total basin width = 2R):
- Overall: total height ${totalH.toFixed(2)} R — ${(totalH / 2).toFixed(2)}× the basin's full width. A wide, grounded vessel, not a tower.
- Podium drum: one circular drum, outer radius 1.00 R, height ${e.rimHeight.toFixed(2)} R${e.plinthHeight > 0.004 ? `, standing on a plain plinth ring ${e.plinthHeight.toFixed(2)} R tall` : ", no plinth — it rises straight from the floor"}.
- Rim band: flat top band from radius ${r.waterOuter.toFixed(2)} R to 1.00 R, carrying ${nmShown}. Medallions are simple engraved concentric-circle discs (radius ${r.medallionRadius.toFixed(3)} R), evenly spaced — never rosettes, never flowers.
- Water: ${water}. The water forms a clean ring (annulus) from the lotus out to radius ${r.waterOuter.toFixed(2)} R.
- Lotus seat (the jaladhari): exactly TWO tiers of smooth carved petals, offset ${c.tierOffsetDeg}° (half a step). LOWER tier: ${c.petalsLower} broad THICK petals floating FLAT on the water like stone lily pads (slab thickness ~${((s.petal.padThickness ?? 0.043) * 187 / 2).toFixed(0)} in visible above the surface, their curved roots blooming up from under the water), tips reaching ${r.tier2PetalTip.toFixed(2)} R. UPPER tier: ${c.petalsUpper} plump rounded bud petals, tightly packed on the cup, rising EXACTLY as high as the pads reach wide (the folded gesture), tips at ${r.tier1PetalTip.toFixed(2)} R ending at the cup lip — never above it. Count the petals exactly.
- ${e.collarHeight > 0.004 ? `A plain cylindrical collar (${e.collarHeight.toFixed(2)} R tall) rings the linga where it meets the lotus.` : "The linga rises directly from the lotus cup, no collar."}
- Linga: radius ${r.linga.toFixed(2)} R, rising ${e.lingaHeightAboveLotus.toFixed(2)} R above the lotus cup — visible height ${hd.toFixed(1)}× its own diameter — crowned by a smooth ${e.lingaDomeRatio <= 1.02 ? "hemispherical" : "slightly elongated elliptical"} dome.
- The spout (pranala/nali): ONE channel, width ${s.nali.widthOverR.toFixed(2)} R, pointing straight at the viewer, projecting ${s.nali.lengthBeyondRimOverR.toFixed(2)} R past the rim; a thin stream falls from its lip into a small square pool (${e.poolWidth.toFixed(2)} R wide) set flush in the pavement in front.

MATERIALS: ${state.display.material === "canon" ? "the linga in polished black stone (charcoal, near-matte); basin, lotus and drum in warm pale sandstone; water still and reflective" : "the whole object in one warm pale carved sandstone; water still and reflective"}.

STYLE: precise archaeological illustration — fine engraved line work and delicate stipple shading, charcoal ink on ivory paper, uniform diffuse light, no cast shadows, mild three-quarter view from slightly above (or match the requested view), the object fully in frame with generous margins, inside a thin ruled border.

DO NOT: no trident/trishul or any weapon motif${s.nali.trishul ? " — EXCEPTION: one small engraved trishul on the channel face is required this time" : ""}; no om symbols, snakes, garlands, flowers, figures or deities; no text; no extra petal rows beyond the two tiers; no extra medallions; no droplets or splashing; no environment, pedestal table, or background scenery; never change the stated counts or proportions.`;
}

const drawer = $("#drawer"), dtext = $("#drawertext");
function openDrawer(kind) {
  $("#drawertitle").textContent = kind === "json" ? "The numbers — grid.json shape" : "Render prompt — for the founder's ChatGPT pass";
  dtext.value = kind === "json" ? currentJSON() : buildPrompt();
  drawer.classList.add("open");
  dtext.focus(); dtext.select();
}
$("#btn-prompt").addEventListener("click", () => openDrawer("prompt"));
$("#btn-json").addEventListener("click", () => openDrawer("json"));
$("#drawerclose").addEventListener("click", () => drawer.classList.remove("open"));
$("#drawercopy").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(dtext.value); $("#drawercopy").textContent = "Copied"; }
  catch (e) { dtext.focus(); dtext.select(); $("#drawercopy").textContent = "Select+copy"; }
  setTimeout(() => { $("#drawercopy").textContent = "Copy"; }, 1600);
});

/* ─────────────────── boot + shot mode ────────────────────── */
buildRows();
buildMurti();
refreshText();

const Q = new URLSearchParams(location.search);
if (Q.has("preset")) {
  state = deep(PRESETS[Q.get("preset")] || CANON);
  refreshInputs(); buildMurti(); refreshText();
}
if (Q.has("explode")) { explodeT = parseFloat(Q.get("explode")) || 0; $("#explode").value = explodeT; applyExplode(); }
if (Q.has("guides")) { state.display.guides = Q.get("guides") === "1"; buildMurti(); }
if (Q.has("over")) {
  // path overrides, e.g. ?over={"rings.cupOuter":0.46} — for batch study renders
  try {
    for (const [p, v] of Object.entries(JSON.parse(Q.get("over")))) setPath(state, p, v);
    refreshInputs(); buildMurti(); refreshText();
  } catch (e) { /* malformed override — ignore */ }
}
if (Q.get("panel") === "0") document.body.classList.add("panel-closed");
if (Q.has("view")) { const v = Q.get("view"); const vs = VIEWS(); Object.assign(cam, vs[v] || vs.study); activeView = vs[v] ? v : "study"; useOrtho = activeView !== "study"; heartMode = v === "heart"; applyHeartFade(); setActiveView(activeView); applyCam(); }
if (innerWidth < 821) document.body.classList.add("panel-closed");

if (Q.get("shot") === "1") {
  const key = Q.get("view") || "study";
  Promise.resolve(document.fonts ? document.fonts.ready : null).then(() => {
    let n = 0;
    const tick = () => {
      renderer.render(scene, camera); placeLabels();
      if (++n < 5) requestAnimationFrame(tick);
      else window.__murtiShot = { done: true, key, frames };
    };
    requestAnimationFrame(tick);
  });
}
