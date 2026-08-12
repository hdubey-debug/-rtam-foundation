/** ?perf=1 — the founder's real-browser perf oracle. Continuous rendering
 * with a small overlay: fps, p95 frame time, draw calls, triangles, and the
 * renderer string. Headless SwiftShader numbers are meaningless for perf;
 * this overlay is only trusted in a real browser.
 */
import type { Engine } from "../engine/createEngine";

export function attachPerfOverlay(engine: Engine): () => void {
  const el = document.createElement("div");
  el.style.cssText = [
    "position:fixed",
    "left:12px",
    "bottom:12px",
    "z-index:50",
    "background:rgba(20,20,20,0.82)",
    "color:#C9C2B6",
    "border:1px solid rgba(200,161,90,0.35)",
    "border-radius:6px",
    "padding:8px 10px",
    "font:11px/1.5 monospace",
    "pointer-events:none",
    "white-space:pre",
  ].join(";");
  document.body.appendChild(el);

  const times: number[] = [];
  let last = performance.now();
  let raf = 0;
  let acc = 0;

  const tick = () => {
    const now = performance.now();
    const dt = now - last;
    last = now;
    times.push(dt);
    if (times.length > 240) times.shift();
    engine.requestRender();

    acc += dt;
    if (acc > 500) {
      acc = 0;
      const sorted = [...times].sort((a, b) => a - b);
      const p95 = sorted[Math.floor(sorted.length * 0.95)] ?? 0;
      const avg = times.reduce((s, t) => s + t, 0) / times.length;
      const stats = engine.stats();
      el.textContent =
        `fps ${(1000 / avg).toFixed(0)}  p95 ${p95.toFixed(1)}ms\n` +
        `draws ${stats.drawCalls}  tris ${(stats.triangles / 1000).toFixed(0)}k\n` +
        engine.rendererString.slice(0, 64);
    }
    raf = requestAnimationFrame(tick);
  };
  raf = requestAnimationFrame(tick);

  return () => {
    cancelAnimationFrame(raf);
    el.remove();
  };
}
