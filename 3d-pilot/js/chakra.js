// chakra.js — the Ṛta-chakra as parts that can move, with the choreography the founder's philosophy asks for.
// Shared by the HyperFrames compositions (paused timeline, rendered) and the site (the same timeline, played live).
//
// The meaning (Harsh, 11 Oct 2026):
//   the bindu (gold)   God, the soul: the 25th tattva. It is always there: never drawn in, never taken away, never moved
//                      by the wheel. Creation and dissolution happen around it.
//   prakriti           24 tattvas: two whorls of 12 petals. From above only 12 are seen, the 12 petals of the anahata,
//                      the heart chakra (God sits in the heart, Gita 18.61). The petals are also the wheel's spokes.
//   ṛta                the ring of time with its 12 Ādityas: 12 months, 360° = 12 × 30 days, so one degree is a day.
//   creation           bindu → prakriti blooms → ṛta begins (the wheel turns: a month is 30°)
//   dissolution        the Ādityas go first, then prakriti; the bindu stays; and creation begins again
// Because the mark has 12-fold symmetry, the wheel at rest after any whole number of months is exactly the upright mark.
(function (root) {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const PETAL = 'M 245.5 182.4 C 239 176 230.5 164 227.5 148 C 225.6 130 242 108 256 95 C 270 108 286.4 130 284.5 148 C 281.5 164 273 176 266.5 182.4 Z';
  const BINDU = 'M 256 205.4 C 283.9 205.4 306.6 228.1 306.6 256 C 306.6 283.9 283.9 306.6 256 306.6 C 228.1 306.6 205.4 283.9 205.4 256 C 205.4 228.1 228.1 205.4 256 205.4 Z';
  const COLORS = { ground: '#141414', ash: '#C9C2B6', deep: '#8F887C', stone: '#B8B1A4', gold: '#C8A15A', light: '#EDEBE6' };
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
      suns.push(el('circle', { cx: x, cy: y, r: 10.35, fill: COLORS.light, opacity: 0 }, rta));        // a window lit (aarti)
    }
    // each petal: a turned group (its place), a sliding group (out from the bindu along its axis), the petal (grows at its base)
    const backP = [], frontP = [], backS = [], frontS = [];
    for (let k = 0; k < 12; k++) {
      const gb = el('g', { transform: `rotate(${30 * k + 15} 256 256)` }, back), sb = el('g', {}, gb);
      backS.push(sb); backP.push(el('path', { d: PETAL, fill: COLORS.deep, stroke: COLORS.ground, 'stroke-width': 5, 'stroke-linejoin': 'round' }, sb));
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
    gsap.set([p.wheel, p.back], { rotation: 0, svgOrigin: '256 256' });
  }
  // the moment the ring's tracing passes Āditya k (k = 0 at the top, clockwise), for a sine in-out trace of duration d
  const passAt = (k, d) => { const f = (15 + 30 * k) / 360; return d * Math.acos(1 - 2 * f) / Math.PI; };

  // prakriti emanates from the bindu: a petal starts hidden behind it (pulled in 70 units, at .45 size: wholly inside the
  // gold disc) and comes out along its own axis, growing, fully opaque (no translucent stage); dissolution reverses it
  function petalIn(tl, slide, petal, at, dur = .85) {
    tl.fromTo(slide, { y: IN_Y }, { y: 0, duration: dur, ease: 'power3.out', immediateRender: false }, at);
    tl.fromTo(petal, { scale: IN_S, svgOrigin: '256 182.4' }, { scale: 1, svgOrigin: '256 182.4', duration: dur, ease: 'power3.out', immediateRender: false }, at);
  }
  function petalOut(tl, slide, petal, at, dur = .6) {
    tl.fromTo(slide, { y: 0 }, { y: IN_Y, duration: dur, ease: 'power2.in', immediateRender: false }, at);
    tl.fromTo(petal, { scale: 1, svgOrigin: '256 182.4' }, { scale: IN_S, svgOrigin: '256 182.4', duration: dur, ease: 'power2.in', immediateRender: false }, at);
  }

  // prakriti blooms: 24 tattvas (the back whorl, then the front between them), then the back whorl tucks behind the
  // front, so that from above 12 are seen. Returns the end time.
  function bloom24(tl, p, at, { stagger = .055, gap = .55, tuck = .7 } = {}) {
    p.backP.forEach((q, k) => petalIn(tl, p.backS[k], q, at + k * stagger));
    const t2 = at + gap; p.frontP.forEach((q, k) => petalIn(tl, p.frontS[k], q, t2 + k * stagger));
    const t3 = t2 + 12 * stagger + .45;
    tl.fromTo(p.back, { rotation: 0, svgOrigin: '256 256' }, { rotation: -15, svgOrigin: '256 256', duration: tuck, ease: 'power2.inOut', immediateRender: false }, t3);
    return t3 + tuck;
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
    return at + dur;
  }
  // ṛta withdraws, counter-clockwise: the Ādityas go first, as the ring recedes past them
  function untraceRta(tl, p, at, dur = 1.1) {
    tl.fromTo(p.ring, { strokeDashoffset: 0 }, { strokeDashoffset: p.OFF, duration: dur, ease: 'sine.inOut', immediateRender: false }, at);
    p.adityas.forEach((a, k) => tl.fromTo(a, { opacity: 1 }, { opacity: 0, duration: .001, immediateRender: false }, at + dur - passAt(k, dur)));
    return at + dur;
  }
  // prakriti withdraws into the bindu: the front 12, then the hidden 12 come out from behind and follow
  function withdraw24(tl, p, at, { stagger = .045 } = {}) {
    p.frontP.forEach((q, k) => petalOut(tl, p.frontS[k], q, at + (11 - k) * stagger));
    const t2 = at + 12 * stagger + .1;
    tl.fromTo(p.back, { rotation: -15, svgOrigin: '256 256' }, { rotation: 0, svgOrigin: '256 256', duration: .5, ease: 'power2.inOut', immediateRender: false }, t2 - .3);
    p.backP.forEach((q, k) => petalOut(tl, p.backS[k], q, t2 + (11 - k) * stagger));
    return t2 + 12 * stagger + .55;
  }
  // the wheel turns n months (30° each) with a rest between: the bindu never moves; at rest it is the upright mark
  function turnMonths(tl, p, at, n = 1, { step = .9, rest = .6, from = 0 } = {}) {
    let t = at;
    for (let i = 0; i < n; i++) { tl.fromTo(p.wheel, { rotation: from + 30 * i, svgOrigin: '256 256' }, { rotation: from + 30 * (i + 1), svgOrigin: '256 256', duration: step, ease: 'power2.inOut', immediateRender: false }, t); t += step + rest; }
    return t - rest;
  }
  // aarti: a light goes round ṛta clockwise, each Āditya's window catching it as it passes
  function aarti(tl, p, at, dur = 5.2) {
    const seg = p.L * .14;                                        // the light: a short lit arc travelling the ring
    tl.set(p.light, { attr: { 'stroke-dasharray': `${seg} ${p.L}` } }, at);
    tl.fromTo(p.light, { strokeDashoffset: seg }, { strokeDashoffset: seg - p.L, duration: dur, ease: 'none', immediateRender: false }, at);
    tl.fromTo(p.light, { opacity: 0 }, { opacity: .5, duration: .6, ease: 'sine.out', immediateRender: false }, at);
    tl.to(p.light, { opacity: 0, duration: .6, ease: 'sine.in' }, at + dur - .6);
    p.suns.forEach((s, k) => {
      const tk = at + dur * ((15 + 30 * k) / 360 + .07);          // when the arc's middle reaches Āditya k
      tl.fromTo(s, { opacity: 0 }, { opacity: .85, duration: .25, ease: 'sine.out', immediateRender: false }, tk - .2);
      tl.to(s, { opacity: 0, duration: 1.1, ease: 'sine.in' }, tk + .1);
    });
    return at + dur;
  }

  // the name, by word (Devanagari is never moved letter by letter), its echo, a rule, the place
  function nameIn(tl, ids, at) {
    tl.fromTo(ids.words, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: .5, ease: 'power4.out', stagger: .14, immediateRender: false }, at);
    tl.fromTo(ids.echo, { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: .45, ease: 'power3.out', immediateRender: false }, at + .34);
    if (ids.rule) tl.fromTo(ids.rule, { scaleX: 0 }, { scaleX: 1, duration: .7, ease: 'power2.inOut', immediateRender: false }, at + .8);
    if (ids.place) tl.fromTo(ids.place, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: .45, ease: 'power4.out', immediateRender: false }, at + 1.15);
    if (ids.placeEcho) tl.fromTo(ids.placeEcho, { opacity: 0 }, { opacity: 1, duration: .45, ease: 'power2.out', immediateRender: false }, at + 1.33);
    return at + 1.8;
  }

  root.RtaChakra = { build, hide, petalIn, petalOut, bloom24, bloom12, traceRta, untraceRta, withdraw24, turnMonths, aarti, nameIn, passAt, PETAL, BINDU, COLORS };
})(typeof window !== 'undefined' ? window : globalThis);
