/** The stage: CSS backdrop + transparent canvas + engine boot.
 * StrictMode-safe: boot is async with a cancelled flag; dispose is
 * idempotent. In shot mode the full readiness pipeline runs (model,
 * instant camera, warm-up, shadow scrub, fonts) before the done payload
 * is published for the harness.
 */
import { useEffect, useRef, useState } from "react";
import * as THREE from "three/webgpu";
import { createEngine, type Engine } from "../engine/createEngine";
import { parseGlb } from "../engine/loadGlb";
import { resolveItem } from "../data/stageItems";
import { shotMode } from "../qa/shotMode";
import { DEFAULT_VIEW } from "../qa/views";
import { publishShotPending, publishShotDone, shotKey } from "../qa/readiness";
import { measureModel } from "../qa/measures";
import { attachPerfOverlay } from "../qa/perfOverlay";

function toBase64(buf: ArrayBuffer): string {
  const bytes = new Uint8Array(buf);
  let out = "";
  const CHUNK = 0x8000;
  for (let i = 0; i < bytes.length; i += CHUNK) {
    out += String.fromCharCode(...bytes.subarray(i, i + CHUNK));
  }
  return btoa(out);
}

function countScene(root: THREE.Object3D) {
  let meshes = 0;
  let instancedMeshes = 0;
  let instances = 0;
  root.traverse((obj) => {
    const im = obj as THREE.InstancedMesh;
    if (im.isInstancedMesh) {
      instancedMeshes++;
      instances += im.count;
    } else if ((obj as THREE.Mesh).isMesh) {
      meshes++;
    }
  });
  return { meshes, instancedMeshes, instances };
}

const boxToArrays = (b: THREE.Box3) => ({
  min: [b.min.x, b.min.y, b.min.z],
  max: [b.max.x, b.max.y, b.max.z],
});

export default function Stage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [contextLost, setContextLost] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    let cancelled = false;
    let engine: Engine | null = null;
    const entry = resolveItem(shotMode.item ?? "");
    const view = shotMode.view ?? DEFAULT_VIEW;
    const key = shotKey(entry.id, view);
    if (shotMode.shot) publishShotPending(key);

    (async () => {
      const e = await createEngine({
        container,
        canvas,
        interactive: !shotMode.shot,
        forceDpr: shotMode.shot ? 1 : undefined,
        onContextLost: () => setContextLost(true),
      });
      if (cancelled) {
        e.dispose();
        return;
      }
      engine = e;

      const model = entry.build();
      const item = e.setModel(model);
      e.applyView(view, shotMode.shot);
      if (shotMode.wireframe || shotMode.xray) {
        e.setLayers({ wireframe: shotMode.wireframe, xray: shotMode.xray });
      }
      if (shotMode.perf) attachPerfOverlay(e);

      if (!shotMode.shot) {
        void e.warmupAndSettle();
        return;
      }

      window.__mandirExportGlb = async () => toBase64(await e.exportCurrentGlb());
      window.__mandirRoundtrip = async () => {
        const buf = await e.exportCurrentGlb();
        const reimported = await parseGlb(buf);
        const item2 = e.setModel({ group: reimported });
        e.applyView(view, true);
        await e.warmupAndSettle(2);
        return JSON.stringify({ bytes: buf.byteLength, realBounds: boxToArrays(item2.realBounds) });
      };
      await e.warmupAndSettle(2);
      await document.fonts.ready;
      if (cancelled) return;
      const stats = e.stats();
      publishShotDone({
        key,
        item: entry.id,
        view,
        renderer: e.rendererString,
        measures: measureModel(item.real, model.anchors),
        stageBounds: boxToArrays(item.stageBounds),
        realBounds: boxToArrays(item.realBounds),
        ...countScene(item.root),
        drawCalls: stats.drawCalls,
        triangles: stats.triangles,
        shadowGen: stats.shadowGen,
        frame: stats.frame,
      });
    })().catch((err) => {
      console.error("engine boot failed:", err);
    });

    return () => {
      cancelled = true;
      engine?.dispose();
      engine = null;
    };
  }, []);

  return (
    <div ref={containerRef} className="stage-backdrop">
      {contextLost ? (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-center">
          <div className="font-deva text-2xl text-bhasma">ऋतम्भरेश्वर मंदिर</div>
          <div className="font-body text-sm text-bhasma-deep">
            The 3D view lost its graphics context. Reload the page to restore it.
          </div>
        </div>
      ) : (
        <canvas ref={canvasRef} className="stage-canvas" />
      )}
    </div>
  );
}
