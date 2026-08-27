/** Shoot reference views of a GLB: node glb-shots.mjs "<glb path>" [outprefix] */
import { build } from "../mandir-3d/node_modules/esbuild/lib/main.js";
import { chromium } from "../mandir-3d/node_modules/playwright/index.mjs";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = resolve(dirname(fileURLToPath(import.meta.url)));
const GLB = process.argv[2] || join(HERE, "../monolith pedestal 3d model.glb");
const PREFIX = process.argv[3] || "ref";
mkdirSync(join(HERE, "shots"), { recursive: true });

const r = await build({
  entryPoints: [join(HERE, "src/glbview.js")], bundle: true, minify: true, format: "iife",
  write: false, nodePaths: [join(HERE, "../mandir-3d/node_modules")], logLevel: "warning",
});
const html = `<!doctype html><meta charset="utf-8"><title>glb</title><body><script>${r.outputFiles[0].text.replaceAll("</script", "<\\/script")}</script></body>`;
const page_path = join(HERE, "dist/glb-view.html");
writeFileSync(page_path, html);

// serve page + GLB over http — fetch() cannot load file:// URLs
const { createServer } = await import("node:http");
const glbBuf = readFileSync(GLB);
const srv = createServer((req, res) => {
  if (req.url.startsWith("/model.glb")) { res.writeHead(200, { "content-type": "model/gltf-binary" }); res.end(glbBuf); }
  else { res.writeHead(200, { "content-type": "text/html" }); res.end(html); }
});
await new Promise((ok) => srv.listen(0, "127.0.0.1", ok));
const port = srv.address().port;
const browser = await chromium.launch({ headless: true });
for (const view of ["front", "quarter", "top"]) {
  const page = await browser.newPage({ viewport: { width: 1400, height: 1100 } });
  page.on("pageerror", (e) => console.error("pageerror:", String(e.message).slice(0, 200)));
  await page.goto(`http://127.0.0.1:${port}/?view=${view}`, { timeout: 60000 });
  await page.waitForFunction(() => window.__glbShot?.done === true, null, { timeout: 240000 });
  await page.waitForTimeout(250);
  await page.screenshot({ path: join(HERE, `shots/${PREFIX}-${view}.png`) });
  console.log(`shot: shots/${PREFIX}-${view}.png`);
  await page.close();
}
await browser.close();
srv.close();
