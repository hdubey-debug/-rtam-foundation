/** The Horizontal Question — shoot the five candidate systems (front + wheel).
 *  All share the LOCKED verticals + Ø58 liṅga + Ø187 podium (grammar preset);
 *  only the open rings differ. node board-shots.mjs */
import { chromium } from "../mandir-3d/node_modules/playwright/index.mjs";
import { mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = resolve(dirname(fileURLToPath(import.meta.url)));
const FILE = `file://${join(HERE, "dist/murti-measured.html")}`;
const OUT = join(HERE, "shots/board");
mkdirSync(OUT, { recursive: true });

// open rings per candidate: collar/throat · cup · tips · lotus · water (+ sun-ring)
const NOMEAS = { "display.measures": false };
const CANDIDATES = {
  A: { ...NOMEAS }, // as-provisional 73/92/109/121/151 — the grammar preset itself
  B: { ...NOMEAS, "rings.jaladhari": 0.3797, "rings.cupOuter": 0.4599, "rings.tier1PetalTip": 0.5561,
       "rings.tier2PetalTip": 0.6791, "rings.waterOuter": 0.8235, "rings.medallionCenter": 0.9118 },
  C: { ...NOMEAS, "rings.tier1PetalTip": 0.5668, "rings.waterOuter": 0.8396, "rings.medallionCenter": 0.9198 },
  D: { ...NOMEAS, "rings.waterOuter": 0.7754, "rings.medallionCenter": 0.8877 },
  E: { ...NOMEAS, "rings.tier2PetalTip": 0.6845, "rings.waterOuter": 0.8289, "rings.medallionCenter": 0.9144 },
};

const browser = await chromium.launch({ headless: true });
let failed = 0;
for (const [name, over] of Object.entries(CANDIDATES)) {
  for (const view of ["front", "wheel"]) {
    const page = await browser.newPage({ viewport: { width: 1640, height: 1020 } });
    const errs = [];
    page.on("pageerror", (e) => errs.push(String(e.message)));
    try {
      const overQ = over ? `&over=${encodeURIComponent(JSON.stringify(over))}` : "";
      await page.goto(`${FILE}?shot=1&preset=grammar&view=${view}&panel=0${overQ}`, { timeout: 30000 });
      await page.waitForFunction(() => window.__murtiShot?.done === true, null, { timeout: 30000 });
      await page.waitForTimeout(300);
      await page.screenshot({ path: join(OUT, `${name}-${view}.png`) });
      console.log(`shot: ${name}-${view}.png${errs.length ? ` [${errs.length} err]` : ""}`);
      errs.forEach((e) => { console.error(`  ERR ${e.slice(0, 200)}`); failed++; });
    } catch (e) { failed++; console.error(`FAIL ${name}-${view}: ${String(e.message).slice(0, 200)}`); }
    await page.close();
  }
}
await browser.close();
process.exit(failed ? 1 : 0);
