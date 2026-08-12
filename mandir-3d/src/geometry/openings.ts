/** THE OPENING SCHEDULE — every exterior opening keyed facade × floor ×
 * bay, each with a status. This is the auditable spec the wall builders
 * consume; nothing places a window except through this table.
 *
 * Law 3 gate: no facade run may carry a system number (12/24) of
 * repeating openings — the count is checked, not pretended away. Facade
 * counts here are RENDER-DERIVED AND PROVISIONAL except the front's
 * door-centered five-bay reading.
 *
 * front = the dvāra face (east — the equinox door axis, D2).
 */

export type Facade = "front" | "rear" | "left" | "right";
export type Floor = "L1" | "L2";
export type OpeningKind = "window" | "door" | "blind";
export type OpeningStatus = "locked" | "provisional";

export interface OpeningSlot {
  facade: Facade;
  floor: Floor;
  /** bay index, 0 at the left corner looking AT the facade */
  bay: number;
  kind: OpeningKind;
  status: OpeningStatus;
  note?: string;
}

const run = (
  facade: Facade,
  floor: Floor,
  kinds: OpeningKind[],
  status: OpeningStatus,
  note?: string,
): OpeningSlot[] =>
  kinds.map((kind, bay) => ({ facade, floor, bay, kind, status, ...(note ? { note } : {}) }));

const W = "window" as const;
const D = "door" as const;

export const openingSchedule: OpeningSlot[] = [
  // front — five bays, the ring broken toward the devotee at the center
  ...run("front", "L1", [W, W, D, W, W], "locked", "door-centered five-bay front, as rendered"),
  ...run("front", "L2", [W, W, W, W, W], "provisional"),
  // long sides — TEN bays: the ten-bay closure derives the porch from the
  // depth exactly (codex DIMS); render reads 10–11; 12 is barred by law 3
  ...run("left", "L1", Array(10).fill(W), "provisional"),
  ...run("left", "L2", Array(10).fill(W), "provisional"),
  ...run("right", "L1", Array(10).fill(W), "provisional"),
  ...run("right", "L2", Array(10).fill(W), "provisional"),
  // rear — quiet five-bay mirror; service openings stay "quiet grammar"
  ...run("rear", "L1", [W, W, W, W, W], "provisional", "rear center may become a service door — open study"),
  ...run("rear", "L2", [W, W, W, W, W], "provisional"),
];

export function openingsFor(facade: Facade, floor: Floor): OpeningSlot[] {
  return openingSchedule
    .filter((s) => s.facade === facade && s.floor === floor)
    .sort((a, b) => a.bay - b.bay);
}

/** Law 3: system numbers (12/24) never ride a repeating element.
 *
 * Checked at every scope the schedule can express: per facade-floor, per
 * facade (both floors), per floor around the whole perimeter, corner-
 * adjacent pairs, and the building total. Segment topology RESOLVED at
 * M5: pilasters sit at bay boundaries and do not split runs — each
 * facade-floor is exactly one contiguous run, which the scopes above
 * already count. No further machinery needed.
 */
export function assertOpenings(): string[] {
  const errs: string[] = [];
  const facades: Facade[] = ["front", "rear", "left", "right"];
  const floors: Floor[] = ["L1", "L2"];
  const SYSTEM = [12, 24];
  const windowCount = (slots: OpeningSlot[]) => slots.filter((s) => s.kind === "window").length;
  const flag = (scope: string, n: number) => {
    if (SYSTEM.includes(n)) errs.push(`law 3: ${scope} carries ${n} — a system number on a repeating run`);
  };

  for (const f of facades) {
    for (const fl of floors) {
      const slots = openingsFor(f, fl);
      flag(`${f} ${fl} bays`, slots.length);
      flag(`${f} ${fl} windows`, windowCount(slots));
      slots.forEach((s, i) => {
        if (s.bay !== i) errs.push(`${f} ${fl}: bay indices not contiguous at ${i}`);
      });
    }
    flag(`${f} both-floor windows`, windowCount(openingSchedule.filter((s) => s.facade === f)));
  }
  for (const fl of floors) {
    flag(`${fl} perimeter windows`, windowCount(openingSchedule.filter((s) => s.floor === fl)));
  }
  // corner-adjacent pairs (a run continuing around a corner)
  const cornerPairs: [Facade, Facade][] = [
    ["front", "left"],
    ["front", "right"],
    ["rear", "left"],
    ["rear", "right"],
  ];
  for (const [a, b] of cornerPairs) {
    for (const fl of floors) {
      flag(
        `${a}+${b} ${fl} corner run`,
        windowCount(openingSchedule.filter((s) => s.floor === fl && (s.facade === a || s.facade === b))),
      );
    }
  }
  flag("building total windows", windowCount(openingSchedule));

  // structural integrity: expected rhythm, symmetry, floor alignment
  const expect = (cond: boolean, msg: string) => {
    if (!cond) errs.push(msg);
  };
  expect(openingsFor("front", "L1").length === 5, "front L1 must be the five-bay dvāra face");
  expect(openingsFor("front", "L1")[2]?.kind === "door", "front L1 center bay must be the door");
  expect(openingsFor("front", "L1").filter((s) => s.kind === "door").length === 1, "exactly one front door");
  expect(openingsFor("front", "L2").length === 5, "front L2 must mirror the five bays");
  expect(openingsFor("rear", "L1").length === 5 && openingsFor("rear", "L2").length === 5, "rear is a five-bay face");
  for (const fl of floors) {
    expect(
      openingsFor("left", fl).length === openingsFor("right", fl).length,
      `left/right ${fl} bay counts must mirror`,
    );
    expect(openingsFor("left", fl).length === 10, `long sides carry ten bays (${fl}) — the ten-bay closure`);
  }
  for (const f of facades) {
    expect(
      openingsFor(f, "L1").length === openingsFor(f, "L2").length,
      `${f}: L1/L2 bay counts must align on shared axes`,
    );
  }

  return errs;
}
