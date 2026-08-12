/** The LOCKED column (doc §2.3, exactly as rendered): pedestal · two-step
 * molded base · recessed-panel shaft · neck band · three-course bracket.
 * Scale comes from the two hard endpoints (terrace → porch beam soffit);
 * the du ratios distribute between them. The recessed panel is made by a
 * PROUD frame (applied ≥2 mm parts, no CSG) — the field between frames
 * reads as the recess.
 *
 * Returns TWO merged geometries (granite pedestal / plaster stack) so the
 * colonnade instances stay material-homogeneous. Origin: pedestal base
 * center at y=0; total height = columnSpec.totalH.
 */
import * as THREE from "three/webgpu";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { columnSpec } from "./dimensions";

export interface ColumnGeometry {
  pedestal: THREE.BufferGeometry;
  upper: THREE.BufferGeometry;
  totalH: number;
}

const box = (w: number, h: number, d: number, y: number): THREE.BufferGeometry => {
  const g = new THREE.BoxGeometry(w, h, d);
  g.translate(0, y + h / 2, 0);
  return g;
};

export function buildColumnGeometry(): ColumnGeometry {
  const H = columnSpec.totalH.v;
  const r = columnSpec.ratios;
  const w = columnSpec.widths;

  const hPedestal = H * r.pedestal;
  const hBase = H * r.base;
  const hShaft = H * r.shaft;
  const hNeck = H * r.neck;
  const hBracket = H * r.bracket;

  // ---- pedestal (granite, plain)
  const pedestal = box(w.pedestal, hPedestal, w.pedestal, 0);

  // ---- the plaster stack
  const parts: THREE.BufferGeometry[] = [];
  let y = hPedestal;

  // two-step molded base
  const hStep = hBase / 2;
  parts.push(box(w.baseSteps[0], hStep, w.baseSteps[0], y));
  parts.push(box(w.baseSteps[1], hStep, w.baseSteps[1], y + hStep));
  y += hBase;

  // shaft with proud panel frames on all four faces
  parts.push(box(w.shaft, hShaft, w.shaft, y));
  {
    const f = columnSpec.panelFrameW;
    const proud = columnSpec.panelFrameProud;
    const inset = 0.02; // frame margin from the shaft arris
    const frameH = hShaft - 2 * inset;
    const frameW = w.shaft - 2 * inset;
    const half = w.shaft / 2 + proud / 2;
    for (const [rot, sx, sz] of [
      [0, 0, half], // +z face
      [Math.PI, 0, -half], // −z face
      [Math.PI / 2, half, 0], // +x face
      [-Math.PI / 2, -half, 0], // −x face
    ] as [number, number, number][]) {
      // frame = two verticals + two horizontals, proud of the face
      const mk = (fw: number, fh: number, ox: number, oy: number): THREE.BufferGeometry => {
        const g = new THREE.BoxGeometry(fw, fh, proud);
        g.translate(ox, 0, 0);
        g.rotateY(rot);
        g.translate(sx, y + inset + frameH / 2 + oy, sz);
        return g;
      };
      parts.push(mk(f, frameH, -(frameW / 2 - f / 2), 0));
      parts.push(mk(f, frameH, frameW / 2 - f / 2, 0));
      parts.push(mk(frameW - 2 * f, f, 0, frameH / 2 - f / 2));
      parts.push(mk(frameW - 2 * f, f, 0, -(frameH / 2 - f / 2)));
    }
  }
  y += hShaft;

  // neck band
  parts.push(box(w.neck, hNeck, w.neck, y));
  y += hNeck;

  // three corbelled bracket courses, widening to carry the beam
  const hCourse = hBracket / 3;
  for (let i = 0; i < 3; i++) {
    parts.push(box(w.bracketSteps[i], hCourse, w.bracketSteps[i], y + i * hCourse));
  }

  const upper = mergeGeometries(parts)!;
  parts.forEach((g) => g.dispose());

  return { pedestal, upper, totalH: H };
}
