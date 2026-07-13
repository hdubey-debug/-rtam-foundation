/* the depth gauge: one mark, morphing to show how deep you stand.
   Chakra on the street (0), anahata in the halls (1), bindu in the sanctum (3).
   Uses sessionStorage so the morph plays FROM wherever you last stood;
   @view-transition in system.css upgrades this to a seamless morph where supported. */
function rtamDepth(depth){
  const gm = document.getElementById("gm");
  const imgs = [...gm.querySelectorAll("img")];
  const show = d => imgs.forEach(m => { m.style.opacity = (+m.dataset.d === d) ? 1 : 0; });
  let prev = +(sessionStorage.getItem("rtam-depth") ?? depth);
  if (![0,1,3].includes(prev)) prev = depth;
  show(prev);
  if (prev !== depth && !matchMedia("(prefers-reduced-motion: reduce)").matches){
    requestAnimationFrame(() => requestAnimationFrame(() => {
      gm.classList.add("moving"); show(depth);
    }));
  } else show(depth);
  sessionStorage.setItem("rtam-depth", depth);

  /* verb 4: veils part once, when you arrive at them */
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting){ e.target.classList.add("parted"); io.unobserve(e.target); }
  }), {threshold:.35});
  document.querySelectorAll(".veil").forEach(v => io.observe(v));

  /* capture hook */
  window.setDepthMorph = from => { gm.classList.add("moving"); show(from);
    setTimeout(() => show(depth), 60); };
}
