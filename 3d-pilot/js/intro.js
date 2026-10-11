// The opening, on the pilot pages (<html data-pilot="1" class="intro">). Before the page, the Ṛta-chakra comes into being
// where the temple will stand: the bindu alone (there from the first frame, never taken away); prakriti blooms, all 24
// tattvas together (the subtle whorl first, then it turns behind the seen, so 12 are seen); ṛta is traced with its 12
// Ādityas while the name lights in its own place. Then one of three endings (?open=…; seat when none is asked for):
//   seat   the finished mark takes its seat: it recedes into the temple's door (on Nandi's page, into Nandi's heart), where
//          the thread of lamplight burns, and the stone rises by light around it. The lamp below is only a lamp.
//   home   the finished mark settles once into its own place on the page (the name's mark, or the footer's on a phone).
//   lamp   the first version: a month turns, all of it returns into the bindu (the Ādityas first, then prakriti), and the
//          bindu descends to the lamp and becomes its flame.
// A touch skips to the end (and doesn't light the lamps). Skipped under reduced motion and with ?skip.
// The choreography is the same code as the HyperFrames films (motion-skills/hf-chakra, js/chakra.js).
(function () {
  const html = document.documentElement, C = window.RtaChakra, G = window.gsap;
  const OPEN = (/[?&]open=(seat|home|lamp)\b/.exec(location.search) || [0, 'seat'])[1];
  html.dataset.open = OPEN;                                     // the lamp's flame is the bindu's gold only when it is the bindu
  const finish = () => { html.classList.remove('intro'); };
  if (!C || !G || (OPEN === 'lamp' && !window.MorphSVGPlugin) || matchMedia('(prefers-reduced-motion: reduce)').matches || /[?&]skip\b/.test(location.search)) { finish(); return; }
  if (OPEN === 'lamp') G.registerPlugin(window.MorphSVGPlugin);
  const $ = (s) => document.querySelector(s), NS = 'http://www.w3.org/2000/svg';
  const play = $('#play'); play.hidden = false;

  // where things are: the picture (the chakra is drawn at its centre and fills most of it)
  const fr = $('#frame').getBoundingClientRect(), W = innerWidth, H = innerHeight;
  const size = Math.min(fr.width, fr.height) * .92, k = size / 512, cx = fr.left + fr.width / 2, cy = fr.top + fr.height / 2;
  const ox = cx - 256 * k, oy = cy - 256 * k, about = `${cx.toFixed(2)} ${cy.toFixed(2)}`;

  // the overlay: the whole screen in CSS px, the chakra in its own 512-unit square. It moves by two groups (never x, y,
  // scale and an svgOrigin on one element): the outer one travels, the inner one scales about the chakra's centre.
  const svg = document.createElementNS(NS, 'svg'); svg.id = 'intro';
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('aria-hidden', 'true');
  const move = document.createElementNS(NS, 'g'), grow = document.createElementNS(NS, 'g'), g = document.createElementNS(NS, 'g');
  g.setAttribute('transform', `translate(${ox} ${oy}) scale(${k})`); svg.appendChild(move); move.appendChild(grow); grow.appendChild(g);
  const holder = document.createElementNS(NS, 'svg'); holder.setAttribute('width', 512); holder.setAttribute('height', 512); holder.setAttribute('overflow', 'visible'); g.appendChild(holder);
  document.body.appendChild(svg);
  const p = C.build(holder);

  // what the opening reveals, in place. The page's own marks come with the page, never beside the one being made.
  const titleParts = ['#title .kicker', '#title .lockup'].map($).filter(Boolean);
  const marks = ['#title .lotus', '#foot .lotus'].map($).filter(Boolean);
  const after = ['#still', '#foot', '#play .lamp', '#play > span:nth-child(2)', '#play .en'].map($).filter(Boolean);
  const thread = $('#thread'), rest = [...after.filter((e) => e.id !== 'still'), ...marks];
  // hidden at once, with their own CSS fades held off: otherwise a child fading out (1 → 0) inside a parent fading in (the
  // name's block, 0 → 1, as .intro comes off) shows faintly for half a second
  G.set([...titleParts, ...after, ...marks], { opacity: 0, transition: 'none' });
  html.classList.add('intro-run'); html.classList.remove('intro');   // the overlay owns the hiding from here; the lamp waits

  const tl = G.timeline({ onComplete: done });
  const light = (e, at) => tl.fromTo(e, { opacity: 0 }, { opacity: 1, duration: .45, ease: 'expo.out', immediateRender: false }, at);
  C.bloom24(tl, p, .35);                                             // prakriti: all 24, the subtle whorl first; then 12 seen
  let t = C.traceRta(tl, p, 1.5, 1.1);                               // ṛta, clockwise from the top
  titleParts.forEach((e, i) => light(e, 1.85 + .3 * i));             // the name, whole, as ṛta begins

  if (OPEN === 'seat') {
    // dusk; then the finished mark recedes into the door, about the door, at an even pace in scale (log), in 1 s. The door
    // is where the thread is (app.js places it from the film's data); it is read when the move begins.
    const R = .012, e2 = G.parseEase('power2.inOut'), E = (q) => (1 - Math.pow(R, e2(q))) / (1 - R);
    const door = (i) => { if (!thread) return 0; const r = thread.getBoundingClientRect(); return (i ? r.top + r.height / 2 - cy : r.left + r.width / 2 - cx) * (1 - R); };
    tl.fromTo('#still', { opacity: 0 }, { opacity: .3, duration: .9, ease: 'sine.inOut', immediateRender: false }, 2.8);
    tl.fromTo(move, { x: 0, y: 0 }, { x: () => door(0), y: () => door(1), duration: 1, ease: E, immediateRender: false }, 3.1);
    tl.fromTo(grow, { scale: 1, svgOrigin: about }, { scale: R, svgOrigin: about, duration: 1, ease: E, immediateRender: false }, 3.1);
    tl.set(move, { opacity: 0 }, 4.1);
    if (thread) {                                                    // the lamplight it went into; then its own breath, from .15
      tl.fromTo(thread, { opacity: 0 }, { opacity: .95, duration: .3, ease: 'sine.out', immediateRender: false }, 3.9);
      tl.to(thread, { opacity: .15, duration: 1, ease: 'sine.inOut' }, 4.2);
    }
    tl.fromTo('#still', { opacity: .3 }, { opacity: 1, duration: 1.4, ease: 'sine.inOut', immediateRender: false }, 3.95);   // the floods
    tl.to(rest, { opacity: 1, duration: .6, ease: 'sine.out', stagger: .08 }, 4.5);
  } else if (OPEN === 'home') {
    // the finished mark settles into the page's own mark (the same drawing, so it lands exactly): one move, .8 s
    const home = marks.find((e) => e.getBoundingClientRect().width > 0);
    const r = home && home.getBoundingClientRect();
    tl.fromTo('#still', { opacity: 0 }, { opacity: 1, duration: 1.4, ease: 'sine.inOut', immediateRender: false }, 3.2);
    if (r) {
      tl.fromTo(move, { x: 0, y: 0 }, { x: r.left + r.width / 2 - cx, y: r.top + r.height / 2 - cy, duration: .8, ease: 'power3.inOut', immediateRender: false }, 2.95);
      tl.fromTo(grow, { scale: 1, svgOrigin: about }, { scale: r.width / size, svgOrigin: about, duration: .8, ease: 'power3.inOut', immediateRender: false }, 2.95);
      tl.set(home, { opacity: 1 }, 3.75); tl.set(move, { opacity: 0 }, 3.75);
    } else tl.to(move, { opacity: 0, duration: .5 }, 2.95);
    if (thread) tl.fromTo(thread, { opacity: 0 }, { opacity: .15, duration: .8, ease: 'sine.inOut', immediateRender: false }, 3.8);
    tl.to(rest.filter((e) => e !== home), { opacity: 1, duration: .6, ease: 'sine.out', stagger: .08 }, 3.8);
  } else {
    // the first version: the bindu descends to the lamp and becomes its flame (the lamp's 24-unit icon, in the mark's units)
    const lamp = $('#play .lamp').getBoundingClientRect();
    const icon = 24 * Math.min(lamp.width, lamp.height) / 60;       // the flame's 24-unit icon, as the lamp draws it
    const ix = lamp.left + lamp.width / 2 - icon / 2, iy = lamp.top + lamp.height / 2 - icon / 2, u = icon / 24;
    const L = (x, y) => `${(((ix + x * u) - ox) / k).toFixed(2)} ${(((iy + y * u) - oy) / k).toFixed(2)}`;
    const FLAME = `M ${L(12, 2.5)} C ${L(15, 6.4)} ${L(16.6, 9.2)} ${L(16.6, 11.8)} C ${L(16.6, 14.34)} ${L(14.54, 16.4)} ${L(12, 16.4)} ` +
                  `C ${L(9.46, 16.4)} ${L(7.4, 14.34)} ${L(7.4, 11.8)} C ${L(7.4, 9.2)} ${L(9, 6.4)} ${L(12, 2.5)} Z`;
    t = C.turnMonths(tl, p, t + .05, 1, { step: .7 });
    t = C.untraceRta(tl, p, t + .35, .7);                              // the Ādityas go first
    t = C.withdraw24(tl, p, t, { stagger: .025 });                     // then prakriti; the bindu stays
    tl.to(p.bindu, { morphSVG: FLAME, duration: .95, ease: 'power3.inOut' }, t);   // and becomes the lamp's flame
    tl.to('#still', { opacity: 1, duration: 1.2, ease: 'sine.inOut' }, t + .1);
    if (thread) tl.fromTo(thread, { opacity: 0 }, { opacity: .15, duration: .8, ease: 'sine.inOut', immediateRender: false }, t + .6);
    tl.to(rest, { opacity: 1, duration: .6, ease: 'sine.out', stagger: .08 }, t + .75);
  }

  // a touch before the end: straight to the landing
  const skip = (e) => {
    e.preventDefault(); e.stopPropagation();
    const swallow = (c) => { c.stopPropagation(); c.preventDefault(); };   // the click that ends this touch must not light the lamps
    addEventListener('click', swallow, { capture: true, once: true }); setTimeout(() => removeEventListener('click', swallow, true), 700);
    tl.progress(1);
  };
  svg.addEventListener('pointerdown', skip);
  addEventListener('resize', () => { if (tl.isActive()) tl.progress(1); }, { once: true });

  function done() {
    G.set([...titleParts, ...after, ...marks, thread].filter(Boolean), { clearProps: 'opacity,transition' });
    html.classList.remove('intro-run');                            // the lamp begins to breathe; the thread, its own breath
    svg.remove();
  }
})();
