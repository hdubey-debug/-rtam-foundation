// The opening, on the pilot pages (<html data-pilot="1" class="intro">): a loader, as on the first temple-3d page that
// Harsh liked (23 Oct 2026: "no video… where the icon is, we show that it's loading… add some flare"). The Ṛta-chakra
// turns slowly in its own glow above the temple's name, and a thin line fills as the 3D arrives (no bytes shown); a
// warmer light gathers behind the chakra with it. The 3D is downloaded and prepared behind it (app.js: rtam:progress,
// rtam:stage), so the landing is ready when it lifts. It holds at least 3.6 s ("let the chakra breathe", his call on that
// page) and at most 10 s; then the line closes, the light swells once, and it fades as the landing rises by light (the
// temple at dusk, the name, the lamp). A touch goes straight to the landing (and doesn't light the lamps). Skipped with
// ?skip; under reduced motion it holds still.
(function () {
  const html = document.documentElement, G = window.gsap;
  const finish = () => { html.classList.remove('intro'); };
  if (!G || /[?&]skip\b/.test(location.search)) { finish(); return; }
  const $ = (s) => document.querySelector(s);
  const MIN = 3600, MAX = 10000, shownAt = performance.now();
  const play = $('#play'); play.hidden = false;

  // the mark (the garbhagriha register: bhasma ash, mahakala windows and seams, the gold bindu)
  const PETAL = 'M 245.5 182.4 C 239 176 230.5 164 227.5 148 C 225.6 130 242 108 256 95 C 270 108 286.4 130 284.5 148 C 281.5 164 273 176 266.5 182.4 Z';
  let mark = '<svg class="ck" viewBox="0 0 512 512" aria-hidden="true"><circle cx="256" cy="256" r="213.5" fill="none" stroke="#C9C2B6" stroke-width="33"/>';
  for (let k = 0; k < 12; k++) mark += `<circle cx="256" cy="44.4" r="10.35" fill="#141414" transform="rotate(${30 * k} 256 256)"/>`;
  for (let k = 0; k < 12; k++) mark += `<path d="${PETAL}" fill="#C9C2B6" stroke="#141414" stroke-width="5" stroke-linejoin="round" transform="rotate(${30 * k} 256 256)"/>`;
  mark += '<circle cx="256" cy="256" r="50.6" fill="#C8A15A"/></svg>';

  const box = document.createElement('div'); box.id = 'intro'; box.setAttribute('aria-hidden', 'true');
  box.innerHTML = `<div class="ld"><div class="mk"><i class="halo"></i><i class="glow"></i>${mark}</div>` +
    '<div class="nm">ऋतम्भरेश्वर मंदिर</div><div class="sb">The temple, in three dimensions</div><div class="bar"><i></i></div></div>';
  // in the middle of what is visible (a phone's 100vh is the screen without its browser bars); re-centred when the phone
  // turns or the bars come and go. The chakra: about a third of the shorter side, 112 to 156 px.
  const place = () => {
    const vv = window.visualViewport, W = Math.round(vv ? vv.width : innerWidth), H = Math.round(vv ? vv.height : innerHeight);
    box.style.width = W + 'px'; box.style.height = H + 'px';
    box.style.setProperty('--s', Math.round(Math.min(156, Math.max(112, Math.min(W, H) * .32))) + 'px');
  };
  place();
  document.body.appendChild(box);

  // what the landing brings, in place. Hidden at once with their own CSS fades held off: otherwise a child fading out
  // (1 → 0) inside a parent fading in (the name's block, 0 → 1, as .intro comes off) shows faintly for half a second.
  const titleParts = ['#title .kicker', '#title .lockup'].map($).filter(Boolean);
  const marks = ['#title .lotus', '#foot .lotus'].map($).filter(Boolean);
  const after = ['#still', '#foot', '#play .lamp', '#play > span:nth-child(2)', '#play .en'].map($).filter(Boolean);
  const thread = $('#thread');
  G.set([...titleParts, ...after, ...marks], { opacity: 0, transition: 'none' });
  html.classList.add('intro-run'); html.classList.remove('intro');   // the loader owns the hiding from here; the lamp waits

  // what is arriving: the fonts, the picture of the temple at dusk, and the 3D (its bytes, then its preparation)
  const got = { fonts: 0, still: 0, stage: 0, staged: false };
  const show = () => {
    const p = .1 * got.fonts + .15 * got.still + .75 * got.stage;
    box.style.setProperty('--p', Math.min(1, p).toFixed(3));
    if (got.fonts && got.still && got.staged) ready();
  };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { got.fonts = 1; show(); }); else got.fonts = 1;
  const still = $('#still');
  const stillDone = () => { got.still = 1; show(); };
  if (!still || still.complete) stillDone();
  else { still.addEventListener('load', stillDone, { once: true }); still.addEventListener('error', stillDone, { once: true }); }
  addEventListener('rtam:progress', (e) => { got.stage = Math.max(got.stage, .9 * e.detail); show(); });   // bytes: 90 %
  addEventListener('rtam:stage', () => { got.stage = 1; got.staged = true; show(); }, { once: true });  // drawn: the rest

  // the landing: the line closes and the light swells once; the loader fades where it stands; the temple's light begins
  // as it is nearly gone (never a black frame, never the two at once); then the name; the lamp last
  const tl = G.timeline({ onComplete: done, paused: true });
  tl.to(box, { opacity: 0, duration: .9, ease: 'sine.inOut' }, .45);
  tl.to('#still', { opacity: 1, duration: 1.4, ease: 'sine.inOut' }, .85);
  if (thread) tl.fromTo(thread, { opacity: 0 }, { opacity: .15, duration: 1, ease: 'sine.inOut', immediateRender: false }, 1.35);
  tl.to([...titleParts, ...marks], { opacity: 1, duration: .8, ease: 'sine.out', stagger: .15 }, 1.35);
  tl.to(after.filter((e) => e.id !== 'still'), { opacity: 1, duration: .6, ease: 'sine.out', stagger: .08 }, 1.95);
  const lift = () => {
    if (lift.on) return; lift.on = true;
    got.stage = Math.max(got.stage, got.staged ? 1 : got.stage);
    box.style.setProperty('--p', '1'); box.classList.add('done');
    tl.play();
  };
  function ready() { if (!ready.on) { ready.on = true; setTimeout(lift, Math.max(0, MIN - (performance.now() - shownAt))); } }
  const longest = setTimeout(lift, MAX);                            // a slow line: the landing comes; the 3D keeps arriving

  // a touch: straight to the landing
  const skip = (e) => {
    e.preventDefault(); e.stopPropagation();
    const swallow = (c) => { c.stopPropagation(); c.preventDefault(); };   // the click that ends this touch must not light the lamps
    addEventListener('click', swallow, { capture: true, once: true }); setTimeout(() => removeEventListener('click', swallow, true), 700);
    lift(); tl.progress(1);
  };
  box.addEventListener('pointerdown', skip);
  const turned = () => place();
  addEventListener('resize', turned); if (window.visualViewport) visualViewport.addEventListener('resize', turned);

  function done() {
    clearTimeout(longest);
    removeEventListener('resize', turned); if (window.visualViewport) visualViewport.removeEventListener('resize', turned);
    G.set([...titleParts, ...after, ...marks, thread].filter(Boolean), { clearProps: 'opacity,transition' });
    html.classList.remove('intro-run');                            // the lamp begins to breathe; the thread, its own breath
    box.remove();
    dispatchEvent(new Event('rtam:intro-done'));
  }
})();
