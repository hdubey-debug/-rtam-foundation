import { createServer } from "vite";
import { chromium } from "playwright";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, rmSync, statSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const valueOf = (name, fallback) => {
  const index = args.indexOf(`--${name}`);
  return index >= 0 && args[index + 1] ? args[index + 1] : fallback;
};

const model = resolve(ROOT, valueOf("model", "indian temple 3d model.glb"));
const output = resolve(ROOT, valueOf("output", "renders/indian-temple-360-hd.mp4"));
const width = Number(valueOf("width", "1920"));
const height = Number(valueOf("height", "1080"));
const fps = Number(valueOf("fps", "24"));
const seconds = Number(valueOf("seconds", "15"));
const fit = Number(valueOf("fit", "1.18"));
const crf = Number(valueOf("crf", "18"));
const frameFormat = valueOf("frame-format", "jpeg");
const frames = Math.round(fps * seconds);

if (!new Set(["jpeg", "png"]).has(frameFormat)) {
  throw new Error('--frame-format must be either "jpeg" or "png".');
}

if (!existsSync(model)) throw new Error(`Model not found: ${model}`);
if (model !== ROOT && !model.startsWith(`${ROOT}${sep}`)) {
  throw new Error("The model must be located inside the project so Vite can serve it.");
}
mkdirSync(dirname(output), { recursive: true });

const frameDir = mkdtempSync(join(tmpdir(), "temple-turntable-"));
const server = await createServer({
  root: ROOT,
  logLevel: "error",
  server: { host: "127.0.0.1" },
});

let browser;
try {
  await server.listen();
  const baseUrl = server.resolvedUrls?.local?.[0];
  if (!baseUrl) throw new Error("Vite did not provide a local URL.");

  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  page.on("console", (message) => {
    if (message.type() === "error") console.error(`browser: ${message.text()}`);
  });
  page.on("pageerror", (error) => console.error(`browser: ${error.message}`));

  const modelPath = `/${relative(ROOT, model).split(sep).map(encodeURIComponent).join("/")}`;
  await page.goto(`${baseUrl}turntable.html?model=${modelPath}&fit=${encodeURIComponent(String(fit))}`, { timeout: 120_000 });
  await page.waitForFunction(
    () => window.__turntable?.ready === true || Boolean(window.__turntable?.error),
    null,
    { timeout: 180_000, polling: 100 },
  );
  const state = await page.evaluate(() => window.__turntable);
  if (state?.error) throw new Error(state.error);
  console.log(`Loaded model: ${JSON.stringify(state?.meta)}`);
  console.log(`Rendering ${frames} frames at ${width}x${height}...`);

  for (let frame = 0; frame < frames; frame++) {
    await page.evaluate(
      ({ frame, frames }) => window.__turntable?.renderFrame?.(frame, frames),
      { frame, frames },
    );
    const extension = frameFormat === "png" ? "png" : "jpg";
    const path = join(frameDir, `frame-${String(frame).padStart(4, "0")}.${extension}`);
    await page.screenshot(
      frameFormat === "png"
        ? { path, type: "png" }
        : { path, type: "jpeg", quality: 100 },
    );
    if (frame === 0 || (frame + 1) % 24 === 0 || frame === frames - 1) {
      console.log(`  frame ${frame + 1}/${frames}`);
    }
  }

  const poster = output.replace(/\.mp4$/i, "-poster.jpg");
  execFileSync(
    "ffmpeg",
    [
      "-y",
      "-hide_banner",
      "-loglevel",
      "warning",
      "-framerate",
      String(fps),
      "-i",
      join(frameDir, `frame-%04d.${frameFormat === "png" ? "png" : "jpg"}`),
      "-c:v",
      "libx264",
      "-preset",
      "medium",
      "-crf",
      String(crf),
      "-tune",
      "animation",
      "-pix_fmt",
      "yuv420p",
      "-movflags",
      "+faststart",
      output,
    ],
    { stdio: "inherit" },
  );
  execFileSync(
    "ffmpeg",
    ["-y", "-hide_banner", "-loglevel", "warning", "-i", output, "-frames:v", "1", "-update", "1", poster],
    { stdio: "inherit" },
  );
  console.log(`Video: ${output} (${(statSync(output).size / 1024 / 1024).toFixed(1)} MB)`);
  console.log(`Poster: ${poster}`);
} finally {
  if (browser) await browser.close();
  await server.close();
  rmSync(frameDir, { recursive: true, force: true });
}
