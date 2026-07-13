/* the pradakshina walk: the passage moves only clockwise — east, south, west,
   north — and ends at the threshold. The compass keeps your position. */
function rtamWalk(){
  const walk = document.getElementById("walk"), pos = document.getElementById("pos");
  const span = () => walk.scrollWidth - walk.clientWidth;

  function paint(){
    const t = span() > 0 ? walk.scrollLeft / span() : 0;
    const a = t * 300 * Math.PI / 180;           /* E → S → W → N → threshold */
    pos.setAttribute("cx", (50 + 33 * Math.cos(a)).toFixed(1));
    pos.setAttribute("cy", (50 + 33 * Math.sin(a)).toFixed(1));
  }
  walk.addEventListener("scroll", paint, {passive:true});

  /* the vertical wheel advances the walk — forward only ever means clockwise */
  walk.addEventListener("wheel", e => {
    if (Math.abs(e.deltaY) > Math.abs(e.deltaX)){
      walk.scrollLeft += e.deltaY * 2.2; e.preventDefault();
    }
  }, {passive:false});
  document.getElementById("fwd").addEventListener("click",
    () => walk.scrollBy({left: walk.clientWidth}));
  document.getElementById("back").addEventListener("click",
    () => walk.scrollBy({left: -walk.clientWidth}));

  window.setWalk = t => { walk.style.scrollBehavior = "auto"; walk.scrollLeft = t * span(); paint(); };
  paint();
}
