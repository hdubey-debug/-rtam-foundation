// The opening, on the pilot pages (<html data-pilot="1" class="intro">): before the page, a short film of the Ṛta-chakra
// made as a real object (ash-stone petals and ring in Shivalinga-black stone, a gold bindu; motion-skills/icon3d, 21 Oct
// 2026). Harsh's order holds: the bindu alone; the 12 petals one by one clockwise from the top; the ring and its 12
// windows. No words. Three films to compare on the phone: ?open=darshan (the default; the view rises from the bindu),
// ?open=dipamala (from above, lit part by part), ?open=kamal (the petals laid open one by one). The film plays in the
// middle of what is visible; its last frame dims where it stands as the landing rises by light (the temple at dusk, the
// name, the lamp). A touch skips to the landing (and doesn't light the lamps). Skipped under reduced motion, with ?skip,
// and when the phone won't play it (no autoplay, as in iOS Low Power Mode, or not begun within 6 s).
(function () {
  const html = document.documentElement, G = window.gsap;
  const finish = () => { html.classList.remove('intro'); };
  if (!G || matchMedia('(prefers-reduced-motion: reduce)').matches || /[?&]skip\b/.test(location.search)) { finish(); return; }
  const FILMS = { darshan: 8.4, dipamala: 8.4, kamal: 8.8 };
  const m = /[?&]open=([a-z]+)/.exec(location.search), film = m && FILMS[m[1]] ? m[1] : 'darshan';
  const $ = (s) => document.querySelector(s);
  const play = $('#play'); play.hidden = false;

  // the film in the middle of what is visible, its mark as large as the drawn mark was (the film's frame is 640 mm for a
  // 460 mm mark: 1.25 × half the shorter side, at most 450 px). Sized in px from the visual viewport (a phone's 100vh is
  // the screen without its browser bars); re-centred when the phone turns or the bars come and go, and it plays on.
  const box = document.createElement('div'); box.id = 'intro'; box.setAttribute('aria-hidden', 'true');
  const v = document.createElement('video');
  v.muted = true; v.defaultMuted = true; v.playsInline = true; v.preload = 'auto';
  for (const a of ['muted', 'playsinline', 'disablepictureinpicture', 'disableremoteplayback']) v.setAttribute(a, '');
  v.src = `media/open-${film}-720.mp4`;
  box.appendChild(v);
  const place = () => {
    const vv = window.visualViewport, W = Math.round(vv ? vv.width : innerWidth), H = Math.round(vv ? vv.height : innerHeight);
    const s = Math.round(Math.min(450, Math.min(W, H) * .625));
    box.style.width = W + 'px'; box.style.height = H + 'px';
    Object.assign(v.style, { width: s + 'px', height: s + 'px', left: Math.round((W - s) / 2) + 'px', top: Math.round((H - s) / 2) + 'px' });
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
  html.classList.add('intro-run'); html.classList.remove('intro');   // the overlay owns the hiding from here; the lamp waits

  // the landing: the film's last frame dims where it stands; the temple's light begins as the mark is nearly gone, so
  // there is never a black frame nor the two at once; then the name; the lamp last
  const tl = G.timeline({ onComplete: done, paused: true });
  tl.to(box, { opacity: 0, duration: 1.0, ease: 'sine.inOut' }, 0);
  tl.to('#still', { opacity: 1, duration: 1.4, ease: 'sine.inOut' }, .6);
  if (thread) tl.fromTo(thread, { opacity: 0 }, { opacity: .15, duration: 1, ease: 'sine.inOut', immediateRender: false }, 1.1);
  tl.to([...titleParts, ...marks], { opacity: 1, duration: .8, ease: 'sine.out', stagger: .15 }, 1.1);
  tl.to(after.filter((e) => e.id !== 'still'), { opacity: 1, duration: .6, ease: 'sine.out', stagger: .08 }, 1.7);
  const land = () => { if (!land.on) { land.on = true; tl.play(); } };
  const abort = () => { v.pause(); land(); tl.progress(1); };       // straight to the landing

  // the film shows from its first played frame (until then the box is empty ground, never a black square)
  v.style.opacity = '0';
  v.addEventListener('playing', () => {
    v.style.opacity = '1'; clearTimeout(watchdog);
    setTimeout(land, (FILMS[film] + 2.5) * 1000);                    // should 'ended' never come
  }, { once: true });
  v.addEventListener('ended', land);
  const watchdog = setTimeout(abort, 6000);                         // not begun in 6 s (a slow line): the page directly
  const p = v.play(); if (p && p.catch) p.catch(abort);             // autoplay refused (Low Power Mode): the page directly

  // a touch before the end: straight to the landing
  const skip = (e) => {
    e.preventDefault(); e.stopPropagation();
    const swallow = (c) => { c.stopPropagation(); c.preventDefault(); };   // the click that ends this touch must not light the lamps
    addEventListener('click', swallow, { capture: true, once: true }); setTimeout(() => removeEventListener('click', swallow, true), 700);
    abort();
  };
  box.addEventListener('pointerdown', skip);
  const turned = () => place();
  addEventListener('resize', turned); if (window.visualViewport) visualViewport.addEventListener('resize', turned);

  function done() {
    clearTimeout(watchdog);
    removeEventListener('resize', turned); if (window.visualViewport) visualViewport.removeEventListener('resize', turned);
    G.set([...titleParts, ...after, ...marks, thread].filter(Boolean), { clearProps: 'opacity,transition' });
    html.classList.remove('intro-run');                            // the lamp begins to breathe; the thread, its own breath
    v.removeAttribute('src'); v.load(); box.remove();               // let the film's memory go
    dispatchEvent(new Event('rtam:intro-done'));                    // (app.js: now the 3D may load)
  }
})();
