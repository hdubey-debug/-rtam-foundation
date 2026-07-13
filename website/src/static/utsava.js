/* the year-wheel: the year keeps the same shape as the mark — twelve around one.
   The list is real DOM (works with no JS); this builds the wheel around it. */
function rtamUtsava(){
  const holder = document.getElementById("festdata");
  const svg = document.getElementById("wheel");
  if (!svg || !holder) return;
  const FESTS = JSON.parse(holder.textContent).map(f => {
    const [y, m, d] = f.date.split("-").map(Number);
    return {...f, m, d};
  });

  const NS = "http://www.w3.org/2000/svg", CX = 380, CY = 380, R = 310;
  const MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
  const MDAYS = [31,28,31,30,31,30,31,31,30,31,30,31];
  const doy = (m, d) => MDAYS.slice(0, m - 1).reduce((a, b) => a + b, 0) + d;
  const ang = v => (-90 + 360 * v / 365) * Math.PI / 180;   /* Jan 1 at top, clockwise */
  const P = (r, a) => [CX + r * Math.cos(a), CY + r * Math.sin(a)];
  const el = (t, at) => { const e = document.createElementNS(NS, t);
    for (const k in at) e.setAttribute(k, at[k]); svg.appendChild(e); return e; };

  el("circle", {class: "ywrim", cx: CX, cy: CY, r: R});
  for (let m = 1; m <= 12; m++){
    const a0 = ang(doy(m, 1));
    const [x1, y1] = P(R - 9, a0), [x2, y2] = P(R + 9, a0);
    el("line", {class: "ywtick", x1, y1, x2, y2});
    const am = ang(doy(m, 1) + MDAYS[m - 1] / 2), [lx, ly] = P(R + 34, am);
    const t = el("text", {class: "ywlbl", x: lx, y: ly,
      "text-anchor": "middle", "dominant-baseline": "middle"});
    t.textContent = MONTHS[m - 1];
  }
  el("circle", {class: "ywhub", cx: CX, cy: CY, r: 13});
  const DG = "०१२३४५६७८९";
  const dg = n => String(n).split("").map(c => DG[+c]).join("");
  const yr = el("text", {class: "ywyear", x: CX, y: CY + 44, "text-anchor": "middle"});
  yr.textContent = dg(new Date().getFullYear());

  /* today: a small flame on the rim */
  const now = new Date();
  const tdoy = doy(now.getMonth() + 1, now.getDate());
  const ta = ang(tdoy), [tx, ty] = P(R, ta);
  el("circle", {class: "ywtoday", cx: tx, cy: ty, r: 26});
  el("path", {class: "ywflame",
    d: "M0,-9 C3.4,-4.6 4.2,-1.4 0,4.4 C-4.2,-1.4 -3.4,-4.6 0,-9 Z",
    transform: `translate(${tx} ${ty})`});
  const [ax, ay] = P(R + 52, ta);
  const aj = el("text", {class: "ywaj", x: ax, y: ay,
    "text-anchor": "middle", "dominant-baseline": "middle"});
  aj.textContent = "आज";

  /* utsava points */
  const dots = FESTS.map((f, i) => {
    const a = ang(doy(f.m, f.d)), [x, y] = P(R, a);
    const g = el("g", {class: "fest"});
    const halo = document.createElementNS(NS, "circle");
    halo.setAttribute("class", "ywhalo");
    halo.setAttribute("cx", x); halo.setAttribute("cy", y); halo.setAttribute("r", 15);
    const c = document.createElementNS(NS, "circle");
    c.setAttribute("class", "ywdot");
    c.setAttribute("cx", x); c.setAttribute("cy", y); c.setAttribute("r", 7);
    g.appendChild(halo); g.appendChild(c);
    g.addEventListener("click", () => setFocus(i));
    g.addEventListener("mouseenter", () => setFocus(i));
    return {halo, c};
  });

  const rows = [...document.querySelectorAll(".yrow")];
  const card = document.getElementById("ycard");
  let cur = -1;
  function setFocus(i){
    if (i === cur) return; cur = i;
    dots.forEach((d, k) => { d.c.setAttribute("r", k === i ? 10 : 7);
      d.halo.setAttribute("opacity", k === i ? .9 : 0); });
    rows.forEach((r, k) => r.classList.toggle("on", k === i));
    const f = FESTS[i];
    card.querySelector(".dn").textContent = f.dn;
    card.querySelector(".en").textContent = f.en;
    card.querySelector(".when .d").textContent = f.display + " · ";
    card.querySelector(".when .dn").textContent = f.tithi;
    card.querySelector(".line").textContent = f.line || "";
  }
  rows.forEach((r, i) => { r.addEventListener("click", () => setFocus(i));
    r.addEventListener("mouseenter", () => setFocus(i)); });
  window.setFocus = setFocus;

  /* open on the next upcoming utsava (by the wheel's annual cycle) */
  const next = FESTS.findIndex(f => doy(f.m, f.d) >= tdoy);
  setFocus(next < 0 ? 0 : next);
}
