// The opening, on the pilot pages (<html data-pilot="1" class="intro">). Before the page, the Ṛta-chakra comes into being
// where the temple will stand: the bindu alone (it is there from the first frame and never leaves); prakriti blooms,
// 24 tattvas of which 12 are seen; ṛta begins and a month turns, while the name appears in its own place. Then all of it
// returns into the bindu (the Ādityas first, then prakriti), and the bindu descends to the lamp and becomes its flame,
// as the temple at dusk rises around it. The visitor touches that flame to light the lamps. A touch earlier skips here.
// The choreography is the same code as the HyperFrames films (motion-skills/hf-chakra, js/chakra.js).
(function () {
  const html = document.documentElement, C = window.RtaChakra, G = window.gsap;
  const finish = () => { html.classList.remove('intro'); };
  if (!C || !G || !window.MorphSVGPlugin || matchMedia('(prefers-reduced-motion: reduce)').matches || /[?&]skip\b/.test(location.search)) { finish(); return; }
  G.registerPlugin(window.MorphSVGPlugin);
  const $ = (s) => document.querySelector(s), NS = 'http://www.w3.org/2000/svg';
  const play = $('#play'); play.hidden = false;

  // where things are: the picture area (the chakra fills most of it) and the lamp's flame
  const fr = $('#frame').getBoundingClientRect(), W = innerWidth, H = innerHeight;
  const size = Math.min(fr.width, fr.height) * .92, k = size / 512, ox = fr.left + fr.width / 2 - 256 * k, oy = fr.top + fr.height / 2 - 256 * k;
  const lamp = $('#play .lamp').getBoundingClientRect();
  const icon = 24 * Math.min(lamp.width, lamp.height) / 60;      // the flame's 24-unit icon, as the lamp draws it
  const ix = lamp.left + lamp.width / 2 - icon / 2, iy = lamp.top + lamp.height / 2 - icon / 2, u = icon / 24;
  const L = (x, y) => `${(((ix + x * u) - ox) / k).toFixed(2)} ${(((iy + y * u) - oy) / k).toFixed(2)}`;
  const FLAME = `M ${L(12, 2.5)} C ${L(15, 6.4)} ${L(16.6, 9.2)} ${L(16.6, 11.8)} C ${L(16.6, 14.34)} ${L(14.54, 16.4)} ${L(12, 16.4)} ` +
                `C ${L(9.46, 16.4)} ${L(7.4, 14.34)} ${L(7.4, 11.8)} C ${L(7.4, 9.2)} ${L(9, 6.4)} ${L(12, 2.5)} Z`;

  // the overlay: the whole screen, in CSS px; the chakra drawn in its own 512-unit square at the picture's centre
  const svg = document.createElementNS(NS, 'svg'); svg.id = 'intro';
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('aria-hidden', 'true');
  const g = document.createElementNS(NS, 'g'); g.setAttribute('transform', `translate(${ox} ${oy}) scale(${k})`); svg.appendChild(g);
  const holder = document.createElementNS(NS, 'svg'); holder.setAttribute('width', 512); holder.setAttribute('height', 512); holder.setAttribute('overflow', 'visible'); g.appendChild(holder);
  document.body.appendChild(svg);
  const p = C.build(holder);

  // what the opening reveals, in place
  const titleParts = ['#title .kicker', '#title .lockup'].map($).filter(Boolean);
  const after = ['#still', '#foot', '#play .lamp', '#play > span:nth-child(2)', '#play .en'].map($).filter(Boolean);   // (the header's lotus keeps its own rules)
  G.set([...titleParts, ...after], { opacity: 0 });
  html.classList.add('intro-run'); html.classList.remove('intro');   // the overlay owns the hiding from here; the lamp waits

  const tl = G.timeline({ onComplete: done });
  let t = C.bloom24(tl, p, .35, { stagger: .035, gap: .35, tuck: .5 });
  const tr = t - .15; t = C.traceRta(tl, p, tr, 1.0);
  tl.to(titleParts, { opacity: 1, duration: .9, ease: 'sine.out', stagger: .2 }, tr + .15);     // the name arrives as time begins
  t = C.turnMonths(tl, p, t + .05, 1, { step: .7 });
  t = C.untraceRta(tl, p, t + .35, .7);                                                         // the Ādityas go first
  t = C.withdraw24(tl, p, t, { stagger: .025 });                                                // then prakriti; the bindu stays
  tl.to(p.bindu, { morphSVG: FLAME, duration: .95, ease: 'power3.inOut' }, t);                   // and becomes the lamp's flame
  tl.to('#still', { opacity: 1, duration: 1.2, ease: 'sine.inOut' }, t + .1);                    // the temple at dusk, by light
  tl.to(after.filter((e) => e.id !== 'still'), { opacity: 1, duration: .6, ease: 'sine.out', stagger: .08 }, t + .75);
  // a touch before the end: straight to the lamp
  const skip = (e) => {
    e.preventDefault(); e.stopPropagation();
    const swallow = (c) => { c.stopPropagation(); c.preventDefault(); };   // the click that ends this touch must not light the lamps
    addEventListener('click', swallow, { capture: true, once: true }); setTimeout(() => removeEventListener('click', swallow, true), 700);
    tl.progress(1);
  };
  svg.addEventListener('pointerdown', skip);
  addEventListener('resize', () => { if (tl.isActive()) tl.progress(1); }, { once: true });

  function done() {
    G.set([...titleParts, ...after], { clearProps: 'opacity' });
    html.classList.remove('intro-run');                          // the lamp's flame starts to breathe from where the bindu rests
    svg.remove();                                                // the real lamp takes over, its flame where the bindu came to rest
  }
})();
