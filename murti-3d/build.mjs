/** Bundle src/app.js (+ three from mandir-3d's node_modules) into one
 *  self-contained dist/murti-measured.html — the artifact file. */
import { build } from "../mandir-3d/node_modules/esbuild/lib/main.js";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = resolve(dirname(fileURLToPath(import.meta.url)));

const result = await build({
  entryPoints: [join(HERE, "src/app.js")],
  bundle: true,
  minify: true,
  format: "iife",
  write: false,
  nodePaths: [join(HERE, "../mandir-3d/node_modules")],
  logLevel: "warning",
});
let js = result.outputFiles[0].text;
js = js.replaceAll("</script", "<\\/script"); // keep the inline <script> intact

const html = readFileSync(join(HERE, "src/template.html"), "utf8").replace("__APP__", () => js);
mkdirSync(join(HERE, "dist"), { recursive: true });
const out = join(HERE, "dist/murti-measured.html");
writeFileSync(out, html);
console.log(`wrote ${out} (${(html.length / 1024).toFixed(0)} KB)`);
