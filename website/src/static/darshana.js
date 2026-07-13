/* the sanctum: the approach (the W1.3 ladder, REVERSED — contraction toward Him)
   and the murti viewing (one stage, three positions).
   The static stacked sequence is the page's default and the reduced-motion
   experience; this file only upgrades it where motion is permitted.
   The rAF loop runs ONLY while the approach is in view. */
function rtamDarshana(){
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- the murti viewing: quiet crossfade between three positions ---- */
  const murti = document.querySelector(".murti");
  if (murti){
    murti.classList.add("live");
    const tabs = [...document.querySelectorAll(".postab")];
    const poss = [...murti.querySelectorAll(".pos")];
    const reads = [...document.querySelectorAll(".pread")];
    const pick = id => {
      tabs.forEach(b => b.setAttribute("aria-selected", String(b.dataset.pos === id)));
      poss.forEach(p => p.classList.toggle("on", p.dataset.pos === id));
      reads.forEach(r => r.classList.toggle("on", r.dataset.pos === id));
    };
    tabs.forEach(b => b.addEventListener("click", () => pick(b.dataset.pos)));
    pick("sammukha");
  }

  /* ---- the approach ---- */
  const ap = document.getElementById("approach");
  if (!ap || still) return;
  ap.classList.add("live");

  const NS = "http://www.w3.org/2000/svg";
  const S = 252 / 230, CX = 300, CY = 300;
  function petalD(deg){
    const a = deg * Math.PI / 180, ux = Math.cos(a), uy = Math.sin(a), nx = -uy, ny = ux;
    const p = (r, w) => `${(CX + ux*r*S + nx*w*S).toFixed(1)} ${(CY + uy*r*S + ny*w*S).toFixed(1)}`;
    const G = [[73.6,10.5],[80,17],[92,25.5],[108,28.5],[126,30.4],[148,14],[161,0]];
    return `M ${p(G[0][0],-G[0][1])} C ${p(G[1][0],-G[1][1])} ${p(G[2][0],-G[2][1])} ${p(G[3][0],-G[3][1])}`
         + ` C ${p(G[4][0],-G[4][1])} ${p(G[5][0],-G[5][1])} ${p(G[6][0],0)}`
         + ` C ${p(G[5][0],G[5][1])} ${p(G[4][0],G[4][1])} ${p(G[3][0],G[3][1])}`
         + ` C ${p(G[2][0],G[2][1])} ${p(G[1][0],G[1][1])} ${p(G[0][0],G[0][1])} Z`;
  }
  const petG = document.getElementById("petG"), winG = document.getElementById("winG");
  const petals = [], wins = [];
  for (let k = 0; k < 12; k++){
    const e = document.createElementNS(NS, "path");
    e.setAttribute("d", petalD(-90 + k*30));
    e.setAttribute("class", "apet");
    e.setAttribute("stroke-width", (5*S).toFixed(1));
    e.style.transformOrigin = "300px 300px";
    petG.appendChild(e); petals.push(e);
    const a = (-90 + k*30) * Math.PI / 180, w = document.createElementNS(NS, "circle");
    w.setAttribute("cx", (300 + 211.6*S*Math.cos(a)).toFixed(1));
    w.setAttribute("cy", (300 + 211.6*S*Math.sin(a)).toFixed(1));
    w.setAttribute("r", (10.35*S).toFixed(1));
    w.setAttribute("class", "awin");
    winG.appendChild(w); wins.push(w);
  }

  const ease = t => t < 0 ? 0 : t > 1 ? 1 : t*t*(3 - 2*t);
  const seg = (p, a, b) => ease((p - a) / (b - a));
  const $ = id => document.getElementById(id);

  function setStage(p, t){
    /* the dipa breathes — hub + glow, 5.5 s */
    const br = Math.sin(2 * Math.PI * t / 5.5);
    $("glowC").setAttribute("r", (120 + 14*br).toFixed(1));
    $("glowC").setAttribute("opacity", (0.75 + 0.25*br).toFixed(2));
    $("hub").setAttribute("transform", `scale(${(1 + 0.018*br).toFixed(3)})`);
    $("hub").style.transformOrigin = "300px 300px";
    /* the rim and the twelve suns depart first */
    const r = 1 - seg(p, 0.06, 0.30);
    $("rimG").setAttribute("opacity", r.toFixed(2));
    $("rimG").setAttribute("transform", `scale(${(0.88 + 0.12*r).toFixed(3)})`);
    $("rimG").style.transformOrigin = "300px 300px";
    wins.forEach((w, k) =>
      w.setAttribute("opacity", (1 - seg(p, 0.04 + k*0.012, 0.16 + k*0.012)).toFixed(2)));
    /* the corolla folds, staggered */
    petals.forEach((e, k) => {
      const q = 1 - seg(p, 0.42 + k*0.014, 0.62 + k*0.014);
      e.style.opacity = q; e.style.transform = `scale(${0.42 + 0.58*q})`;
    });
    /* the bindu's ring arrives as the petals fold */
    $("binduRing").setAttribute("opacity", seg(p, 0.55, 0.70).toFixed(2));
    /* the three captions: cosmic → heart → केवलम् (which stays) */
    $("capC").style.opacity = Math.min(1, 1 - seg(p, 0.20, 0.28));
    $("capB").style.opacity = Math.min(seg(p, 0.30, 0.38), 1 - seg(p, 0.52, 0.60));
    $("capA").style.opacity = seg(p, 0.66, 0.78);
    $("aphint").style.opacity = 1 - seg(p, 0.03, 0.08);
  }

  /* IO-gated: the loop exists only while the stage is on screen */
  let running = false, t0 = null;
  function loop(){
    if (!running) return;
    const vh = innerHeight;
    const rect = ap.getBoundingClientRect();
    const p = Math.max(0, Math.min(1, -rect.top / (ap.offsetHeight - vh)));
    setStage(p, (performance.now() - (t0 ??= performance.now())) / 1000);
    requestAnimationFrame(loop);
  }
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting && !running){ running = true; loop(); }
    else if (!e.isIntersecting) running = false;
  }));
  io.observe(ap);

  /* capture hook */
  window.setApproach = p => { running = false; setStage(p, 0); };
}
