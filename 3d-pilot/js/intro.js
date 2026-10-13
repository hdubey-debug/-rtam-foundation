// The opening, on the pilot pages (<html data-pilot="1" class="intro">), as Harsh asked on 13 Oct 2026. Before the page,
// the Ṛta-chakra is built in the middle of the screen: the bindu alone and still; the 12 petals one by one, clockwise from
// the top (the order of pradakshina); the ring; the 12 Ādityas one by one. No words. Nothing is moved once it is made: the
// finished mark dims where it stands as the landing rises by light (the temple at dusk, then the name, then the lamp).
// A touch skips to the landing (and doesn't light the lamps). Skipped under reduced motion and with ?skip.
// The choreography is the same code as the HyperFrames films (motion-skills/hf-chakra, js/chakra.js; film I6).
(function () {
  const html = document.documentElement, C = window.RtaChakra, G = window.gsap;
  const finish = () => { html.classList.remove('intro'); };
  if (!C || !G || matchMedia('(prefers-reduced-motion: reduce)').matches || /[?&]skip\b/.test(location.search)) { finish(); return; }
  const $ = (s) => document.querySelector(s), NS = 'http://www.w3.org/2000/svg';
  const play = $('#play'); play.hidden = false;

  // the mark in the middle of the screen: half the shorter side, at most 360 px
  const W = innerWidth, H = innerHeight, size = Math.min(360, Math.min(W, H) * .5), k = size / 512;
  const svg = document.createElementNS(NS, 'svg'); svg.id = 'intro';
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('aria-hidden', 'true');
  const g = document.createElementNS(NS, 'g'); g.setAttribute('transform', `translate(${W / 2 - 256 * k} ${H / 2 - 256 * k}) scale(${k})`); svg.appendChild(g);
  const holder = document.createElementNS(NS, 'svg'); holder.setAttribute('width', 512); holder.setAttribute('height', 512); holder.setAttribute('overflow', 'visible'); g.appendChild(holder);
  document.body.appendChild(svg);
  const p = C.build(holder);

  // what the landing brings, in place. Hidden at once with their own CSS fades held off: otherwise a child fading out
  // (1 → 0) inside a parent fading in (the name's block, 0 → 1, as .intro comes off) shows faintly for half a second.
  const titleParts = ['#title .kicker', '#title .lockup'].map($).filter(Boolean);
  const marks = ['#title .lotus', '#foot .lotus'].map($).filter(Boolean);
  const after = ['#still', '#foot', '#play .lamp', '#play > span:nth-child(2)', '#play .en'].map($).filter(Boolean);
  const thread = $('#thread');
  G.set([...titleParts, ...after, ...marks], { opacity: 0, transition: 'none' });
  html.classList.add('intro-run'); html.classList.remove('intro');   // the overlay owns the hiding from here; the lamp waits

  const tl = G.timeline({ onComplete: done });
  let t = C.petalsInOrder(tl, p, 1.2);                              // the bindu alone; then the petals, one every 0.3 s
  t = C.traceRing(tl, p, t - .2, 1.5);                              // the ring, clockwise from the top
  t = C.adityasIn(tl, p, t + .15);                                  // the twelve, one by one
  const h = t + .85;                                                // the finished mark, held
  tl.to(svg, { opacity: 0, duration: .8, ease: 'power2.in' }, h);   // it dims where it stands, all of it at once
  // the temple rises only once the mark is nearly gone (both at once reads as a watermark on the stone)
  tl.to('#still', { opacity: 1, duration: 1.4, ease: 'sine.inOut' }, h + .55);
  if (thread) tl.fromTo(thread, { opacity: 0 }, { opacity: .15, duration: 1, ease: 'sine.inOut', immediateRender: false }, h + 1.1);
  tl.to([...titleParts, ...marks], { opacity: 1, duration: .8, ease: 'sine.out', stagger: .15 }, h + 1.1);    // the name
  tl.to(after.filter((e) => e.id !== 'still'), { opacity: 1, duration: .6, ease: 'sine.out', stagger: .08 }, h + 1.7);   // the lamp, last

  // a touch before the end: straight to the landing
  const skip = (e) => {
    e.preventDefault(); e.stopPropagation();
    const swallow = (c) => { c.stopPropagation(); c.preventDefault(); };   // the click that ends this touch must not light the lamps
    addEventListener('click', swallow, { capture: true, once: true }); setTimeout(() => removeEventListener('click', swallow, true), 700);
    tl.progress(1);
  };
  svg.addEventListener('pointerdown', skip);
  // a turn of the phone ends it (the overlay was laid out for the old shape). Only a real change counts: phones also send
  // resize as the page loads and as the address bar slides, at the same width.
  const turned = () => { if (Math.abs(innerWidth - W) > 40 || (innerWidth > innerHeight) !== (W > H)) tl.progress(1); };
  addEventListener('resize', turned);

  function done() {
    removeEventListener('resize', turned);
    G.set([...titleParts, ...after, ...marks, thread].filter(Boolean), { clearProps: 'opacity,transition' });
    html.classList.remove('intro-run');                            // the lamp begins to breathe; the thread, its own breath
    svg.remove();
  }
})();
