// संध्या दर्शन · Sandhya Darshan. The page opens on the poster that was scanned, its lamps are lit (the film), the 3D
// temple rises around the same lamps, and the visitor walks around it (pradakshina) to Nandi's view of it.
// States (on <body>): s-poster → s-film → s-hold → s-handoff → s-walk. Phones that cannot run the 3D walk the same path
// through night pictures (tier "still").
import { Stage, STOPS, NANDI_FRONT, NANDI_CRANE } from './stage.js';

const $ = (s) => document.querySelector(s);
const body = document.body;
const subject = document.documentElement.dataset.subject || 'temple';
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const qs = new URLSearchParams(location.search);

// ---------------------------------------------------------------- what this phone gets
function detectTier() {
  if (qs.get('tier')) return qs.get('tier');
  const c = document.createElement('canvas');
  if (!(c.getContext('webgl2') || c.getContext('webgl'))) return 'still';
  const conn = navigator.connection || {};
  if (conn.saveData || /(^|-)(slow-2g|2g)$/.test(conn.effectiveType || '')) return 'still';
  const ios = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const mem = navigator.deviceMemory || 4;
  if (mem < 2) return 'still';
  return ios || mem >= 6 ? 'hi' : 'lo';
}
const tier = detectTier();
body.dataset.tier = tier;

// ---------------------------------------------------------------- words (Hindi first, a small English echo)
const WORDS = {
  intro: ['अब मंदिर आपका है', 'Swipe to walk around it'],
  poster: ['पहाड़ीखेड़ा में बन रहा है', 'Now rising at Pahadi Kheda'],
  door: ['द्वार · दीप की एक रेखा', 'The door · a thread of lamplight'],
  jali: ['जाली · भीतर दीप जल रहे हैं', 'The jali · lamps burning within'],
  tower: ['शिखर · गर्भगृह के ठीक ऊपर', 'The tower · over the sanctum'],
  side: ['प्रदक्षिणा · मंदिर सदा दाहिने हाथ', 'Keep the temple on your right'],
  nandi: ['नन्दी · अपने स्वामी की ओर', 'Nandi · facing his lord'],
  gaze: ['नन्दी की दृष्टि से', 'As Nandi sees it'],
};
function caption(key) {
  const c = $('#caption'), w = WORDS[key]; if (!w) return;
  c.classList.add('fade');
  setTimeout(() => { c.querySelector('.dn').textContent = w[0]; c.querySelector('.en').textContent = w[1]; c.classList.remove('fade'); }, 250);
}

// ---------------------------------------------------------------- state
let state = 'poster';
function set(s) { state = s; body.classList.remove(...[...body.classList].filter((c) => c.startsWith('s-'))); body.classList.add('s-' + s); }

// ---------------------------------------------------------------- the film and the 3D
const film = $('#film');
const FILM = await fetch(`media/${subject}-film.json`).then((r) => r.json()).catch(() => ({}));
if (FILM.thread) { const st = $('#frame').style; st.setProperty('--tx', FILM.thread[0] + '%'); st.setProperty('--ty', FILM.thread[1] + '%'); st.setProperty('--th', FILM.thread[2] + '%'); }
film.src = `media/${subject}-${tier === 'hi' ? 1280 : 960}.mp4`;

let stage = null, stageReady = false, filmDone = false, entering = false;
if (tier !== 'still') {
  try {
    stage = new Stage($('#gl'), { tier, breathe: !reduce });
    stage.onframe = onFrame;
    layout();
    stage.load((p) => $('#frame').style.setProperty('--p', p.toFixed(2)))
      .then(() => { stageReady = true; if (subject === 'nandi') { stage.view = { ...NANDI_FRONT, look: NANDI_FRONT.look.slice() }; stage.u = stage.uNow = 5; } if (filmDone && state === 'hold') waitThenHandoff(); })
      .catch(() => { stage = null; body.dataset.tier = 'still'; if (filmDone && state === 'hold') waitThenHandoff(); });
  } catch (e) { stage = null; body.dataset.tier = 'still'; }
}

function startFilm() {
  if (state !== 'poster') return;
  set('film');
  const p = film.play();
  if (p && p.catch) p.catch(() => { set('poster'); $('#play').hidden = false; });   // autoplay refused: the visitor lights the lamps
}
let heldAt = 0;
function hold() { if (state === 'poster' || state === 'film') { set('hold'); heldAt = performance.now(); follow(1000); } }
function filmEnded() { if (filmDone) return; filmDone = true; film.pause(); hold(); waitThenHandoff(); }
film.addEventListener('ended', filmEnded);
film.addEventListener('error', () => { if (state === 'poster' || state === 'film') filmEnded(); });
setTimeout(() => { if (state === 'poster' && $('#play').hidden) filmEnded(); }, 7000);   // the film never came
$('#skip').addEventListener('click', filmEnded);
$('#play').addEventListener('click', () => { $('#play').hidden = true; startFilm(); });

if (reduce) filmEnded();
else if (qs.has('skip')) setTimeout(filmEnded, 700);   // (the tests: straight to the walk)
else {
  film.addEventListener('canplaythrough', () => setTimeout(startFilm, 500), { once: true });
  film.load();
  setTimeout(() => { if (state === 'poster' && film.readyState >= 3) startFilm(); }, 2500);
}
// the hand-over waits for the 3D, and for the picture to finish rising into place
function waitThenHandoff() { if (stageReady || !stage) setTimeout(handoff, Math.max(0, 950 - (performance.now() - heldAt))); }

// the lamps stay, the stone returns: the picture dims to its lamps, and the 3D rises around them from the same view
function handoff() {
  if (state !== 'hold') return;
  set('handoff'); layout();
  setTimeout(() => {
    if (!stage) { stillWalk(); return; }
    set('walk');
    if (subject === 'nandi') {                       // facing Nandi as on the poster, then see what he sees
      entering = true; stage.view = { ...NANDI_FRONT, look: NANDI_FRONT.look.slice() }; stage.u = stage.uNow = 5; stage.dirty = true; caption('nandi');
      setTimeout(() => {
        if (state !== 'walk' || stage.anim) { entering = false; return; }
        stage.goPoses(NANDI_CRANE, 5200, () => { entering = false; stage.scrub(5); caption('gaze'); });
      }, 2400);
    } else {
      stage.scrub(0); caption('intro'); setTimeout(() => { if (Math.round(stage.u) === 0 && !stage.anim) caption('poster'); }, 4200);
    }
    follow(1200);
    if (tier === 'hi') setTimeout(() => stage.upgrade(), 3000);
  }, 1100);
}

// keep the 3D framed on the picture area while the layout moves (state changes, rotation)
function layout() { if (!stage) return; const r = $('#frame').getBoundingClientRect(); stage.setFrame({ x: r.left, y: r.top, w: r.width, h: r.height }); stage.resize(); }
function follow(ms) { const t0 = performance.now(); const tick = (t) => { layout(); if (t - t0 < ms) requestAnimationFrame(tick); }; requestAnimationFrame(tick); }
addEventListener('resize', () => follow(1000));
addEventListener('orientationchange', () => follow(1200));

// ---------------------------------------------------------------- the walk
// where one is: a tick sliding along a hairline; close to the stone, the name steps away
const PATH_W = 120;
function onFrame(u) {
  $('#path').style.setProperty('--at', (u / (STOPS.length - 1) * PATH_W).toFixed(1) + 'px');
  const i = Math.round(u), near = state === 'walk' && !entering && STOPS[i] && STOPS[i].near && Math.abs(u - i) < .3;
  body.classList.toggle('near', !!near);
}
function markPath() { $('#path').setAttribute('aria-valuenow', String(Math.round(stage ? stage.u : 0))); }
function toStop(i, dur, done) {
  i = Math.max(0, Math.min(STOPS.length - 1, i));
  stage.goU(i, dur || 1500, () => { caption(STOPS[i].id === 'poster' ? 'poster' : STOPS[i].id); markPath(); done && done(); });
  markPath();
}
$('#path').addEventListener('click', (e) => {         // tap along the path: walk to the nearest stop
  if (state !== 'walk' || !stage) return;
  const r = $('#path').getBoundingClientRect(); auto(false);
  toStop(Math.round((e.clientX - r.left) / r.width * (STOPS.length - 1)));
});

// gestures: drag sideways to walk (the temple turns with the finger), pinch to come closer
const gl = $('#gl'); const pts = new Map(); let drag = null, pinch = null;
const dist = (a, b) => Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
gl.addEventListener('pointerdown', (e) => {
  if (state !== 'walk' || entering) return;
  gl.setPointerCapture(e.pointerId); pts.set(e.pointerId, e); auto(false); stage.wake();
  if (pts.size === 1) drag = { x: e.clientX, u: stage.uNow, last: e.clientX, v: 0, moved: false };
  if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: dist(a, b), z: stage.zoom }; drag = null; }
});
gl.addEventListener('pointermove', (e) => {
  if (!pts.has(e.pointerId)) return; pts.set(e.pointerId, e);
  if (pinch && pts.size === 2) { const [a, b] = [...pts.values()]; stage.zoom = Math.max(.72, Math.min(1.3, pinch.z * pinch.d / dist(a, b))); stage.dirty = true; return; }
  if (drag) {
    const dx = e.clientX - drag.x; if (Math.abs(dx) > 4) drag.moved = true;
    stage.scrub(drag.u + dx / (stage.frame.w * .75)); drag.v = e.clientX - drag.last; drag.last = e.clientX;
  }
});
const lift = (e) => {
  pts.delete(e.pointerId); if (pts.size < 2) pinch = null;
  if (drag && pts.size === 0) {
    const flick = Math.abs(drag.v) > 5 ? Math.sign(drag.v) * .5 : 0;
    if (drag.moved) toStop(Math.round(stage.u + flick), 700);
    drag = null;
  }
};
gl.addEventListener('pointerup', lift); gl.addEventListener('pointercancel', lift);
gl.addEventListener('wheel', (e) => { if (state !== 'walk') return; e.preventDefault(); stage.zoom = Math.max(.72, Math.min(1.3, stage.zoom * (1 + e.deltaY * .0012))); stage.dirty = true; }, { passive: false });
addEventListener('keydown', (e) => {
  if (state === 'walk' && stage && !entering) {
    if (e.key === 'ArrowRight') { auto(false); toStop(Math.round(stage.u) + 1); }
    if (e.key === 'ArrowLeft') { auto(false); toStop(Math.round(stage.u) - 1); }
  }
});

// प्रदक्षिणा: a slow walk round, pausing at each stop, that stops when touched; it ends at Nandi, facing the temple
let autoT = null;
function auto(on) {
  clearTimeout(autoT); autoT = null;
  $('#chips [data-act="walk"]').classList.toggle('on', !!on);
  if (!on) return;
  const step = () => {
    const i = Math.round(stage.u);
    if (i >= STOPS.length - 1) { auto(false); return; }
    toStop(i + 1, 2600, () => { autoT = setTimeout(step, 2300); });
  };
  if (Math.round(stage.u) < STOPS.length - 1) { step(); return; }
  // at Nandi, a new round: step back to where the poster stands (a short glide, the same side of the temple), then walk
  const s0 = STOPS[0];
  stage.goPoses([{ ...s0, az: s0.az + 360, look: s0.look.slice() }], 1800, () => { stage.scrub(0); caption('poster'); markPath(); autoT = setTimeout(step, 1500); });
}
$('#chips').addEventListener('click', (e) => {
  const b = e.target.closest('button'); if (!b || !stage || entering) return;
  const a = b.dataset.act;
  if (a === 'walk') auto(!b.classList.contains('on'));
  if (a === 'nandi') { auto(false); toStop(STOPS.length - 1); }
});

// ---------------------------------------------------------------- the night pictures (phones without the 3D)
const STILLS = [
  { src: `media/temple-last.webp`, key: 'poster' }, { src: 'media/front-night.webp', key: 'door' },
  { src: 'media/nandi-last.webp', key: 'nandi' }];
let stillI = 0, stillOn = false;
function stillShow(i) {
  stillI = Math.max(0, Math.min(STILLS.length - 1, i));
  const im = $('#still'); im.style.transition = 'opacity .45s'; im.style.opacity = '0';
  setTimeout(() => { im.src = STILLS[stillI].src; im.onload = () => { im.style.opacity = '1'; }; caption(STILLS[stillI].key); }, 460);
  $('#path').style.setProperty('--at', (stillI / (STILLS.length - 1) * PATH_W).toFixed(1) + 'px');
}
function stillWalk() {
  set('walk'); stillShow(0);
  if (stillOn) return; stillOn = true;
  let x0 = null;
  $('#app').addEventListener('pointerdown', (e) => { x0 = e.clientX; });
  $('#app').addEventListener('pointerup', (e) => { if (x0 === null || state !== 'walk') return; const dx = e.clientX - x0; x0 = null; if (Math.abs(dx) > 40) stillShow(stillI + (dx > 0 ? 1 : -1)); });   // as the 3D: the finger moves you forward
  $('#chips').addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b || state !== 'walk') return;
    if (b.dataset.act === 'walk') stillShow(stillI + 1);
    if (b.dataset.act === 'nandi') stillShow(STILLS.length - 1);
  });
}

// ---------------------------------------------------------------- address, contact, sharing
async function share() {
  const url = location.origin + location.pathname.replace(/[^/]*$/, '');
  const text = 'पहाड़ीखेड़ा में बन रहा है · ऋतम्भरेश्वर मंदिर';
  try { if (navigator.share) { await navigator.share({ title: 'ऋतम्भरेश्वर मंदिर', text, url }); return; } } catch (e) { if (e && e.name === 'AbortError') return; }
  const a = document.createElement('a');                 // WhatsApp in a new tab: the visit stays where it was
  a.href = 'https://wa.me/?text=' + encodeURIComponent(text + '\n' + url); a.target = '_blank'; a.rel = 'noopener';
  document.body.append(a); a.click(); a.remove();
}
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-act]'); if (!b) return;
  const a = b.dataset.act;
  if (a === 'share') share();
  if (a === 'visit') { const v = $('#visit'); v.hidden = false; requestAnimationFrame(() => v.classList.add('on')); }
  if (a === 'close') { const v = $('#visit'); v.classList.remove('on'); setTimeout(() => { v.hidden = true; }, 500); }
});
