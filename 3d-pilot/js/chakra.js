// chakra.js — the Ṛta-chakra as parts that can move, with the choreography the founder's philosophy asks for.
// Shared by the HyperFrames compositions (paused timeline, rendered) and the site (the same timeline, played live).
//
// The meaning (Harsh, 11 Oct 2026):
//   the bindu (gold)   God, the soul: the 25th tattva. It is always there: never drawn in, never taken away, never moved
//                      by the wheel. Creation and dissolution happen around it.
//   prakriti           24 tattvas: two whorls of 12 petals. From above only 12 are seen, the 12 petals of the anahata,
//                      the heart chakra (God sits in the heart, Gita 18.61). The hidden whorl stands for the subtle
//                      tattvas: they come before the seen in creation and follow them out in dissolution.
//   ṛta                the ring of time with its 12 Ādityas: 12 months, 360° = 12 × 30 days, so one degree is a day.
//   the wheel          RV 1.164.11: the twelve-spoked wheel of ṛta turns round the sky and never ages. Harsh reads the
//                      petals as its spokes, so the wheel that turns is prakriti and ṛta together, round the still bindu
//                      (turnMonths' default). The advisor reads the twelve Ādityas as the spokes, so only the ring turns
//                      ({ part: 'rta' }). Either way it comes to rest upright, and the bindu never turns.
//   creation           bindu → prakriti blooms → ṛta begins
//   dissolution        the Ādityas go first, then prakriti; the bindu stays; and creation begins again
// Because the mark has 12-fold symmetry, the wheel at rest after any whole number of months is exactly the upright mark.
(function (root) {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const PETAL = 'M 245.5 182.4 C 239 176 230.5 164 227.5 148 C 225.6 130 242 108 256 95 C 270 108 286.4 130 284.5 148 C 281.5 164 273 176 266.5 182.4 Z';
  const BINDU = 'M 256 205.4 C 283.9 205.4 306.6 228.1 306.6 256 C 306.6 283.9 283.9 306.6 256 306.6 C 228.1 306.6 205.4 283.9 205.4 256 C 205.4 228.1 228.1 205.4 256 205.4 Z';
  const COLORS = { ground: '#141414', ash: '#C9C2B6', deep: '#8F887C', subtle: '#3A3835', stone: '#B8B1A4', gold: '#C8A15A', light: '#EDEBE6', lamp: '#F3D9A0' };
  const R_RING = 213.5, R_ADITYA = 211.6, START = -105;          // the ring is traced from between two Ādityas
  const IN_Y = 70, IN_S = .45;                                    // a petal hidden behind the bindu: base and tip inside r 50.6
  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };

  // build the mark inside an <svg> (viewBox 0 0 512 512). Everything but the bindu starts hidden.
  function build(svg) {
    svg.setAttribute('viewBox', '0 0 512 512'); svg.setAttribute('overflow', 'visible');
    const wheel = el('g', { class: 'wheel' }, svg);
    const back = el('g', { class: 'prakriti-back' }, wheel), front = el('g', { class: 'prakriti' }, wheel);
    const rta = el('g', { class: 'rta' }, wheel);
    const ring = el('circle', { cx: 256, cy: 256, r: R_RING, fill: 'none', stroke: COLORS.ash, 'stroke-width': 33, transform: `rotate(${START} 256 256)` }, rta);
    const light = el('circle', { cx: 256, cy: 256, r: R_RING, fill: 'none', stroke: COLORS.light, 'stroke-width': 33, opacity: 0, transform: `rotate(${START} 256 256)` }, rta);
    const adityas = [], suns = [];
    for (let k = 0; k < 12; k++) {
      const a = (-90 + 30 * k) * Math.PI / 180, x = 256 + R_ADITYA * Math.cos(a), y = 256 + R_ADITYA * Math.sin(a);
      adityas.push(el('circle', { cx: x, cy: y, r: 10.35, fill: COLORS.ground }, rta));
      suns.push(el('circle', { cx: x, cy: y, r: 10.35, fill: COLORS.lamp, opacity: 0 }, rta));         // a window lit (aarti), lamp-coloured
    }
    // each petal: a turned group (its place), a sliding group (out from the bindu along its axis), the petal (grows at its base)
    const backP = [], frontP = [], backS = [], frontS = [];
    for (let k = 0; k < 12; k++) {
      const gb = el('g', { transform: `rotate(${30 * k + 15} 256 256)` }, back), sb = el('g', {}, gb);
      backS.push(sb); backP.push(el('path', { d: PETAL, fill: COLORS.subtle, stroke: COLORS.ground, 'stroke-width': 5, 'stroke-linejoin': 'round' }, sb));
      const gf = el('g', { transform: `rotate(${30 * k} 256 256)` }, front), sf = el('g', {}, gf);
      frontS.push(sf); frontP.push(el('path', { d: PETAL, fill: COLORS.ash, stroke: COLORS.ground, 'stroke-width': 5, 'stroke-linejoin': 'round' }, sf));
    }
    const bindu = el('path', { class: 'bindu', d: BINDU, fill: COLORS.gold }, svg);
    // the trace: one dash as long as the ring (+1 %: a circle's drawn length is not 2πr) and a longer gap; hidden, the dash
    // sits well inside its gap (off = L + 30), so no hairline shows at the start before the ring is drawn
    const L = ring.getTotalLength() * 1.01, OFF = L + 30;
    for (const c of [ring, light]) { c.setAttribute('stroke-dasharray', `${L} ${L + 60}`); c.setAttribute('stroke-dashoffset', OFF); }
    const parts = { svg, wheel, back, front, rta, ring, light, L, OFF, adityas, suns, backP, frontP, backS, frontS, bindu };
    hide(parts); return parts;
  }
  function hide(p) {
    gsap.set([...p.backS, ...p.frontS], { y: IN_Y });                                               // behind the bindu
    gsap.set([...p.backP, ...p.frontP], { opacity: 1, scale: IN_S, svgOrigin: '256 182.4' });
    gsap.set(p.adityas, { opacity: 0 }); gsap.set(p.suns, { opacity: 0 });
    gsap.set([p.ring, p.light], { strokeDashoffset: p.OFF }); gsap.set(p.light, { opacity: 0 });
    gsap.set([p.wheel, p.back, p.rta], { rotation: 0, svgOrigin: '256 256' });
    gsap.set(p.ring, { attr: { 'stroke-dasharray': `${p.L} ${p.L + 60}` } });
    p.adityas.forEach((a) => gsap.set(a, { scale: 1, svgOrigin: `${a.getAttribute('cx')} ${a.getAttribute('cy')}` }));
  }
  // the finished mark, at once (for films that begin with it, and for the site's marks)
  function show(p) {
    gsap.set([...p.backS, ...p.frontS], { y: 0 }); gsap.set([...p.backP, ...p.frontP], { opacity: 1, scale: 1, svgOrigin: '256 182.4' });
    gsap.set(p.backP, { scale: .92, svgOrigin: '256 182.4' }); gsap.set(p.back, { rotation: -15, svgOrigin: '256 256' });
    gsap.set(p.ring, { strokeDashoffset: 0, attr: { 'stroke-dasharray': 'none' } }); gsap.set(p.adityas, { opacity: 1 });
  }
  // the moment the ring's tracing passes Āditya k (k = 0 at the top, clockwise), for a sine in-out trace of duration d
  const passAt = (k, d) => { const f = (15 + 30 * k) / 360; return d * Math.acos(1 - 2 * f) / Math.PI; };

  // prakriti emanates from the bindu: a petal starts hidden behind it (pulled in 70 units, at .45 size: wholly inside the
  // gold disc) and comes out along its own axis, growing, fully opaque (no translucent stage); dissolution reverses it
  function petalIn(tl, slide, petal, at, dur = .85) {
    tl.set(petal, { opacity: 1 }, at);
    tl.fromTo(slide, { y: IN_Y }, { y: 0, duration: dur, ease: 'power4.out', immediateRender: false }, at);
    tl.fromTo(petal, { scale: IN_S, svgOrigin: '256 182.4' }, { scale: 1, svgOrigin: '256 182.4', duration: dur, ease: 'power4.out', immediateRender: false }, at);
  }
  function petalOut(tl, slide, petal, at, dur = .6, from = 1) {
    tl.fromTo(slide, { y: 0 }, { y: IN_Y, duration: dur, ease: 'power2.in', immediateRender: false }, at);
    tl.fromTo(petal, { scale: from, svgOrigin: '256 182.4' }, { scale: IN_S, svgOrigin: '256 182.4', duration: dur, ease: 'power2.in', immediateRender: false }, at);
    tl.set(petal, { opacity: 0 }, at + dur);
  }

  // prakriti blooms: all 24 tattvas grow out of the bindu together, the subtle whorl leading by 120 ms (and a little shorter:
  // never longer than the seen); then it turns 15° behind the seen, so that from above 12 are seen. Returns the end time.
  function bloom24(tl, p, at, { lead = .12, dur = .9, tuck = .4 } = {}) {
    p.backP.forEach((q, k) => { petalIn(tl, p.backS[k], q, at, dur); tl.to(q, { scale: .92, svgOrigin: '256 182.4', duration: .3, ease: 'sine.out' }, at + dur - .3); });
    p.frontP.forEach((q, k) => petalIn(tl, p.frontS[k], q, at + lead, dur));
    const t3 = at + lead + dur;
    tl.fromTo(p.back, { rotation: 0, svgOrigin: '256 256' }, { rotation: -15, svgOrigin: '256 256', duration: tuck, ease: 'sine.inOut', immediateRender: false }, t3);
    return t3 + tuck;
  }
  // Harsh's opening (13 Oct 2026): the 12 seen petals come one by one, clockwise from the top (the order of pradakshina),
  // each out of the bindu; then the ring; then the 12 Ādityas one by one. Returns the end time.
  function petalsInOrder(tl, p, at, { stagger = .30, dur = .8 } = {}) {
    p.frontP.forEach((q, k) => petalIn(tl, p.frontS[k], q, at + k * stagger, dur));
    return at + 11 * stagger + dur;
  }
  // the ring alone, traced clockwise from the top (its windows come after, one by one)
  function traceRing(tl, p, at, dur = 1.4) {
    tl.set(p.ring, { attr: { 'stroke-dasharray': `${p.L} ${p.L + 60}`, transform: 'rotate(-90 256 256)' } }, at);
    tl.fromTo(p.ring, { strokeDashoffset: p.OFF }, { strokeDashoffset: 0, duration: dur, ease: 'sine.inOut', immediateRender: false }, at);
    tl.set(p.ring, { attr: { 'stroke-dasharray': 'none' } }, at + dur);        // whole: no seam where the trace began
    return at + dur;
  }
  // the 12 Ādityas, one by one clockwise from the top: each window darkens into the ring (a fade, 200 ms: they are holes,
  // and a hole that scales up pops)
  function adityasIn(tl, p, at, { stagger = .2, dur = .2 } = {}) {
    p.adityas.forEach((a, k) => tl.fromTo(a, { opacity: 0 }, { opacity: 1, duration: dur, ease: 'sine.out', immediateRender: false }, at + k * stagger));
    return at + 11 * stagger + dur;
  }
  // prakriti blooms as one: the 12 seen petals open together (a single breath)
  function bloom12(tl, p, at, dur = 1.0) {
    p.frontP.forEach((q, k) => {
      tl.fromTo(p.frontS[k], { y: IN_Y }, { y: 0, duration: dur, ease: 'expo.out', immediateRender: false }, at);
      tl.fromTo(q, { scale: IN_S, svgOrigin: '256 182.4' }, { scale: 1, svgOrigin: '256 182.4', duration: dur, ease: 'expo.out', immediateRender: false }, at);
    });
    return at + dur;
  }
  // ṛta is traced clockwise, the Ādityas appearing as it passes them (the year's 12 months)
  function traceRta(tl, p, at, dur = 1.4) {
    tl.fromTo(p.ring, { strokeDashoffset: p.OFF }, { strokeDashoffset: 0, duration: dur, ease: 'sine.inOut', immediateRender: false }, at);
    p.adityas.forEach((a, k) => tl.fromTo(a, { opacity: 0 }, { opacity: 1, duration: .001, immediateRender: false }, at + passAt(k, dur)));
    tl.set(p.ring, { attr: { 'stroke-dasharray': 'none' } }, at + dur);        // whole: no seam where the trace began
    return at + dur;
  }
  // ṛta withdraws, counter-clockwise: the Ādityas go first, as the ring recedes past them
  function untraceRta(tl, p, at, dur = 1.1) {
    tl.set(p.ring, { attr: { 'stroke-dasharray': `${p.L} ${p.L + 60}` }, strokeDashoffset: 0 }, at);
    tl.fromTo(p.ring, { strokeDashoffset: 0 }, { strokeDashoffset: p.OFF, duration: dur, ease: 'sine.inOut', immediateRender: false }, at);
    p.adityas.forEach((a, k) => tl.fromTo(a, { opacity: 1 }, { opacity: 0, duration: .001, immediateRender: false }, at + dur - passAt(k, dur)));
    return at + dur;
  }
  // prakriti withdraws into the bindu: the front 12, then the hidden 12 come out from behind and follow
  function withdraw24(tl, p, at, { stagger = .045 } = {}) {
    p.frontP.forEach((q, k) => petalOut(tl, p.frontS[k], q, at + (11 - k) * stagger));
    const t2 = at + 12 * stagger + .1;
    tl.fromTo(p.back, { rotation: -15, svgOrigin: '256 256' }, { rotation: 0, svgOrigin: '256 256', duration: .5, ease: 'power2.inOut', immediateRender: false }, t2 - .3);
    p.backP.forEach((q, k) => petalOut(tl, p.backS[k], q, t2 + (11 - k) * stagger, .6, .92));
    return t2 + 12 * stagger + .55;
  }
  // the wheel turns n months (30° each) with a rest between: prakriti and ṛta together round the still bindu, or with
  // part: 'rta' the ring alone. At every rest it is the upright mark.
  function turnMonths(tl, p, at, n = 1, { step = .9, rest = .6, from = 0, part = 'wheel' } = {}) {
    let t = at; const g = part === 'rta' ? p.rta : p.wheel;
    for (let i = 0; i < n; i++) { tl.fromTo(g, { rotation: from + 30 * i, svgOrigin: '256 256' }, { rotation: from + 30 * (i + 1), svgOrigin: '256 256', duration: step, ease: 'power2.inOut', immediateRender: false }, t); t += step + rest; }
    return t - rest;
  }
  // aarti: a lamp passes clockwise behind ṛta and each Āditya's window catches its light, which dies over 600 ms. The ring
  // itself never shines. One pass is dur seconds.
  function aarti(tl, p, at, dur = 1.8) {
    p.suns.forEach((s, k) => {
      const tk = at + dur * (k + .5) / 12;
      tl.fromTo(s, { opacity: 0 }, { opacity: .9, duration: .12, ease: 'sine.out', immediateRender: false }, tk);
      tl.to(s, { opacity: 0, duration: .6, ease: 'sine.in' }, tk + .14);
    });
    return at + dur + .75;
  }

  // the name: whole words that light as a lamp catches (out-expo, 450 ms) after a beat of black; never wiped through a
  // glyph, never letter by letter. Then the echo, the rule and the place.
  function nameIn(tl, ids, at) {
    const on = (e, t) => tl.fromTo(e, { opacity: 0 }, { opacity: 1, duration: .45, ease: 'expo.out', immediateRender: false }, t);
    const words = typeof ids.words === 'string' ? Array.from(document.querySelectorAll(ids.words)) : ids.words;
    words.forEach((w, i) => on(w, at + .16 + i * .4));
    const t = at + .16 + words.length * .4;
    on(ids.echo, t);
    if (ids.rule) tl.fromTo(ids.rule, { scaleX: 0 }, { scaleX: 1, duration: .6, ease: 'power2.inOut', immediateRender: false }, t);
    if (ids.place) on(ids.place, t + .5);
    if (ids.placeEcho) on(ids.placeEcho, t + .5);
    return t + .95;
  }

  root.RtaChakra = { build, hide, show, petalsInOrder, traceRing, adityasIn, petalIn, petalOut, bloom24, bloom12, traceRta, untraceRta, withdraw24, turnMonths, aarti, nameIn, passAt, PETAL, BINDU, COLORS };
})(typeof window !== 'undefined' ? window : globalThis);
