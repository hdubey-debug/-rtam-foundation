// संध्या दर्शन · Sandhya Darshan. The page opens on the poster that was scanned, its lamps are lit (the film), the 3D
// rises around the same lamps, and the visitor walks round it, a full circle: the temple, Nandi's mandapa, or the whole
// complex. States (on <body>): s-poster → s-film → s-hold → s-handoff → s-walk. Phones that cannot run the 3D see the
// same through night pictures (tier "still").
import { Stage, MODES } from './stage.js';

const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const body = document.body;
const subject = document.documentElement.dataset.subject || 'temple';
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const qs = new URLSearchParams(location.search);

// ---------------------------------------------------------------- what this phone gets
function detectTier() {
  if (qs.get('tier')) return qs.get('tier');
  const c = document.createElement('canvas');
  const gl = c.getContext('webgl2') || c.getContext('webgl');
  if (!gl) return 'still';
  const conn = navigator.connection || {};
  if (conn.saveData || /(^|-)(slow-2g|2g)$/.test(conn.effectiveType || '')) return 'still';
  const mem = navigator.deviceMemory || 4;                 // Chrome reports at most 8; Safari reports nothing
  if (mem < 2) return 'still';
  return mem >= 4 ? 'hi' : 'lo';                          // iPhones (no report) and most phones get the sharp models
}
const tier = detectTier();
body.dataset.tier = tier;

// ---------------------------------------------------------------- words (Hindi first, a small English echo)
const WORDS = {
  intro: ['अब मंदिर आपका है', 'Swipe to walk around it'],
  introNandi: ['नन्दी · अपने स्वामी की ओर', 'Swipe to walk around Nandi'],
  poster: ['पहाड़ीखेड़ा में बन रहा है', 'Now rising at Pahadi Kheda'],
  door: ['द्वार · दीप की एक रेखा', 'The door · a thread of lamplight'],
  jali: ['जाली · भीतर दीप जल रहे हैं', 'The jali · lamps burning within'],
  tower: ['शिखर · गर्भगृह के ठीक ऊपर', 'The tower · over the sanctum'],
  side: ['प्रदक्षिणा · मंदिर सदा दाहिने हाथ', 'Keep the temple on your right'],
  nandiFace: ['नन्दी · अपने स्वामी की ओर', 'Nandi · facing his lord'],
  nandiBack: ['नन्दी · शिव का वाहन', "Nandi · Shiva's mount"],
  mandapa: ['नन्दी मंडप', 'The Nandi mandapa'],
  gaze: ['नन्दी की दृष्टि से', 'As Nandi sees it'],
  complex: ['मंदिर परिसर', 'The temple and its mandapa'],
};
// one caption at a time: the old one fades out completely before the new one fades in, and while one walks round, a new
// caption waits until its side has stayed in view a moment (no flicker at the boundaries, never two at once)
let shown = '', want = '', busy = false, waitT = null;
function caption(key, now) {
  if (key === want && !now) return;                      // already on its way (or shown): let its wait run
  want = key; clearTimeout(waitT);
  if (now) swapCaption(); else waitT = setTimeout(swapCaption, 450);
}
function swapCaption() {
  if (busy || want === shown || !WORDS[want]) return;
  busy = true; const key = want, c = $('#caption');
  c.classList.add('fade');
  setTimeout(() => {
    shown = key; c.querySelector('.dn').textContent = WORDS[key][0]; c.querySelector('.en').textContent = WORDS[key][1];
    c.classList.remove('fade');
    setTimeout(() => { busy = false; if (want !== shown) swapCaption(); }, 380);
  }, shown ? 380 : 0);
}
// what is in front of you, as you walk round
function sectorWord(mode, az, facing) {
  if (mode === 'temple') {
    if (Math.abs(((az - MODES.temple.home) % 360 + 540) % 360 - 180) < 14) return 'poster';
    const f = Math.abs(facing);
    if (f <= 35) return 'door';
    if (f >= 135) return 'tower';
    return facing > 0 ? 'jali' : 'side';
  }
  if (mode === 'nandi') { const f = Math.abs(facing); return f <= 55 ? 'nandiFace' : f >= 125 ? 'nandiBack' : 'mandapa'; }
  return Math.abs(facing) <= 18 ? 'gaze' : 'complex';
}

// ---------------------------------------------------------------- state
let state = 'poster';
function set(s) { state = s; body.classList.remove(...[...body.classList].filter((c) => c.startsWith('s-'))); body.classList.add('s-' + s); }

// ---------------------------------------------------------------- the film and the 3D
const film = $('#film');
const FILM = await fetch(`media/${subject}-film.json`).then((r) => r.json()).catch(() => ({}));
if (FILM.thread) { const st = $('#frame').style; st.setProperty('--tx', FILM.thread[0] + '%'); st.setProperty('--ty', FILM.thread[1] + '%'); st.setProperty('--th', FILM.thread[2] + '%'); }
film.src = `media/${subject}-${tier === 'hi' ? 1280 : 960}.mp4`;

const START = subject === 'nandi' ? 'nandi' : 'temple';
let stage = null, stageReady = false, filmDone = false, introUntil = 0;
if (tier !== 'still') {
  try {
    stage = new Stage($('#gl'), { tier, breathe: !reduce });
    stage.onframe = onFrame; stage.onspinend = () => $('#walk').classList.remove('on');
    layout();
    stage.load((p) => $('#frame').style.setProperty('--p', p.toFixed(2)))
      .then(() => { stageReady = true; stage.setMode(START); if (filmDone && state === 'hold') waitThenHandoff(); })
      .catch(() => { stage = null; body.dataset.tier = 'still'; if (filmDone && state === 'hold') waitThenHandoff(); });
  } catch (e) { stage = null; body.dataset.tier = 'still'; }
}

function startFilm() {
  if (state !== 'poster') return;
  $('#play').hidden = true; set('film');
  const p = film.play();
  if (p && p.catch) p.catch(() => { set('poster'); $('#play').hidden = false; });   // autoplay refused: the visitor lights the lamps
}
let heldAt = 0;
function hold() { if (state === 'poster' || state === 'film') { set('hold'); heldAt = performance.now(); follow(1000); } }
function filmEnded() { if (filmDone) return; filmDone = true; film.pause(); $('#play').hidden = true; hold(); waitThenHandoff(); }
film.addEventListener('ended', filmEnded);
film.addEventListener('error', () => { if (state === 'poster' || state === 'film') filmEnded(); });
setTimeout(() => { if (state === 'poster' && $('#play').hidden) filmEnded(); }, 7000);   // the film never came
$('#skip').addEventListener('click', filmEnded);
// the lamps are lit by a tap: on the button, or anywhere on the poster while it waits
$('#play').addEventListener('click', (e) => { e.stopPropagation(); startFilm(); });
$('#app').addEventListener('click', () => { if (state === 'poster' && !$('#play').hidden) startFilm(); });

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
    set('walk'); markMode(START);
    stage.setMode(START); introUntil = performance.now() + 4200;
    caption(START === 'nandi' ? 'introNandi' : 'intro', true);
    setTimeout(() => { introUntil = 0; onFrame(stage.az); }, 4300);
    follow(1200);
    if (tier === 'hi') setTimeout(() => stage.upgrade(), 2500);
  }, 1100);
}

// keep the 3D framed on the picture area while the layout moves (state changes, rotation)
function layout() {
  // the 3D fades out behind the name above and the controls below, wherever they stand on this screen
  const tt = $('#title .lockup').getBoundingClientRect(), ui = $('#ui').getBoundingClientRect(), st = document.documentElement.style;
  st.setProperty('--fadeTop', Math.round(tt.bottom) + 'px'); st.setProperty('--fadeBot', Math.round(ui.top + 8) + 'px');
  if (!stage) return; const r = $('#frame').getBoundingClientRect(); stage.setFrame({ x: r.left, y: r.top, w: r.width, h: r.height }); stage.resize();
}
function follow(ms) { const t0 = performance.now(); const tick = (t) => { layout(); if (t - t0 < ms) requestAnimationFrame(tick); }; requestAnimationFrame(tick); }
// turning the phone: the layout jumps to its new place at once (no sliding text), then the 3D follows
let rotT = null, wide = innerWidth > innerHeight;
function turned() {
  if ((innerWidth > innerHeight) !== wide) { wide = !wide; body.classList.add('rot'); clearTimeout(rotT); rotT = setTimeout(() => body.classList.remove('rot'), 700); }
  follow(1000);
}
addEventListener('resize', turned);
addEventListener('orientationchange', turned);

// ---------------------------------------------------------------- the walk
// the dial: a ring with one tick, where you stand around the building (its front at the top)
function onFrame(az) {
  if (!stage) return;
  const f = stage.facing();
  $('#walk .dial i').style.transform = `rotate(${f.toFixed(1)}deg)`;      // walking round clockwise turns the dot clockwise
  if (state === 'walk' && performance.now() > introUntil) caption(sectorWord(stage.mode, az, f));
}
function markMode(name) { $$('#modes button').forEach((b) => b.classList.toggle('on', b.dataset.mode === name)); }

// drag sideways to walk round (the building turns with the finger), flick to keep going, pinch to come closer
const gl = $('#gl'); const pts = new Map(); let drag = null, pinch = null;
const dist = (a, b) => Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
const degPerPx = () => 300 / Math.max(320, stage.frame.w * 1.6);
gl.addEventListener('pointerdown', (e) => {
  if (state !== 'walk') return;
  gl.setPointerCapture(e.pointerId); pts.set(e.pointerId, e); stage.stopSpin(); stage.vel = 0;
  if (pts.size === 1) drag = { last: e.clientX, t: performance.now(), v: 0 };
  if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: dist(a, b), z: stage.zoom }; drag = null; }
});
gl.addEventListener('pointermove', (e) => {
  if (!pts.has(e.pointerId)) return; pts.set(e.pointerId, e);
  if (pinch && pts.size === 2) { const [a, b] = [...pts.values()]; stage.zoom = Math.max(.8, Math.min(2.2, pinch.z * dist(a, b) / pinch.d)); stage.dirty = true; stage.wake(); return; }
  if (drag) {
    const now = performance.now(), dx = e.clientX - drag.last, d = dx * degPerPx();
    stage.rotate(d); drag.v = .7 * drag.v + .3 * (d / Math.max(8, now - drag.t) * 1000); drag.last = e.clientX; drag.t = now;
  }
});
const lift = (e) => {
  pts.delete(e.pointerId); if (pts.size < 2) pinch = null;
  if (drag && pts.size === 0) { if (performance.now() - drag.t < 90) stage.fling(drag.v); drag = null; }
};
gl.addEventListener('pointerup', lift); gl.addEventListener('pointercancel', lift);
gl.addEventListener('wheel', (e) => { if (state !== 'walk') return; e.preventDefault(); stage.zoom = Math.max(.8, Math.min(2.2, stage.zoom * (1 - e.deltaY * .0012))); stage.dirty = true; }, { passive: false });
addEventListener('keydown', (e) => {
  if (state !== 'walk' || !stage) return;
  if (e.key === 'ArrowRight') { stage.stopSpin(); stage.fling(140); }
  if (e.key === 'ArrowLeft') { stage.stopSpin(); stage.fling(-140); }
});

// प्रदक्षिणा: walk round once, slowly, keeping it on your right; a touch stops it
$('#walk').addEventListener('click', () => {
  if (!stage || state !== 'walk') return;
  if (stage.spinning) { stage.stopSpin(); return; }
  $('#walk').classList.add('on'); stage.spin(reduce ? 60 : 16);
});

// what to walk round: the temple, Nandi's mandapa, or the whole complex; the view dips to the night and comes back on it
$('#modes').addEventListener('click', (e) => {
  const b = e.target.closest('button[data-mode]'); if (!b || state !== 'walk') return;
  const name = b.dataset.mode; if (!stage) { stillShow(name, 0); return; }
  if (name === stage.mode) { stage.setMode(name, MODES[name].home); return; }       // again: back to where it starts
  markMode(name);
  const keep = name !== 'nandi' && stage.mode !== 'nandi';                           // temple ↔ complex keep their direction
  gl.animate([{ opacity: 1 }, { opacity: 0 }], { duration: reduce ? 1 : 320, fill: 'forwards', easing: 'ease-in' }).finished.then(() => {
    stage.setMode(name, keep ? stage.az : undefined);
    caption(sectorWord(stage.mode, stage.az, stage.facing()), true);                 // a choice: its words come at once
    gl.getAnimations().forEach((a) => a.cancel());
    gl.animate([{ opacity: 0 }, { opacity: 1 }], { duration: reduce ? 1 : 700, easing: 'ease-out' });
  });
});

// ---------------------------------------------------------------- the night pictures (phones without the 3D)
const STILLS = { temple: ['media/temple-last.webp', 'media/front-night.webp'], nandi: ['media/nandi-last.webp'], complex: ['media/front-night.webp'] };
let stillName = START, stillI = 0;
function stillShow(name, i) {
  const list = STILLS[name]; stillName = name; stillI = ((i % list.length) + list.length) % list.length;
  const im = $('#still'); im.style.transition = 'opacity .45s'; im.style.opacity = '0';
  setTimeout(() => { im.src = list[stillI]; im.onload = () => { im.style.opacity = '1'; }; }, 460);
  caption(name === 'nandi' ? 'nandiFace' : name === 'complex' ? 'gaze' : stillI ? 'door' : 'poster', true); markMode(name);
}
function stillWalk() {
  set('walk'); stillShow(START, 0);
  let x0 = null;
  $('#app').addEventListener('pointerdown', (e) => { x0 = e.clientX; });
  $('#app').addEventListener('pointerup', (e) => { if (x0 === null || state !== 'walk') return; const dx = e.clientX - x0; x0 = null; if (Math.abs(dx) > 40) stillShow(stillName, stillI + (dx > 0 ? 1 : -1)); });
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
