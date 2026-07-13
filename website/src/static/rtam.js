/* ṚTAM site runtime — the depth gauge, the four verbs' triggers, the menu.
   Ambient life only: nothing here runs while the page is still. */
function rtamDepth(depth){
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* the depth gauge: one mark, morphing once per threshold crossing.
     Chakra on the land (0), anahata in the halls and on the walk (1–2),
     bindu in the sanctum (3). sessionStorage lets the morph play FROM
     wherever you last stood; @view-transition upgrades it where supported. */
  const stage = d => d >= 3 ? 3 : d >= 1 ? 1 : 0;
  const gm = document.getElementById("gm");
  const imgs = [...gm.querySelectorAll("img")];
  const show = s => imgs.forEach(m => { m.style.opacity = (+m.dataset.d === s) ? 1 : 0; });
  let prev = +(sessionStorage.getItem("rtam-depth") ?? depth);
  if (![0,1,2,3].includes(prev)) prev = depth;
  show(stage(prev));
  if (stage(prev) !== stage(depth) && !still){
    requestAnimationFrame(() => requestAnimationFrame(() => {
      gm.classList.add("moving"); show(stage(depth));
    }));
  } else show(stage(depth));
  sessionStorage.setItem("rtam-depth", depth);

  /* verb 4: veils part once, when you arrive at them (never the LCP hero) */
  const vio = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting){ e.target.classList.add("parted"); vio.unobserve(e.target); }
  }), {threshold:.35});
  document.querySelectorAll(".veil").forEach(v => vio.observe(v));

  /* thresholds: the flame is passed along the hairline once, on first arrival */
  const tio = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting){ e.target.classList.add("lit"); tio.unobserve(e.target); }
  }), {threshold:.9});
  document.querySelectorAll(".thresh").forEach(h => tio.observe(h));

  /* the menu: full-screen, layer-colored */
  const menu = document.getElementById("menu");
  const setOpen = open => {
    menu.classList.toggle("open", open);
    document.body.classList.toggle("menu-open", open);
    document.querySelectorAll(".menubtn").forEach(b => b.setAttribute("aria-expanded", open));
    if (open) menu.querySelector("a, button").focus();
  };
  document.querySelectorAll(".gate .menubtn").forEach(b =>
    b.addEventListener("click", () => setOpen(true)));
  menu.querySelector(".menubtn").addEventListener("click", () => setOpen(false));
  addEventListener("keydown", e => {
    if (e.key === "Escape" && menu.classList.contains("open")) setOpen(false);
  });

  /* foil: gold catches light as the page moves — event-driven, no free loop.
     A still page is still gold; reduced-motion never registers the listener. */
  if (document.querySelector(".foil, .foil-rule") && !still){
    let raf = 0;
    const setp = () => {
      raf = 0;
      const range = document.documentElement.scrollHeight - innerHeight;
      const t = range > 0 ? Math.max(0, Math.min(1, scrollY / range)) : 0;
      document.documentElement.style.setProperty("--foilp", t.toFixed(4));
    };
    addEventListener("scroll", () => { if (!raf) raf = requestAnimationFrame(setp); },
                     {passive:true});
    setp();
  }

  /* capture hooks (previews only) */
  window.setDepthMorph = from => { gm.classList.add("moving"); show(stage(from));
    setTimeout(() => show(stage(depth)), 60); };
  window.setFoil = t => document.documentElement.style.setProperty("--foilp", t.toFixed(4));
}
