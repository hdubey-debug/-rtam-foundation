// संध्या दर्शन · Sandhya Darshan. The page opens on the poster that was scanned, its lamps are lit (the film), the 3D
// rises around the same lamps, and the visitor walks round it, a full circle: the temple, Nandi's mandapa, or the whole
// complex. States (on <body>): s-poster → s-film → s-hold → s-handoff → s-walk. Phones that cannot run the 3D see the
// same through night pictures (tier "still").
import { MODES } from './motion.js';
import { Fire, Life } from './fire.js';

const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const body = document.body;
const subject = document.documentElement.dataset.subject || 'temple';
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const qs = new URLSearchParams(location.search);
// the pilot (test pages only, <html data-pilot="1">): the lamps are lit by a hand, the walk goes round by itself at one size,
// centred, and प्रदक्षिणा पूर्ण · the return
const PILOT = document.documentElement.dataset.pilot === '1';
// the lamp's fire as Harsh chooses it on the test link (25 Oct: "I would need to see them all in the actual demo"):
// ?fire=blue (his blue GIF's colours), ?disc=0 (the fire alone and larger, no disc)
const FIRE_BLUE = qs.get('fire') === 'blue';
if (qs.get('disc') === '0') document.documentElement.classList.add('fire-nodisc');
let lampsLit = true;                                    // the walk's lamp: the temple's lamps lit, or at rest

// ---------------------------------------------------------------- what this phone gets
// One set of models for the whole visit, never swapped mid-walk: a desktop (a fine pointer and no touch) gets the sharp
// ones; every phone and tablet the light ones. No WebGL, a data saver, a 2G line or under 2 GB: the night pictures.
function detectTier() {
  if (qs.get('tier')) return qs.get('tier');
  const c = document.createElement('canvas');
  const gl = c.getContext('webgl2') || c.getContext('webgl');
  if (!gl) return 'still';
  const lose = gl.getExtension('WEBGL_lose_context'); if (lose) lose.loseContext();     // the probe gives its GPU context back
  const conn = navigator.connection || {};
  if (conn.saveData || /(^|-)(slow-2g|2g)$/.test(conn.effectiveType || '')) return 'still';
  if ((navigator.deviceMemory || 4) < 2) return 'still';                                  // Chrome reports at most 8; Safari nothing
  return navigator.maxTouchPoints === 0 && matchMedia('(pointer: fine)').matches ? 'hi' : 'lo';
}
const tier = detectTier();
body.dataset.tier = tier;

// ---------------------------------------------------------------- words (Hindi first, a small English echo)
const WORDS = {
  intro: ['अब मंदिर आपका है', 'Swipe to walk around it'],
  introNandi: ['नन्दी · अपने स्वामी की ओर', 'Swipe to walk around Nandi'],
  door: ['द्वार · दीप की एक रेखा', 'The door · a thread of lamplight'],
  jali: ['जाली · भीतर दीप जल रहे हैं', 'The jali · lamps burning within'],
  doorOut: ['द्वार · दीप शांत', 'The door · its lamp at rest'],
  jaliOut: ['जाली · भीतर दीप शांत हैं', 'The jali · the lamps at rest within'],
  tower: ['शिखर · गर्भगृह के ठीक ऊपर', 'The tower · over the sanctum'],
  side: ['प्रदक्षिणा · मंदिर सदा दाहिने हाथ', 'Keep the temple on your right'],
  returned: ['प्रदक्षिणा पूर्ण', 'One round, complete'],
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
    const w = (!lampsLit && WORDS[key + 'Out']) || WORDS[key];       // (the lamps at rest: the door and the jali say so)
    shown = key; c.querySelector('.dn').textContent = w[0]; c.querySelector('.en').textContent = w[1];
    c.classList.remove('fade');
    setTimeout(() => { busy = false; if (want !== shown) swapCaption(); }, 380);
  }, shown ? 380 : 0);
}
// what is in front of you, as you walk round
function sectorWord(mode, az, facing) {
  if (mode === 'temple') {
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
// (where the door's thread sits in the film is written into the page by the build: build_site.py)
const film = $('#film');
film.src = `media/${subject}-${tier === 'hi' ? 1280 : 960}.mp4`;      // only its first bytes for now (preload="metadata")

const START = subject === 'nandi' ? 'nandi' : 'temple';
// sideways, the picture as large as 1700 of the screen's own pixels (the 1280 film at 1.33×, as a laptop shows it), never
// under 1000 CSS px: a laptop as before, a 1× wide monitor's picture larger
document.documentElement.style.setProperty('--cap', Math.round(Math.min(1700, Math.max(1000, 1700 / (devicePixelRatio || 1)))) + 'px');
// the stone on the A2 poster (left, top, right; its width = 100) and where its reflection fades out; and the stone's place
// in the film's frame (left, top, right, base, %: sandhya_film.py, written in by the build). fitPoster sets one on the other
// the final upright poster (1B, 25 Oct 2026): its stone's left, top and right, and its reflection's end, in its own unit
// (its width / 100), measured on rtam-posters/out/final/A2B-*-crowned.png (were the approved A2's 8.25-91.69 from 60.0)
const A2 = { temple: [3.69, 54.25, 96.06], nandi: [10.69, 54.31, 89.31] }, A2_END = 124.0;
const BOX = (getComputedStyle(document.documentElement).getPropertyValue('--box').trim() || '3.3 1.3 96.3 80').split(/\s+/).map(Number);
let stage = null, has3D = tier !== 'still', stageReady = false, filmDone = false, introUntil = 0;
// the 3D (three.js and the models) starts arriving once the page itself is ready (intro.js: rtam:ready; 8 s at most),
// so on a slow line it never takes the landing's bandwidth; it is waited for only after the film, 15 s at most
if (has3D) whenReady(() => {
  import('./stage.js').then(({ Stage }) => {
    if (!has3D) return null;
    stage = new Stage($('#gl'), { tier });
    stage.onframe = onFrame; stage.onspinend = spinEnded; stage.onlost = lost;
    layout();
    return stage.load();
  }).then(() => {
    if (!stage) return;
    stageReady = true; stage.setMode(START); if (filmDone && state === 'hold') waitThenHandoff();
  }).catch(lost);
});
fitPoster();
function whenReady(fn) {
  const h = document.documentElement, go = () => { if (!go.on) { go.on = true; fn(); } };
  if (h.dataset.ready || !(h.classList.contains('intro') || h.classList.contains('intro-run'))) { go(); return; }
  addEventListener('rtam:ready', go, { once: true }); setTimeout(go, 8000);
}
// the 3D gave up (its code or models failed, the phone took the GPU back, or it came too late): the night pictures
function lost() {
  const s = stage; stage = null; has3D = false; stageReady = false; body.dataset.tier = 'still';
  if (s) s.stop();
  if (state === 'hold') waitThenHandoff(); else if (state === 'walk') stillWalk();
}

function startFilm() {
  if (state !== 'poster') return;
  lampLit(); set('film'); watch();
  const p = film.play();                                // inside the tap itself: a WebView refuses a play() that comes later
  if (p && p.catch) p.catch(() => {
    if (PILOT) filmEnded();                             // refused or broken: on to the stone (never a lamp that does nothing)
    else { set('poster'); lampBack(); }                 // autoplay refused: the visitor lights the lamps
  });
}
// a film that stalls (a weak line) does not hold the visit up: 8 s for its first frame, then 4 s without a new one,
// and the lamps hand over (the dusk picture stays until it plays: body.playing)
film.addEventListener('playing', () => body.classList.add('playing'));
function watch() {
  let last = -1, at = performance.now();
  const t = setInterval(() => {
    if (state !== 'film') { clearInterval(t); return; }
    const now = performance.now();
    if (film.currentTime !== last && body.classList.contains('playing')) { last = film.currentTime; at = now; }
    if (now - at >= (body.classList.contains('playing') ? 4000 : 8000)) { clearInterval(t); filmEnded(); }
  }, 250);
}
let heldAt = 0;
function hold() {
  if (state !== 'poster' && state !== 'film') return;
  set('hold'); heldAt = performance.now();
  setTimeout(() => { if (state === 'hold' && has3D && !stageReady) lost(); }, 15000);   // the 3D, 15 s at most
}
function filmEnded() { if (filmDone) return; filmDone = true; film.pause(); $('#play').hidden = true; hold(); waitThenHandoff(); }
film.addEventListener('ended', filmEnded);
film.addEventListener('error', () => { if (state === 'poster' || state === 'film') filmEnded(); });
setTimeout(() => { if (state === 'poster' && $('#play').hidden) filmEnded(); }, 7000);   // the film never came
$('#skip').addEventListener('click', (e) => { e.stopPropagation(); if (state === 'film') filmEnded(); });   // only while the film plays
// the lamps are lit by a tap: on the button, or anywhere on the poster while it waits
$('#play').addEventListener('click', (e) => { e.stopPropagation(); startFilm(); });
$('#app').addEventListener('click', (e) => {
  if (e.target.closest('button, a, #visit')) return;                   // the address, share and the sheet never light the lamps
  if (state === 'poster' && !$('#play').hidden) startFilm();
});
// the lamp under a finger gives at once (pointerdown: iOS shows no :active on a button without a touch handler); lit, it
// fills with light and goes as the film starts
const lampEl = $('#play');
lampEl.addEventListener('pointerdown', () => { lampEl.classList.add('down'); if (fire) fire.press(); });
for (const ev of ['pointerup', 'pointercancel', 'pointerleave']) lampEl.addEventListener(ev, () => { lampEl.classList.remove('down'); if (fire) fire.release(); });
// the lamp's fire (js/fire.js), in the disc in the glyph's place: it burns while the lamp is shown and the page is seen;
// under a finger it draws in; lit, it roars as the lamp fills with light and goes, and gives its GPU context back.
// No WebGL: the glyph (its slow SMIL lean)
const mkFire = (cv) => { try { const f = new Fire(cv, { blue: FIRE_BLUE }); document.documentElement.classList.add('fire'); return f; } catch (e) { return null; } };
let fire = mkFire($('#play .lamp canvas'));
if (fire) {
  const burn = () => { if (!fire) return; if (reduce) fire.render(1.2); else fire.run(!lampEl.hidden); };   // (reduced motion: one still drawing)
  new MutationObserver(burn).observe(lampEl, { attributes: true, attributeFilter: ['hidden'] });
  document.addEventListener('visibilitychange', () => fire && fire.wake());
  if (window.ResizeObserver) new ResizeObserver(() => fire && fire.resize()).observe(fire.cv);
  burn();
}
let litT = 0;
function lampLit() {
  if (lampEl.hidden) return;
  lampEl.classList.add('lit'); if (fire) fire.light();
  litT = setTimeout(() => { lampEl.hidden = true; lampEl.classList.remove('lit', 'down'); if (fire) { fire.free(); fire = null; } }, 420);
}
function lampBack() { clearTimeout(litT); lampEl.classList.remove('lit', 'down'); lampEl.hidden = false; if (fire) fire.life = new Life(); }

// the walk's lamp (Harsh, 25 Oct: "a lights on and off feature? where we click on fire and internal lights are on and
// when we click the fire just the black smoke moves instead of the fire"): the landing's lamp again, on the water before
// the temple; a tap rests the lamps (its fire sinks into smoke, the disc dims, the jali and the door go dark), another
// lights them again (the fire catches, the lamps come back)
const lampsEl = $('#diya');                             // (#lamps is the hand-over's lamps-only picture)
let walkFire = null;
function lampsShow() {
  if (!stage || !lampsEl.hidden) return;
  lampsEl.hidden = false; placeLamps();
  walkFire = mkFire(lampsEl.querySelector('canvas'));
  if (!walkFire) { lampsEl.classList.add('noglfire'); return; }
  if (reduce) walkFire.render(1.2); else walkFire.run(true);
  document.addEventListener('visibilitychange', () => walkFire && walkFire.wake());
}
function placeLamps() {
  if (lampsEl.hidden) return;
  const h = lampsEl.offsetHeight || 52;
  if (matchMedia('(orientation: landscape)').matches) {      // sideways: at the picture's foot, on its reflection
    const f = $('#frame').getBoundingClientRect(); lampsEl.style.left = (f.left + f.width / 2).toFixed(1) + 'px'; lampsEl.style.top = (f.bottom - h - 6).toFixed(1) + 'px';
  } else {                                                    // upright: over the caption
    const u = $('#ui').getBoundingClientRect(); lampsEl.style.left = '50%'; lampsEl.style.top = (u.top - h - 4).toFixed(1) + 'px';
  }
}
lampsEl.addEventListener('pointerdown', () => lampsEl.classList.add('down'));
for (const ev of ['pointerup', 'pointercancel', 'pointerleave']) lampsEl.addEventListener(ev, () => lampsEl.classList.remove('down'));
lampsEl.addEventListener('click', (e) => {
  e.stopPropagation(); if (!stage) return;
  lampsLit = !lampsLit;
  stage.setLamps(lampsLit, lampsLit ? 1600 : 1100);
  if (walkFire) { if (reduce) { walkFire.life.set(lampsLit, walkFire.now - 5); walkFire.render(walkFire.now); } else walkFire.set(lampsLit); }   // (reduced motion: the new state at once)
  lampsEl.classList.toggle('out', !lampsLit);
  const [dn, en] = lampsLit ? ['दीप शांत करें', 'Rest the lamps'] : ['दीप जलाएँ', 'Light the lamps'];
  lampsEl.querySelector('.lbl > span:first-child').textContent = dn; lampsEl.querySelector('.lbl .en').textContent = en;
  if (shown === 'door' || shown === 'jali') { const k = shown; shown = ''; caption(k, true); }     // its words follow the lamps
});

if (reduce) filmEnded();
else if (qs.has('skip')) setTimeout(filmEnded, 700);   // (the tests: straight to the walk)
else if (PILOT) {                                     // the pilot: the visitor lights the lamps; nothing starts by itself
  $('#play').hidden = false;
  // once the landing is up (intro.js), the film's bytes, and the pictures it hands over to decoded now (a decode at the
  // moment they appear drops frames)
  afterOpening(() => {
    if (state === 'poster') { film.preload = 'auto'; film.load(); }
    for (const im of [$('#last'), $('#lamps')]) if (im.decode) im.decode().catch(() => {});
  });
}
else {
  film.addEventListener('canplaythrough', () => setTimeout(startFilm, 500), { once: true });
  film.load();
  setTimeout(() => { if (state === 'poster' && film.readyState >= 3) startFilm(); }, 2500);
}
function afterOpening(fn) {
  const h = document.documentElement.classList;
  if (h.contains('intro') || h.contains('intro-run')) addEventListener('rtam:intro-done', fn, { once: true }); else fn();
}
// the hand-over waits for the 3D, and lets the film's last frame be seen a moment
function waitThenHandoff() { if (stageReady || !has3D) setTimeout(handoff, Math.max(0, 950 - (performance.now() - heldAt))); }

// the same size, in the same place (Harsh, 22 Oct: "the image is there, and then the 3D model shows up at a similar size"):
// the 3D is drawn through the film's own camera (the anchor: the view solved on the film's lamps), so it rises exactly
// under the picture, and the picture then leaves. Nothing moves; the camera steps back only as the walk begins.
function handoff() {
  if (state !== 'hold') return;
  if (!stage || !stageReady) { set('handoff'); setTimeout(stillWalk, 900); return; }
  layout(); stage.setMode(START); stage.setSettle(0); stage.shown = true;
  set('handoff');
  const ms = handOver();
  setTimeout(() => {
    for (const a of hoAnims.splice(0)) a.cancel();      // the page's own CSS holds the end state
    if (!stage) { stillWalk(); return; }
    set('walk'); markMode(START); lampsShow();
    if (PILOT) beginWalk();
    else {
      stage.setSettle(1); introUntil = performance.now() + 4200;
      caption(START === 'nandi' ? 'introNandi' : 'intro', true);
      setTimeout(() => { introUntil = 0; onFrame(stage.az); }, 4300);
    }
  }, ms);
}
// The picture becomes the 3D in place, by light: the lamps stay, the stone returns (Harsh chose it of three, 23 Oct). The
// floods go down and the lamps stay lit; the 3D rises under those lamps with its stone dark (its own lamps-only look);
// the picture leaves; then the stone comes back by light (1.6 s, a flood). The temple's lamps are its windows and door,
// lit in the picture and in the 3D alike. Nandi's lamps-only picture is its lamp's light on the ceiling alone, a bar of
// light in the dark (Harsh, 22 Oct: "a rectangular patch"): the mandapa dims instead to the 3D's own lamp, which rises
// as the picture goes. Under reduced motion, a quiet cross-fade.
const SINE = 'cubic-bezier(.37, 0, .63, 1)';
let hoAnims = [];
// (a second fade of the same element waits for its own start: fill 'forwards', or its first value would apply at once)
const fadeTo = (el, from, to, ms, delay = 0, fill = 'both') => hoAnims.push(el.animate([{ opacity: from }, { opacity: to }], { duration: ms, delay, easing: SINE, fill }));
function handOver() {
  if (reduce) { fadeTo($('#gl'), .002, 1, 300); fadeTo($('#frame'), 1, 0, 300, 150); return 500; }
  stage.setLight(0, 1);
  if (START === 'nandi') { fadeTo($('#gl'), .002, 1, 300); fadeTo($('#last'), 1, 0, 900); fadeTo($('#frame'), 1, 0, 700, 400); }
  else { fadeTo($('#lamps'), 0, 1, 600); fadeTo($('#last'), 1, 0, 900); fadeTo($('#gl'), .002, 1, 400, 400); fadeTo($('#frame'), 1, 0, 600, 1000); }
  setTimeout(() => stage && stage.tweenTo('stone', 1, 1600), 1200);
  return 2900;
}

// keep the 3D framed on the picture area while the layout moves (state changes, rotation)
// Upright: the A2 poster at the screen's width (Harsh, 23 Oct: "make sure the dimensions and size and reflection and look
// is exactly like" the poster people scan, "Specifically, A2"): the kicker and the name (page.html), and the stone with
// its reflection where the A2 has them, in the A2's unit (its width / 100). On the A2 the stone stands at left, top,
// right and its reflection fades out at 122.75 (A2, measured on the finals); the film's frame is sized and placed so
// that its own stone (BOX) falls there. Under the reflection the lamp (in the walk, its controls), then
// the foot. A screen too short for the poster with the lamp under it takes it a little smaller. (On a phone, vh is the
// screen without the browser's bars: the visible height is measured.)
function fitPoster() {
  const st = $('#stage'), pl = $('#play'), ui = $('#ui'), root = document.documentElement.style;
  if (matchMedia('(orientation: landscape)').matches) {          // (the same in every state: nothing moves after the landing)
    st.style.top = st.style.height = pl.style.top = pl.style.bottom = ui.style.top = ui.style.bottom = ''; st.style.removeProperty('--fw');
    root.removeProperty('--u'); root.removeProperty('--y0'); return;
  }
  const W = innerWidth, H = window.visualViewport ? visualViewport.height : innerHeight;
  const F = $('#foot').getBoundingClientRect().top, P = pl.offsetHeight || 135, g = Math.max(6, H * .01);
  const lamp = P * .8;                                                     // (its ring may lie on the reflection's last light)
  const u = Math.min(W / 100, (F - g - lamp) / A2_END), y0 = Math.max(0, (F - g - lamp - A2_END * u) / 2);
  root.setProperty('--u', u.toFixed(3) + 'px'); root.setProperty('--y0', y0.toFixed(1) + 'px');
  const a = A2[START], fw = (a[2] - a[0]) * u / ((BOX[2] - BOX[0]) / 100), fh = fw * .75;
  st.style.setProperty('--fw', fw.toFixed(1) + 'px');
  st.style.top = (y0 + a[1] * u - BOX[1] / 100 * fh).toFixed(1) + 'px'; st.style.height = fh.toFixed(1) + 'px';
  const end = y0 + A2_END * u;                                             // the reflection's end: the lamp under it
  pl.style.top = (end - P * .2 + Math.max(0, (F - g - end - lamp) / 2)).toFixed(1) + 'px'; pl.style.bottom = 'auto';
  ui.style.top = (F - g - (ui.offsetHeight || 95)).toFixed(1) + 'px'; ui.style.bottom = 'auto';
}
if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => fitPoster());   // (the foot's height is its font's)
addEventListener('load', () => fitPoster());
function layout() {
  fitPoster();
  // the 3D fades out behind the name above and the controls below, wherever they stand on this screen
  const tt = $('#title .lockup').getBoundingClientRect(), ui = $('#ui').getBoundingClientRect();
  fade('--fadeTop', Math.round(tt.bottom) + 'px'); fade('--fadeBot', Math.round(ui.top + 8) + 'px');
  if (!stage) return; const r = $('#frame').getBoundingClientRect(); stage.setFrame({ x: r.left, y: r.top, w: r.width, h: r.height }); stage.resize();
  // where the stone is seen: sideways, the picture's column, its full height (over and under the picture is only the
  // page's ground once the picture has gone, room the tower uses when it comes nearest); upright, between the name and
  // the controls (the 3D's mask)
  const sc = $('#stage').getBoundingClientRect();
  stage.setBand(matchMedia('(orientation: landscape)').matches ? { top: Math.min(r.top, sc.top) + 4, bottom: Math.max(r.bottom, sc.bottom) - 4, left: r.left, right: r.right }
                                                                : { top: tt.bottom, bottom: ui.top, left: 0, right: innerWidth });
  placeLamps();
}
// the 3D's mask edges, set only when they move (each change restyles the page and redraws the mask)
const fades = {};
function fade(k, v) { if (fades[k] !== v) { fades[k] = v; document.documentElement.style.setProperty(k, v); } }
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
  if (PILOT) walkedRound(az);
  // the walk's own round slowing to rest: its words hold, and प्रदक्षिणा पूर्ण follows as it stops (never the start's
  // words in between)
  if (stage.spinning && stage.roundLeft() < 3.5) { clearTimeout(waitT); want = shown; return; }
  if (state === 'walk' && performance.now() > introUntil && !hintOn) caption(sectorWord(stage.mode, az, f));
}

// the walk begins by itself, once the stone has risen (already at the walk's one size, centred: the hand-over settled
// the picture onto it): one round, easing up to a walking pace and down again, to rest where it began; the door's lamp
// brightens in its last moments and प्रदक्षिणा पूर्ण comes as it rests. A touch takes over; प्रदक्षिणा walks another
// round (or, while it walks, stops it softly); while it rests, a light goes round the dial now and then.
let held = false, inviteT = null, invites = 0;
function beginWalk() {
  introUntil = 0; onFrame(stage.az);
  if (reduce) { stage.setSettle(1); invite(); return; }
  setTimeout(() => {
    if (state !== 'walk' || !stage || stage.spinning) return;
    if (stage.settle < 1 && !stage.settleTween) stage.settleTo(1, 4500);   // the camera steps back, about the stone's centre
    if (!held) walkRound(); else invite();
  }, 500);
}
function walkRound() { clearTimeout(inviteT); $('#walk').classList.add('on'); if (beadSum >= 360) beadsFrom(); stage.spin(); }
function spinEnded(completed) {
  $('#walk').classList.remove('on');
  if (state !== 'walk') return;
  if (completed) roundDone();
  if (PILOT) invite();
}
// a touch, a key, the dial or a choice of view: the walk is theirs now
function touched() {
  held = true; clearTimeout(inviteT);
}
// the dial asks, without words: a thin light goes once round it, clockwise, every few seconds, three times at most
function invite() {
  if (!PILOT || reduce) return;
  clearTimeout(inviteT); invites = 0;
  const go = () => {
    if (state !== 'walk' || (stage && stage.spinning) || invites >= 3) return;
    if (pts.size) { inviteT = setTimeout(go, 1500); return; }                 // not while a finger is on the stone
    invites++; traceDial(); inviteT = setTimeout(go, 5200);
  };
  inviteT = setTimeout(go, 1800);
}
function traceDial() {
  const dial = $('#walk .dial'); let c = dial.querySelector('svg.trace circle');
  if (!c) { dial.insertAdjacentHTML('beforeend', '<svg class="trace" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="19"/></svg>'); c = dial.querySelector('svg.trace circle'); }
  const L = 2 * Math.PI * 19 * 1.01;
  c.animate([{ strokeDashoffset: L, opacity: 0 }, { strokeDashoffset: L * .8, opacity: 1, offset: .15 }, { strokeDashoffset: 0, opacity: 1, offset: .82 }, { strokeDashoffset: 0, opacity: 0 }],
            { duration: 1600, easing: 'cubic-bezier(.45, 0, .55, 1)' });
}

// प्रदक्षिणा पूर्ण: a full clockwise circle, back where it began (the walk's own round as it rests, or one walked by
// hand in one view): the words say so, and the door's lamp burns brighter for the rest of the visit (×1.5, 900 ms, sine
// in-out; in the walk's own round, over its last 900 ms)
let walked = 0, lastAz = null, walkMode = null, returned = false, lit = false, hintOn = false;
function walkedRound(az) {
  if (state !== 'walk' || !stage) return;
  if (stage.mode !== walkMode || lastAz === null) { walkMode = stage.mode; walked = 0; lastAz = az; beadsFrom(); return; }
  const d = ((az - lastAz) % 360 + 540) % 360 - 180;
  walked += d; lastAz = az; beadWalk(d);                                  // signed: pradakshina is clockwise (+)
  if (stage.roundLeft() <= 1.5) lampUp();                                  // (as its last beads light)
  if (returned || stage.spinning) return;                                  // the walk's own round: its words come as it rests
  const home = MODES[stage.mode].home, off = Math.abs(((az - home) % 360 + 540) % 360 - 180);
  if (walked >= 346 && off <= 14) roundDone();
}
function roundDone() {
  returned = true; walked = 0; hintOn = true;
  caption('returned', true);
  setTimeout(() => { hintOn = false; if (stage) onFrame(stage.az); }, 4500);
  lampUp();
}
// the round complete, the temple's lamps answer: the door's (or the mandapa's) lamp brighter by half, the jali by a
// quarter, together over 1.4 s, and they stay
function lampUp() {
  if (lit || !stage) return; lit = true;
  if (stage.mode === 'nandi') brighten(2, 1.5, 1400); else { brighten(1, 1.5, 1400); brighten(0, 1.25, 1400); }
}
// the dial is the wheel of the twelve Ādityas (page.html): a bead every 30° round the building, from its front at the
// dial's top; each lights as the visitor's place reaches it walking clockwise and goes out again walking back (1.5° behind
// it, so a place that rests on a bead never flickers it); at 360° the wheel is whole. A new round (the dial) starts it
// again, as does another view
const beads = [...document.querySelectorAll('#walk .dial b')];
let bead0 = 0, beadSum = 0;
function beadsFrom() { bead0 = stage ? stage.facing() : 0; beadSum = 0; paintBeads(); }
function beadWalk(d) { beadSum = Math.max(-30, Math.min(400, beadSum + d)); paintBeads(); }
function paintBeads() {
  beads.forEach((b, k) => {
    const at = ((30 * k - bead0) % 360 + 360) % 360 || 360;              // how far round, from the start, this bead stands
    if (beadSum >= Math.min(at - .5, 360)) b.classList.add('lit'); else if (beadSum < at - 2) b.classList.remove('lit');
  });
}
function brighten(i, k, ms) {
  const m = stage.glows && stage.glows[i]; if (!m) return;
  const from = m.opacity, to = Math.min(1, from * k), t0 = performance.now();
  const tick = (now) => {
    const p = Math.min(1, (now - t0) / ms); m.opacity = from + (to - from) * (.5 - .5 * Math.cos(Math.PI * p));
    stage.dirty = true; stage.wake(); if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
function markMode(name) { $$('#modes button').forEach((b) => b.classList.toggle('on', b.dataset.mode === name)); }

// drag sideways to walk round (the building turns with the finger), flick to keep going, pinch to come closer
const gl = $('#gl'); const pts = new Map(); let drag = null, pinch = null;
const dist = (a, b) => Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
const degPerPx = () => 300 / Math.max(320, stage.frame.w * 1.6);
gl.addEventListener('pointerdown', (e) => {
  if (state !== 'walk' || !stage) return;
  touched();
  gl.setPointerCapture(e.pointerId); pts.set(e.pointerId, e); stage.stopSpin(); stage.vel = 0;
  if (pts.size === 1) drag = { last: e.clientX, t: performance.now(), v: 0 };
  if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: dist(a, b), z: stage.zoom }; drag = null; }
});
gl.addEventListener('pointermove', (e) => {
  if (!pts.has(e.pointerId) || !stage) return; pts.set(e.pointerId, e);
  if (pinch && pts.size === 2) { const [a, b] = [...pts.values()]; stage.zoom = Math.max(.8, Math.min(2.2, pinch.z * dist(a, b) / pinch.d)); stage.dirty = true; stage.wake(); return; }
  if (drag) {
    const now = performance.now(), dx = e.clientX - drag.last, d = dx * degPerPx();
    stage.rotate(d); drag.v = .7 * drag.v + .3 * (d / Math.max(8, now - drag.t) * 1000); drag.last = e.clientX; drag.t = now;
  }
});
const lift = (e) => {
  pts.delete(e.pointerId); if (pts.size < 2) pinch = null;
  if (drag && pts.size === 0) { if (stage && performance.now() - drag.t < 90) stage.fling(drag.v); drag = null; }
};
gl.addEventListener('pointerup', lift); gl.addEventListener('pointercancel', lift);
gl.addEventListener('wheel', (e) => { if (state !== 'walk' || !stage) return; e.preventDefault(); stage.zoom = Math.max(.8, Math.min(2.2, stage.zoom * (1 - e.deltaY * .0012))); stage.dirty = true; }, { passive: false });
addEventListener('keydown', (e) => {
  if (state !== 'walk' || !stage) return;
  if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') touched();
  if (e.key === 'ArrowRight') { stage.stopSpin(); stage.fling(140); }
  if (e.key === 'ArrowLeft') { stage.stopSpin(); stage.fling(-140); }
});

// प्रदक्षिणा: walk round once more, keeping it on your right; while it walks, it stops softly
$('#walk').addEventListener('click', () => {
  if (!stage || state !== 'walk') return;
  touched();
  if (stage.spinning) stage.stopSpin(true); else walkRound();
});

// what to walk round: the temple, Nandi's mandapa, or the whole complex; the view dips to the night and comes back on it
$('#modes').addEventListener('click', (e) => {
  const b = e.target.closest('button[data-mode]'); if (!b || state !== 'walk') return;
  touched();
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
  const text = 'ग्राम पहाड़ीखेड़ा, जबलपुर में निर्माणाधीन · ऋतम्भरेश्वर मंदिर';
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

// the loader's handshake: every control above is wired (intro.js lifts onto a working lamp, or hides it)
dispatchEvent(new Event('rtam:app-ready'));
