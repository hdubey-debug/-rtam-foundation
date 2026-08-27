/** QA screenshots of dist/murti-measured.html (file://, SwiftShader).
 *  node shoot.mjs [name=query ...]   e.g. node shoot.mjs study="view=study&panel=0" */
import { chromium } from "../mandir-3d/node_modules/playwright/index.mjs";
import { mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = resolve(dirname(fileURLToPath(import.meta.url)));
const FILE = `file://${join(HERE, "dist/murti-measured.html")}`;
const SHOTS = join(HERE, "shots");
mkdirSync(SHOTS, { recursive: true });

const DEFAULT = [
  ["study", "view=study&panel=1"],
  ["front", "view=front&panel=0"],
  ["wheel", "view=wheel&panel=0"],
  ["heart", "view=heart&panel=0"],
  ["exploded", "view=study&explode=1&panel=0"],
  ["image-study", "view=study&preset=image&panel=1"],
  ["guides-wheel", "view=wheel&guides=1&panel=0"],
];
const args = process.argv.slice(2);
const jobs = args.length ? args.map((a) => a.split("=", 1).concat(a.slice(a.indexOf("=") + 1))) : DEFAULT;

const browser = await chromium.launch({ headless: true });
let failed = 0;
for (const [name, query] of jobs) {
  const page = await browser.newPage({ viewport: { width: 1640, height: 1020 } });
  const errs = [];
  page.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  page.on("pageerror", (e) => errs.push(String(e.message)));
  try {
    await page.goto(`${FILE}?shot=1&${query}`, { timeout: 30000 });
    await page.waitForFunction(() => window.__murtiShot?.done === true, null, { timeout: 30000, polling: 100 });
    await page.waitForTimeout(350);
    await page.screenshot({ path: join(SHOTS, `${name}.png`) });
    console.log(`shot: ${name}.png${errs.length ? `  [${errs.length} console error(s)]` : ""}`);
    for (const e of errs) { console.error(`   ERR ${e.slice(0, 240)}`); failed++; }
  } catch (e) {
    failed++;
    console.error(`FAIL ${name}: ${String(e.message).slice(0, 300)}`);
    try { await page.screenshot({ path: join(SHOTS, `${name}--FAILED.png`) }); } catch {}
  }
  await page.close();
}
await browser.close();
process.exit(failed ? 1 : 0);
