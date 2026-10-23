// The opening, on the tour's pages (<html data-pilot="1" class="intro">; S1 of the finishing pass, 22 Oct 2026). The
// Ṛta-chakra alone on the night ground, in a faint warm light outside its ring, turning slowly while the page makes
// itself ready behind it. Then it brakes and comes to rest upright (motion.js), and dissolves as the temple rises by its
// own light where the chakra was: first the door's thread of lamplight and the temple at dusk, then the name, the lamp
// and the foot together. No words, no bar, no tap to skip.
// Ready = the fonts (2.5 s at most), the temple's picture, and the page's own script (app.js: rtam:app-ready); the 3D
// keeps arriving behind the landing. It turns 4.5 to 10.5 s; under reduced motion it stands upright and still for
// 1.2 s at least. Skipped with ?skip. Should this script never run, the page's CSS shows the landing by itself.
import { TURN, brakeAt, angleAt } from './motion.js';

const html = document.documentElement, $ = (s) => document.querySelector(s);
const SINE = 'cubic-bezier(.37, 0, .63, 1)', EXPO = 'cubic-bezier(.16, 1, .3, 1)';   // the brand's reveal, and a lamp's ignition
let appReady = false;                                     // app.js's handshake: every control is wired
addEventListener('rtam:app-ready', () => { appReady = true; }, { once: true });

// rtam:ready: the page is ready (the 3D may start arriving: it never competes with the landing); rtam:intro-done: the
// landing is up (the film's bytes may come)
const ready = () => { if (!html.dataset.ready) { html.dataset.ready = '1'; dispatchEvent(new Event('rtam:ready')); } };
if (!Element.prototype.animate || /[?&]skip\b/.test(location.search)) { html.classList.remove('intro'); ready(); dispatchEvent(new Event('rtam:intro-done')); }
else open();

function open() {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const play = $('#play'), still = $('#still'), thread = $('#thread');
  play.hidden = false;                                    // laid out beneath, so it is ready the moment it shows
  // what the landing brings, held unseen until the opening hands over (their own CSS fades held off meanwhile, or a
  // fade of theirs would show through). At a thousandth, not nothing: already painted and on the GPU, so the dissolve
  // needs no first paint from a main thread that may be busy taking the 3D apart
  const words = ['#title .kicker', '#title .lockup', '#title .lotus', '#foot', '#play'].map($).filter(Boolean);
  const held = [still, thread, ...words].filter(Boolean);
  for (const el of held) { el.style.transition = 'none'; el.style.opacity = '.001'; }
  html.classList.add('intro-run'); html.classList.remove('intro');     // the opening owns the landing from here

  // the mark (the garbhagriha register: bhasma ash, mahakala windows and seams, the gold bindu), in its own light
  const PETAL = 'M 245.5 182.4 C 239 176 230.5 164 227.5 148 C 225.6 130 242 108 256 95 C 270 108 286.4 130 284.5 148 C 281.5 164 273 176 266.5 182.4 Z';
  let mark = '<svg class="ck" viewBox="0 0 512 512"><circle cx="256" cy="256" r="213.5" fill="none" stroke="#C9C2B6" stroke-width="33"/>';
  for (let k = 0; k < 12; k++) mark += `<circle cx="256" cy="44.4" r="10.35" fill="#141414" transform="rotate(${30 * k} 256 256)"/>`;
  for (let k = 0; k < 12; k++) mark += `<path d="${PETAL}" fill="#C9C2B6" stroke="#141414" stroke-width="5" stroke-linejoin="round" transform="rotate(${30 * k} 256 256)"/>`;
  mark += '<circle cx="256" cy="256" r="50.6" fill="#C8A15A"/></svg>';
  const box = document.createElement('div'); box.id = 'intro'; box.setAttribute('aria-hidden', 'true');
  box.innerHTML = `<div class="lt"><canvas></canvas>${mark}</div>`;
  const lt = box.firstChild, halo = lt.firstChild, ck = lt.lastChild;
  // in the centre of what is visible, upright or sideways (Harsh, 22 Oct: "the icon has to be centered"; a phone's fixed
  // layer can be taller than the screen while the browser's bars show); a third of the shorter side, 112-160 px
  let size = 0;
  const place = () => {
    const vv = window.visualViewport, W = vv ? vv.width : innerWidth, H = vv ? vv.height : innerHeight;
    const s = Math.round(Math.min(160, Math.max(112, Math.min(W, H) * .34)));
    box.style.setProperty('--x', Math.round((vv ? vv.offsetLeft : 0) + W / 2) + 'px'); box.style.setProperty('--y', Math.round((vv ? vv.offsetTop : 0) + H / 2) + 'px');
    box.style.setProperty('--s', s + 'px');
    if (s !== size) { size = s; drawHalo(halo, s); }
  };
  place();
  document.body.appendChild(box);
  addEventListener('resize', place); if (window.visualViewport) visualViewport.addEventListener('resize', place);   // (the bars come and go)

  const anims = [], now = () => document.timeline.currentTime;
  const at = (el, frames, ms, start, easing) => {            // an animation starting at a moment of the document's timeline
    const a = el.animate(frames, { duration: ms, easing, fill: 'forwards' }); if (start !== undefined) a.startTime = start;
    anims.push(a); return a;
  };
  at(lt, [{ opacity: 0 }, { opacity: 1 }], reduce ? 300 : 900, undefined, SINE);
  let turn = reduce ? null : ck.animate([{ transform: 'rotate(0deg)' }, { transform: 'rotate(360deg)' }], { duration: 36000, iterations: Infinity });

  // ready: the fonts (2.5 s at most), the temple's picture, the page's script; at 7.5 s it brakes regardless
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const fonts = document.fonts && document.fonts.load
    ? Promise.race([Promise.all([document.fonts.load('400 16px Tiro'), document.fonts.load('500 10px Cinzel')]).catch(() => {}), wait(2500)]) : null;
  const picture = still.decode ? still.decode().catch(() => {}) : null;
  const page = appReady ? null : new Promise((r) => addEventListener('rtam:app-ready', r, { once: true }));
  const started = (turn ? turn.ready : Promise.resolve()).then(() => (turn ? turn.startTime : now()));
  started.then((t0) => {
    let decided = false;
    const decide = () => {
      if (decided) return; decided = true; ready();
      const readyAt = (now() - t0) / 1000;
      if (reduce) { dissolve(Math.max(now(), t0 + 1200), true); return; }
      // the turn as one animation from its start: steady, then braking from its slot to rest upright (the same curve
      // as motion.js, sampled finely; it carries on from where the steady turn is, so the hand-over never shows)
      const b = brakeAt(readyAt), end = b + TURN.brake, frames = [{ transform: 'rotate(0deg)', offset: 0 }];
      for (let i = 0; i <= 40; i++) { const t = b + TURN.brake * i / 40; frames.push({ transform: `rotate(${angleAt(t, readyAt).toFixed(4)}deg)`, offset: t / end }); }
      const a = ck.animate(frames, { duration: end * 1000, fill: 'forwards' }); a.startTime = t0; turn.cancel(); turn = a;
      dissolve(t0 + (end + .3) * 1000, false);            // a breath at rest, then the light changes hands
    };
    Promise.all([fonts, picture, page]).then(decide);
    setTimeout(decide, Math.max(0, t0 + TURN.slots[TURN.slots.length - 1] * 1000 - 60 - now()));
  });

  // the dissolve, in two beats from D (S1). Light: the chakra fades (900 ms) as the door's thread ignites (400 ms, to
  // full, then settling) and the temple floods in (1600 ms, from 300 ms), so the two are never seen at once and the
  // frame is never black; the chakra's own light lingers 400 ms longer, so warm light is there as the stone arrives.
  // Then the name, the lamp and the foot, together (900 ms, from 1400 ms). Under reduced motion, all within 600 ms.
  function dissolve(D, quick) {
    const k = quick ? .3 : 1;
    at(ck, [{ opacity: 1 }, { opacity: 0 }], 900 * k, D, SINE);
    at(halo, [{ opacity: 1 }, { opacity: 0 }], 1300 * k, D, SINE);
    if (thread) { at(thread, [{ opacity: 0 }, { opacity: 1 }], 400 * k, D, EXPO); at(thread, [{ opacity: 1 }, { opacity: .85 }], 600 * k, D + 400 * k, SINE); }
    at(still, [{ opacity: 0 }, { opacity: 1 }], quick ? 400 : 1600, D + 300 * k, SINE);
    let last = null;
    for (const el of words) last = at(el, [{ opacity: 0 }, { opacity: 1 }], quick ? 400 : 900, D + (quick ? 200 : 1400), SINE);
    // from the second beat a tap reaches the page: on the lamp it lights the lamps, and the opening steps aside at once
    setTimeout(() => {
      box.style.pointerEvents = 'none';
      if (!appReady) play.hidden = true;                  // the page's script has not come: no lamp that does nothing yet
      document.addEventListener('click', done, { capture: true, once: true });
    }, Math.max(0, D + (quick ? 200 : 1400) - now()));
    last.finished.then(done, done);
  }
  setTimeout(done, 16000);                                // whatever happens, the landing by 16 s

  function done() {
    if (done.on) return; done.on = true;
    document.removeEventListener('click', done, true); removeEventListener('resize', place);
    if (window.visualViewport) visualViewport.removeEventListener('resize', place);
    for (const el of held) el.style.opacity = '';         // their own CSS again (the animations hold them meanwhile)
    for (const a of anims) a.cancel();
    if (turn) turn.cancel();
    ready(); html.classList.remove('intro-run');                   // the lamp and the door's thread begin to breathe
    box.remove();
    requestAnimationFrame(() => requestAnimationFrame(() => { for (const el of held) el.style.transition = ''; }));
    dispatchEvent(new Event('rtam:intro-done'));
  }
  // the page's script came after the landing (a slow line): its lamp comes by light, not at a blink
  addEventListener('rtam:app-ready', () => { if (done.on || box.style.pointerEvents === 'none') play.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 900, easing: SINE }); }, { once: true });
}

// The chakra's own light: the lamp's colour at a tenth of its strength (rgb(42,40,34) at its brightest), from the ring's
// outer edge outward, gone by 2.2× the mark. Nothing inside the ring (35 % of the halo's radius is the ring's inner
// edge), so the mark's dark seams never show against it. Dithered at the screen's own pixels, so no cheap screen bands.
function drawHalo(cv, s) {
  const d = Math.min(2, devicePixelRatio || 1), n = Math.round(2.2 * s * d), g = cv.getContext('2d');
  cv.width = cv.height = n;
  const img = g.createImageData(n, n), px = img.data, c = (n - 1) / 2, R = n / 2;
  const G = 20, L = [243, 217, 160], K = .1, lut = new Float32Array(1025);
  const ss = (u) => (u <= 0 ? 0 : u >= 1 ? 1 : u * u * (3 - 2 * u));
  for (let i = 0; i <= 1024; i++) {
    const r = Math.sqrt(i / 1024);
    lut[i] = K * ss((r - .35) / .07) * Math.exp(-(((Math.max(r, .42) - .42) / .2) ** 2)) * (1 - ss((r - .78) / .22));
  }
  let seed = 2463534242;
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const o = (y * n + x) * 4, dx = (x - c) / R, dy = (y - c) / R, q = dx * dx + dy * dy;
    px[o + 3] = 255;
    const f = q < 1 ? lut[(q * 1024) | 0] : 0;
    if (!f) { px[o] = px[o + 1] = px[o + 2] = G; continue; }
    seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5;          // xorshift: a triangular dither of ±1 level
    const e = ((seed & 0xffff) + (seed >>> 16 & 0xffff)) / 65536 - 1;
    for (let ch = 0; ch < 3; ch++) px[o + ch] = Math.round(G + f * (L[ch] - G) + e);
  }
  g.putImageData(img, 0, 0);
}
