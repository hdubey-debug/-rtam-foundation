/** The walls — four extruded panels (Shape-with-holes) whose openings
 * come EXCLUSIVELY from openings.ts, plus instanced pilasters, the
 * instanced window template (4 draws for every window on the building),
 * and the door. Facade conventions per dimensions.facadeConventions:
 * front/rear = five bays centered between corner piers; sides = ten bays
 * corner-to-corner. Panels for front/rear are trimmed by the wall
 * thickness so side-wall end faces stay ADJACENT (coplanar neighbors on
 * one architectural plane), never overlapping.
 *
 * Local frame: body center at origin, front face at +bodyDepth/2.
 * Group "body" holds ONLY the wall solids (measures bind to it);
 * applied parts live in "body-applied"; the door is its own group.
 */
import * as THREE from "three/webgpu";
import type { MaterialLib } from "../materials/materials";
import {
  bodyDepth,
  doorSpec,
  envelopes,
  facadeConventions,
  facadeGrid,
  pilasterSpec,
  stations,
  windowSpec,
} from "./dimensions";
import { openingsFor, type Facade } from "./openings";
import { buildWindowGeometry } from "./window";
import { buildDoor } from "./door";
import type { BuiltPart } from "./podium";

interface FacadeDef {
  facade: Facade;
  width: number;
  angle: number;
  plane: number;
  margin: number;
  trim: number;
}

export function buildWalls(lib: MaterialLib): BuiltPart {
  const group = new THREE.Group();
  group.name = "walls-and-openings";

  const sW = envelopes.structuralW.v;
  const bD = bodyDepth.v;
  const t = envelopes.wallThickness.v;
  const bay = facadeGrid.bayW.v;
  const wallBase = stations.podiumTopY.v;
  const wallTop = stations.plateY.v;
  const wallH = wallTop - wallBase;

  const FACADES: FacadeDef[] = [
    { facade: "front", width: sW, angle: 0, plane: bD / 2, margin: facadeConventions.cornerPierW.v, trim: t },
    { facade: "rear", width: sW, angle: Math.PI, plane: bD / 2, margin: facadeConventions.cornerPierW.v, trim: t },
    { facade: "right", width: bD, angle: Math.PI / 2, plane: sW / 2, margin: 0, trim: 0 },
    { facade: "left", width: bD, angle: -Math.PI / 2, plane: sW / 2, margin: 0, trim: 0 },
  ];

  const uCenter = (def: FacadeDef, bayIdx: number) => -def.width / 2 + def.margin + (bayIdx + 0.5) * bay;

  /** local facade coords (u along the facade, y up, exterior at z=0)
   * → world position on that facade plane */
  const toWorld = (def: FacadeDef, u: number, y: number, out = new THREE.Vector3()) => {
    const cos = Math.cos(def.angle);
    const sin = Math.sin(def.angle);
    // rotY(angle) applied to (u, y, plane)
    return out.set(u * cos + def.plane * sin, y, -u * sin + def.plane * cos);
  };

  // ---- wall panels (group "body" — the measures bind here)
  const body = new THREE.Group();
  body.name = "body";
  group.add(body);

  const holeRect = (path: THREE.Path, cx: number, cy: number, hw: number, hh: number) => {
    // holes wind opposite the outer shape
    path.moveTo(cx - hw, cy - hh);
    path.lineTo(cx - hw, cy + hh);
    path.lineTo(cx + hw, cy + hh);
    path.lineTo(cx + hw, cy - hh);
    path.closePath();
  };

  for (const def of FACADES) {
    const half = def.width / 2 - def.trim;

    // the DOOR is a NOTCH in the outer contour, never an edge-touching
    // hole (GEO audit: a hole sharing the bottom edge makes the extruder
    // emit duplicate coplanar sidewalls at the threshold)
    const doorSlots = openingsFor(def.facade, "L1").filter((s) => s.kind === "door");
    const shape = new THREE.Shape();
    shape.moveTo(-half, wallBase);
    for (const slot of doorSlots.sort((a, b) => a.bay - b.bay)) {
      const u = uCenter(def, slot.bay);
      shape.lineTo(u - doorSpec.w.v / 2, wallBase);
      shape.lineTo(u - doorSpec.w.v / 2, wallBase + doorSpec.h.v);
      shape.lineTo(u + doorSpec.w.v / 2, wallBase + doorSpec.h.v);
      shape.lineTo(u + doorSpec.w.v / 2, wallBase);
    }
    shape.lineTo(half, wallBase);
    shape.lineTo(half, wallTop);
    shape.lineTo(-half, wallTop);
    shape.closePath();

    for (const floor of ["L1", "L2"] as const) {
      const openingH = floor === "L1" ? windowSpec.l1OpeningH.v : windowSpec.l2OpeningH.v;
      const sillY = floor === "L1" ? stations.l1SillY.v : stations.l2SillY.v;
      for (const slot of openingsFor(def.facade, floor)) {
        if (slot.kind !== "window") continue;
        const u = uCenter(def, slot.bay);
        const path = new THREE.Path();
        holeRect(path, u, sillY + openingH / 2, windowSpec.openingW.v / 2, openingH / 2);
        shape.holes.push(path);
      }
    }

    const geo = new THREE.ExtrudeGeometry(shape, { depth: t, bevelEnabled: false });
    geo.translate(0, 0, -t); // exterior face at z=0, solid behind
    geo.rotateY(def.angle);
    const mesh = new THREE.Mesh(geo, lib.plaster);
    mesh.name = `wall-${def.facade}`;
    mesh.position.set(def.plane * Math.sin(def.angle), 0, def.plane * Math.cos(def.angle));
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    body.add(mesh);
  }

  // ---- applied parts
  const applied = new THREE.Group();
  applied.name = "body-applied";
  group.add(applied);

  // pilasters at bay boundaries + corner pilasters on the piers
  {
    const mk = (w: number): THREE.BufferGeometry => {
      const g = new THREE.BoxGeometry(w, wallH, pilasterSpec.proud.v);
      g.translate(0, wallBase + wallH / 2, pilasterSpec.proud.v / 2);
      return g;
    };
    const placements: { def: FacadeDef; u: number; corner: boolean }[] = [];
    for (const def of FACADES) {
      const slots = openingsFor(def.facade, "L1");
      const bays = slots.length;
      const doorSlot = slots.find((s) => s.kind === "door");
      const doorU = doorSlot ? uCenter(def, doorSlot.bay) : null;
      const start = -def.width / 2 + def.margin;
      const from = def.margin > 0 ? 0 : 1;
      const to = def.margin > 0 ? bays : bays - 1;
      for (let i = from; i <= to; i++) {
        const u = start + i * bay;
        // the dvāra trim owns its bay — the two flanking pilasters yield
        // (GEO audit: the outer jamb overlapped them)
        if (doorU !== null && Math.abs(u - doorU) < bay * 0.55) continue;
        placements.push({ def, u, corner: false });
      }
      if (def.margin > 0) {
        placements.push({ def, u: -def.width / 2 + pilasterSpec.cornerW.v / 2, corner: true });
        placements.push({ def, u: def.width / 2 - pilasterSpec.cornerW.v / 2, corner: true });
      }
    }
    const std = placements.filter((p) => !p.corner);
    const cor = placements.filter((p) => p.corner);
    const build = (geo: THREE.BufferGeometry, list: typeof placements, name: string) => {
      const inst = new THREE.InstancedMesh(geo, lib.plaster, list.length);
      inst.name = name;
      inst.castShadow = true;
      inst.receiveShadow = true;
      const m = new THREE.Matrix4();
      const pos = new THREE.Vector3();
      list.forEach((p, i) => {
        m.makeRotationY(p.def.angle);
        m.setPosition(toWorld(p.def, p.u, 0, pos));
        inst.setMatrixAt(i, m);
      });
      inst.instanceMatrix.needsUpdate = true;
      inst.computeBoundingBox();
      inst.computeBoundingSphere();
      applied.add(inst);
    };
    build(mk(pilasterSpec.w.v), std, "pilasters");
    build(mk(pilasterSpec.cornerW.v), cor, "pilasters-corner");
  }

  // window template instances: 4 draws for every window on the building
  {
    const l1 = buildWindowGeometry(windowSpec.l1OpeningH.v);
    const l2 = buildWindowGeometry(windowSpec.l2OpeningH.v);
    const lists: Record<"L1" | "L2", THREE.Matrix4[]> = { L1: [], L2: [] };
    const pos = new THREE.Vector3();
    for (const def of FACADES) {
      for (const floor of ["L1", "L2"] as const) {
        const openingH = floor === "L1" ? windowSpec.l1OpeningH.v : windowSpec.l2OpeningH.v;
        const sillY = floor === "L1" ? stations.l1SillY.v : stations.l2SillY.v;
        for (const slot of openingsFor(def.facade, floor)) {
          if (slot.kind !== "window") continue;
          const m = new THREE.Matrix4().makeRotationY(def.angle);
          m.setPosition(toWorld(def, uCenter(def, slot.bay), sillY + openingH / 2, pos));
          lists[floor].push(m.clone());
        }
      }
    }
    const inst = (
      geo: THREE.BufferGeometry,
      mat: THREE.Material,
      ms: THREE.Matrix4[],
      name: string,
      cast: boolean,
    ) => {
      const im = new THREE.InstancedMesh(geo, mat, ms.length);
      im.name = name;
      im.castShadow = cast;
      im.receiveShadow = true;
      ms.forEach((m, i) => im.setMatrixAt(i, m));
      im.instanceMatrix.needsUpdate = true;
      im.computeBoundingBox();
      im.computeBoundingSphere();
      applied.add(im);
    };
    inst(l1.plaster, lib.plaster, lists.L1, "windows-l1", true);
    inst(l1.jali, lib.jaliDark, lists.L1, "jali-l1", false);
    inst(l2.plaster, lib.plaster, lists.L2, "windows-l2", true);
    inst(l2.jali, lib.jaliDark, lists.L2, "jali-l2", false);
  }

  // ---- the door, at the front center bay
  const door = buildDoor(lib);
  const frontDef = FACADES[0];
  const doorSlot = openingsFor("front", "L1").find((s) => s.kind === "door")!;
  const doorU = uCenter(frontDef, doorSlot.bay);
  door.group.position.set(doorU, wallBase, bD / 2);
  group.add(door.group);

  const anchors: Record<string, THREE.Vector3> = {
    "window-ground": (() => {
      const def = FACADES[0];
      const slot = openingsFor("front", "L1").find((s) => s.kind === "window")!;
      return toWorld(def, uCenter(def, slot.bay), stations.l1SillY.v + windowSpec.l1OpeningH.v / 2);
    })(),
  };
  for (const [k, v] of Object.entries(door.anchors)) {
    anchors[k] = v.clone().add(door.group.position);
  }
  return { group, anchors };
}
