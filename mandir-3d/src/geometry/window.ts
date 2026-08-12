/** The LOCKED window template (doc §2.5, Fig 6 chain): projecting head
 * cap + drip · dentil blocks · architrave step · raised frame band
 * ~140 mm · [clear jali opening] · molded sill + drip · corbel blocks.
 *
 * Jali is a SEPARATE STUDY — the placeholder is a NEUTRAL orthogonal
 * grille with non-symbolic counts (5×7; never 12 — law 3). The reserved
 * "screen" (the pierced chakra) never appears.
 *
 * Returns TWO merged geometries per size (plaster parts / dark jali) so
 * every window on the building instances from 4 total draws. Origin:
 * OPENING CENTER, wall exterior face at z=0, proud parts +z, jali −z.
 */
import * as THREE from "three/webgpu";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { windowSpec } from "./dimensions";

export interface WindowGeometry {
  plaster: THREE.BufferGeometry;
  jali: THREE.BufferGeometry;
  /** full unit height incl. head/sill extras (for collision checks) */
  unitH: number;
  unitW: number;
}

const box = (w: number, h: number, d: number, x: number, y: number, z: number): THREE.BufferGeometry => {
  const g = new THREE.BoxGeometry(w, h, d);
  g.translate(x, y, z);
  return g;
};

export function buildWindowGeometry(openingH: number): WindowGeometry {
  const w = windowSpec.openingW.v;
  const b = windowSpec.bandM.v;
  const p = windowSpec.parts;

  const plasterParts: THREE.BufferGeometry[] = [];
  const jaliParts: THREE.BufferGeometry[] = [];

  const hw = w / 2;
  const hh = openingH / 2;

  // ---- raised frame band (the doc's 140 mm anchor), proud of the wall
  {
    const d = p.bandProud;
    plasterParts.push(box(b, openingH + 2 * b, d, -(hw + b / 2), 0, d / 2));
    plasterParts.push(box(b, openingH + 2 * b, d, hw + b / 2, 0, d / 2));
    plasterParts.push(box(w, b, d, 0, hh + b / 2, d / 2));
    plasterParts.push(box(w, b, d, 0, -(hh + b / 2), d / 2));
  }
  const frameHalfW = hw + b;
  const frameHalfH = hh + b;

  // ---- architrave step around the frame
  {
    const a = p.architraveStep;
    const d = p.architraveProud;
    plasterParts.push(box(a, openingH + 2 * b + 2 * a, d, -(frameHalfW + a / 2), 0, d / 2));
    plasterParts.push(box(a, openingH + 2 * b + 2 * a, d, frameHalfW + a / 2, 0, d / 2));
    plasterParts.push(box(2 * frameHalfW, a, d, 0, frameHalfH + a / 2, d / 2));
    plasterParts.push(box(2 * frameHalfW, a, d, 0, -(frameHalfH + a / 2), d / 2));
  }
  const archHalfW = frameHalfW + p.architraveStep;
  const archTop = frameHalfH + p.architraveStep;

  // ---- dentil row above the architrave (centered residual — pitches
  // never stretch; count is size-derived and non-system)
  {
    const pitch = p.dentilW + p.dentilGap;
    const count = Math.max(3, Math.floor((2 * archHalfW) / pitch));
    const rowW = count * pitch - p.dentilGap;
    const y = archTop + p.dentilH / 2;
    for (let i = 0; i < count; i++) {
      const x = -rowW / 2 + p.dentilW / 2 + i * pitch;
      plasterParts.push(box(p.dentilW, p.dentilH, p.dentilProud, x, y, p.dentilProud / 2));
    }
  }
  const dentilTop = archTop + p.dentilH;

  // ---- projecting head cap with a REAL drip lip: it hangs BELOW the
  // cap's front underside (GEO audit: the old lip was fully embedded)
  {
    const capW = 2 * archHalfW + 0.08;
    const y = dentilTop + p.headCapH / 2;
    plasterParts.push(box(capW, p.headCapH, p.headCapProud, 0, y, p.headCapProud / 2));
    plasterParts.push(box(capW - 0.03, 0.024, 0.02, 0, dentilTop - 0.012, p.headCapProud - 0.012));
  }

  // ---- molded sill + drip (lip hangs below the sill front), corbels
  {
    const sillW = 2 * frameHalfW + 0.1;
    const ySill = -(frameHalfH + p.sillH / 2);
    plasterParts.push(box(sillW, p.sillH, p.sillProud, 0, ySill, p.sillProud / 2));
    plasterParts.push(box(sillW - 0.03, 0.024, 0.02, 0, ySill - p.sillH / 2 - 0.012, p.sillProud - 0.012));
    const yCorbel = -(frameHalfH + p.sillH + p.corbelH / 2);
    const spread = w * 0.72;
    const n: number = p.corbelCount;
    for (let i = 0; i < n; i++) {
      const x = n === 1 ? 0 : -spread / 2 + (i * spread) / (n - 1);
      plasterParts.push(box(p.corbelW, p.corbelH, p.corbelProud, x, yCorbel, p.corbelProud / 2));
    }
  }

  // ---- jali placeholder: dark backing + neutral orthogonal grille
  {
    const zBack = -p.jaliInset - 0.02;
    jaliParts.push(box(w - 0.02, openingH - 0.02, 0.02, 0, 0, zBack));
    const t = p.jaliBarT;
    const zBar = -p.jaliInset;
    for (let i = 1; i <= p.jaliBarsV; i++) {
      const x = -hw + (i * w) / (p.jaliBarsV + 1);
      jaliParts.push(box(t, openingH - 0.02, t, x, 0, zBar));
    }
    for (let j = 1; j <= p.jaliBarsH; j++) {
      const y = -hh + (j * openingH) / (p.jaliBarsH + 1);
      jaliParts.push(box(w - 0.02, t, t, 0, y, zBar));
    }
  }

  const plaster = mergeGeometries(plasterParts)!;
  const jali = mergeGeometries(jaliParts)!;
  [...plasterParts, ...jaliParts].forEach((g) => g.dispose());

  return {
    plaster,
    jali,
    unitH: openingH + 2 * b + p.architraveStep + p.dentilH + p.headCapH + p.sillH + p.corbelH,
    unitW: 2 * archHalfW + 0.08,
  };
}
