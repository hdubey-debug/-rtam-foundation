# mandir-3d — the temple in 3D

An interactive 3D viewer for the **Rtambhareshvara Mandir**, and the parametric
model behind it. Everything on stage is a **parametric design visualization —
a design study, not for construction**. Locked components follow the measured
specs in `../temple-DESIGN-DIRECTIONS.md`; open components carry `provisional`
status until the sthapati/engineer review.

## Run it

```bash
npm install
npm run fonts      # one-time: subset brand fonts → public/fonts (needs python3 + fontTools)
npm run dev        # local viewer
```

Useful URLs:

- `/?perf=1` — live perf overlay (fps, p95 frame time, draws, tris). Trust it
  only in a real browser; headless numbers are meaningless.
- `/?shot=1&item=fixture&view=hero` — deterministic shot mode (QA).

## QA

```bash
npm run shoot -- --views front,hero,side,rear,top --tag M0 --export
npm run test       # geometry tests (vitest)
```

Headless shots run on SwiftShader — a geometry/regression oracle only.
Beauty and performance calls happen in a real browser.

## The two tracks

- **Track B (this repo's model)**: `src/geometry/` generates the temple from
  the measured dimension tables — regenerates when a number changes, exports
  to GLB (real meters) for Blender.
- **Track A (placeholder, founder's task)**: an AI-generated GLB of
  `../temple_v3.jpeg` so the viewer also shows the render-faithful massing.

### Track A — how to generate it (founder)

1. Go to the Tripo studio (tripo3d.ai), sign in (free tier is fine for a
   local placeholder).
2. Upload `temple_v3.jpeg` (repo root) → *Image to 3D*. Prefer the highest
   quality setting offered; textured output.
3. Download the result as **GLB** and drop it at
   `mandir-3d/public/models/temple-tripo.glb`.
4. Tell Claude it's there — it gets optimized (Draco + WebP), registered with
   license provenance, and slotted into the viewer.

**License note:** free-tier Tripo output is licensed NON-COMMERCIAL. The GLB
therefore stays local (gitignored) with its provenance recorded, and the
production build refuses to bundle it. Track B replaces it as components
land. (Fallback if Tripo disappoints: Hunyuan3D, Apache-2.0, on a cluster
GPU node.)

## Deploy

Nothing is deployed (founder decision — local only for now). Both paths are
kept build-verified:

- standalone: `npm run build` → `dist/`
- under the website at a subpath: `VITE_BASE=/mandir/ npm run build`

## Layout

- `src/engine/` — stage engine (three r185 `WebGPURenderer` with
  `forceWebGL: true` — a deliberate WebGL2-always choice; TSL node materials
  are why this renderer class), lighting, ground, camera rig, normalize,
  warm-up, export clone.
- `src/geometry/` — the parametric model (real meters). `fixture.ts` is the
  M0 technical spike, replaced by `buildTemple` from M2.
- `src/qa/` — canonical views, shot mode, readiness protocol, perf overlay.
- `scripts/shoot.mjs` — headless shot harness (generation-scoped done
  protocol, two-stable-captures rule, export smoke test).
- `shots/` — gitignored; approved sets archived per milestone (`--tag M<n>`).
