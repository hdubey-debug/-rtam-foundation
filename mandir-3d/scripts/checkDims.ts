/** npm run check:dims — the datum gate.
 * Prints the full dimension report as JSON (the codex advisor's eyes) and
 * exits non-zero if any assertion fails.
 */
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { dimsReport, assertDims } from "../src/geometry/dimensions";
import { assertOpenings, openingSchedule } from "../src/geometry/openings";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

const report = {
  ...dimsReport(),
  openingSchedule,
  openingFailures: assertOpenings(),
};

const out = join(ROOT, "shots", "dims-report.json");
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify(report, null, 2));

const failures = [...assertDims(), ...assertOpenings()];
console.log(`dims report → ${out}`);
if (failures.length) {
  console.error(`\n${failures.length} datum failure(s):`);
  failures.forEach((f) => console.error(`  - ${f}`));
  process.exit(1);
}
// print what was actually checked — a bare PASS overstates the gate
const { assertionsChecked } = await import("../src/geometry/dimensions");
console.log(`check:dims PASS — ${assertionsChecked.length} assertion groups:`);
assertionsChecked.forEach((a) => console.log(`  ✓ ${a}`));
