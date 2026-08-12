/** Headless shot harness (SwiftShader = geometry/regression oracle only —
 * beauty and perf belong to the founder's real browser).
 *
 *   node scripts/shoot.mjs [--views front,hero,...] [--item fixture]
 *                          [--tag M0] [--export]
 *
 * Per view: boots the app in ?shot=1 mode, waits for the GENERATION-SCOPED
 * done payload (key must match the requested {item, view} — stale dones
 * can't satisfy it), then requires TWO consecutive byte-identical captures.
 * Console errors and page errors collected from before navigation; any at
 * all fail the run. Renderer string must contain "SwiftShader" (probe-
 * verified on this machine with default chromium flags).
 *
 * --export: pulls the export-clone GLB out of the page and validates it
 * node-side with @gltf-transform: meshes present, every material carries
 * explicit non-default PBR (the r185 node-material fallback is metallic 0 /
 * roughness 1 / white — exactly the failure we guard against).
 */
import { createServer } from "vite";
import { chromium } from "playwright";
import { mkdirSync, writeFileSync, copyFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SHOTS = join(ROOT, "shots");

// ---- args
const args = process.argv.slice(2);
const argOf = (name) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 && args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : null;
};
const VIEWS = (argOf("views") ?? "front,hero,side,rear,top").split(",").map((s) => s.trim());
const ITEM = argOf("item") ?? "fixture";
const TAG = argOf("tag");
const LAYERS = argOf("layers"); // e.g. "wire" | "xray" | "wire,xray"
const DO_EXPORT = args.includes("--export");
const DO_ROUNDTRIP = args.includes("--roundtrip");

const failures = [];
const note = (msg) => console.log(msg);
const fail = (msg) => {
  failures.push(msg);
  console.error(`FAIL: ${msg}`);
};

mkdirSync(SHOTS, { recursive: true });

// ---- server (programmatic; never hardcode the port — read resolvedUrls)
const server = await createServer({ root: ROOT, server: { host: "127.0.0.1" } });
await server.listen();
const url = server.resolvedUrls?.local?.[0];
if (!url) {
  console.error("vite gave no resolved URL");
  process.exit(1);
}
note(`vite dev server: ${url}`);

const browser = await chromium.launch({ headless: true });
const measures = { item: ITEM, url: null, renderer: null, views: {}, errors: {} };

async function shootView(view) {
  const key = `${ITEM}::${view}`;
  const page = await browser.newPage({
    viewport: { width: 1600, height: 1000 },
    deviceScaleFactor: 1,
  });
  const errors = [];
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(`console.error: ${m.text()}`);
  });
  page.on("pageerror", (e) => errors.push(`pageerror: ${e.message}`));

  try {
    const layerQ = LAYERS ? `&layers=${LAYERS}` : "";
    await page.goto(`${url}?shot=1&item=${ITEM}&view=${view}${layerQ}`, { timeout: 60000 });
    await page.waitForFunction(
      (k) => window.__mandirShot?.done === true && window.__mandirShot?.key === k,
      key,
      { timeout: 120000, polling: 100 },
    );
    const state = await page.evaluate(() => window.__mandirShot);
    const payload = state.payload;

    // two consecutive stable captures
    let a = await page.screenshot();
    let b = null;
    let stable = false;
    for (let i = 0; i < 7; i++) {
      await page.waitForTimeout(250);
      b = await page.screenshot();
      if (a.equals(b)) {
        stable = true;
        break;
      }
      a = b;
    }
    if (!stable) fail(`${view}: captures never stabilized (7 attempts)`);

    const suffix = LAYERS ? `--${LAYERS.replace(",", "-")}` : "";
    const file = join(SHOTS, `${ITEM}--${view}${suffix}.png`);
    writeFileSync(file, b ?? a);
    note(`shot: ${file}`);

    if (!payload?.renderer?.includes("SwiftShader")) {
      fail(`${view}: UNMASKED_RENDERER lacks SwiftShader → "${payload?.renderer}"`);
    }
    for (const c of payload?.measures?.checks ?? []) {
      if (!c.ok) fail(`${view}: measure "${c.name}" got ${c.got.toFixed(4)} want ${c.want.toFixed(4)} (±${c.tolM})`);
    }
    measures.renderer = payload?.renderer ?? null;
    measures.views[view] = payload;
    if (errors.length) {
      measures.errors[view] = errors;
      errors.forEach((e) => fail(`${view}: ${e}`));
    }
  } catch (e) {
    fail(`${view}: ${e.message?.slice(0, 300)}`);
    try {
      writeFileSync(join(SHOTS, `${ITEM}--${view}--FAILED.png`), await page.screenshot());
    } catch {
      /* page may be gone */
    }
  } finally {
    await page.close();
  }
}

async function exportSmoke() {
  const key = `${ITEM}::front`;
  const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
  const errors = [];
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  page.on("pageerror", (e) => errors.push(e.message));
  try {
    await page.goto(`${url}?shot=1&item=${ITEM}&view=front`, { timeout: 60000 });
    await page.waitForFunction(
      (k) => window.__mandirShot?.done === true && window.__mandirShot?.key === k,
      key,
      { timeout: 120000, polling: 100 },
    );
    const b64 = await page.evaluate(() => window.__mandirExportGlb());
    const glb = Buffer.from(b64, "base64");
    const glbPath = join(SHOTS, `${ITEM}-export.glb`);
    writeFileSync(glbPath, glb);
    note(`export: ${glbPath} (${(glb.length / 1024).toFixed(1)} KB)`);
    if (glb.length < 10_000) fail(`export GLB suspiciously small: ${glb.length} bytes`);

    const { NodeIO } = await import("@gltf-transform/core");
    const doc = await new NodeIO().readBinary(new Uint8Array(glb));
    const root = doc.getRoot();
    const meshes = root.listMeshes();
    const materials = root.listMaterials();
    note(`export: ${meshes.length} meshes, ${materials.length} materials`);

    if (meshes.length < 5) fail(`export: expected ≥5 meshes, got ${meshes.length}`);
    if (materials.length < 4) fail(`export: expected ≥4 materials, got ${materials.length}`);
    let sawMetal = false;
    let sawStone = false;
    for (const mat of materials) {
      const base = mat.getBaseColorFactor();
      const metal = mat.getMetallicFactor();
      const rough = mat.getRoughnessFactor();
      const isDefaultWhite = base.slice(0, 3).every((c) => c > 0.99);
      note(
        `  material "${mat.getName()}": base=[${base.map((c) => c.toFixed(2)).join(",")}] metal=${metal} rough=${rough}`,
      );
      if (isDefaultWhite) {
        fail(`export: material "${mat.getName()}" has default white baseColor — node-material fallback`);
      }
      if (metal >= 0.8) sawMetal = true;
      if (metal === 0 && rough > 0.5) sawStone = true;
    }
    if (!sawMetal) fail("export: no metallic material survived (gilt lost)");
    if (!sawStone) fail("export: no stone-like material survived");
    measures.export = {
      bytes: glb.length,
      meshes: meshes.length,
      materials: materials.map((m) => ({
        name: m.getName(),
        baseColor: m.getBaseColorFactor(),
        metallic: m.getMetallicFactor(),
        roughness: m.getRoughnessFactor(),
      })),
    };
    if (errors.length) errors.forEach((e) => fail(`export: ${e}`));
  } catch (e) {
    fail(`export: ${e.message?.slice(0, 300)}`);
  } finally {
    await page.close();
  }
}

async function roundtrip() {
  const key = `${ITEM}::front`;
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  page.on("pageerror", (e) => errors.push(e.message));
  try {
    await page.goto(`${url}?shot=1&item=${ITEM}&view=front`, { timeout: 60000 });
    await page.waitForFunction(
      (k) => window.__mandirShot?.done === true && window.__mandirShot?.key === k,
      key,
      { timeout: 120000, polling: 100 },
    );
    const original = (await page.evaluate(() => window.__mandirShot)).payload;
    const rt = JSON.parse(await page.evaluate(() => window.__mandirRoundtrip()));
    note(`roundtrip: ${(rt.bytes / 1024).toFixed(1)} KB reimported`);
    // reimported real bounds must match the original within the DoD ±1 cm
    for (const axis of [0, 1, 2]) {
      const dMin = Math.abs(rt.realBounds.min[axis] - original.realBounds.min[axis]);
      const dMax = Math.abs(rt.realBounds.max[axis] - original.realBounds.max[axis]);
      if (dMin > 0.01 || dMax > 0.01) {
        fail(`roundtrip: axis ${axis} bounds drifted (min ${dMin.toFixed(4)}, max ${dMax.toFixed(4)})`);
      }
    }
    await page.waitForTimeout(400);
    writeFileSync(join(SHOTS, `${ITEM}--roundtrip.png`), await page.screenshot());
    note(`shot: ${join(SHOTS, `${ITEM}--roundtrip.png`)}`);
    measures.roundtrip = { bytes: rt.bytes, realBounds: rt.realBounds };
    if (errors.length) errors.forEach((e) => fail(`roundtrip: ${e}`));
  } catch (e) {
    fail(`roundtrip: ${e.message?.slice(0, 300)}`);
  } finally {
    await page.close();
  }
}

for (const view of VIEWS) await shootView(view);
if (DO_EXPORT) await exportSmoke();
if (DO_ROUNDTRIP) await roundtrip();

measures.url = url;
measures.generatedAt = new Date().toISOString();
writeFileSync(join(SHOTS, "measures.json"), JSON.stringify(measures, null, 2));
note(`measures: ${join(SHOTS, "measures.json")}`);

if (TAG) {
  const dir = join(SHOTS, TAG);
  mkdirSync(dir, { recursive: true });
  for (const f of readdirSync(SHOTS)) {
    // archive only THIS item's artifacts + the measures — no stale strays
    const ours = f.startsWith(`${ITEM}-`) || f === "measures.json" || f === "dims-report.json";
    if (ours && (f.endsWith(".png") || f.endsWith(".json") || f.endsWith(".glb"))) {
      copyFileSync(join(SHOTS, f), join(dir, f));
    }
  }
  note(`archived → ${dir}`);
}

await browser.close();
await server.close();

if (failures.length) {
  console.error(`\n${failures.length} failure(s):`);
  failures.forEach((f) => console.error(`  - ${f}`));
  process.exit(1);
}
console.log(`\nPASS — ${VIEWS.length} views clean, renderer: ${measures.renderer}`);
