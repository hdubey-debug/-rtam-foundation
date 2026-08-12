/** THE DATUM TABLES — dimensions.ts
 *
 * Datum-based, not a precedence chain: founder feet bind hard at NAMED
 * datums; doc-mm values bind inside their component; render-derived and
 * selected values are soft; everything carries {source, status, tol,
 * provenance}.
 *
 * PARAMETRIC DISCIPLINE (codex DIMS audit): every value is defined ONCE
 * as a constant below and referenced everywhere else — no repeated
 * literals. Change an authority constant and every dependent moves.
 *
 * Founder dimensions (2026-08-11): width 52 ft · depth 88 ft · body
 * (podium+L1+L2) ≈ 30 ft · total 52 ft TO THE KALASHA TIP (dhvaja
 * excluded — founder-confirmed).
 *
 * This model is a PARAMETRIC DESIGN VISUALIZATION — a design study, not
 * for construction. Provisional values await sthapati/engineer review.
 */

export const FT = 0.3048;
export const MM = 0.001;

export type Source =
  | "founder" // the founder's stated feet, at a named datum
  | "doc-mm" // temple-DESIGN-DIRECTIONS.md millimetre spec
  | "locked-du" // du anchor from the plan-mode render analysis
  | "render" // measured off temple_v3.jpeg — soft
  | "derived" // computed from other authorities (real references)
  | "assumed"; // a selected design/interpretation value

export type Status = "locked" | "provisional" | "assumed" | "superseded";

export interface Dim {
  /** meters */
  v: number;
  source: Source;
  status: Status;
  tol?: number;
  provenance: string;
}

const dim = (v: number, source: Source, status: Status, provenance: string, tol?: number): Dim => ({
  v,
  source,
  status,
  provenance,
  ...(tol !== undefined ? { tol } : {}),
});

// ===========================================================================
// THE AUTHORITY CONSTANTS — single source; everything below references these
// ===========================================================================

// founder numbers (locked numerically; their BINDINGS are assumptions
// recorded separately below)
const PODIUM_W = 52 * FT; // 15.8496
const PODIUM_D = 88 * FT; // 26.8224
const PLATE_Y = 30 * FT; // 9.144
const TIP_Y = 52 * FT; // 15.8496

// doc-mm (locked)
const COURSE_UPANA = 150 * MM;
const COURSE_JAGATI = 300 * MM;
const COURSE_KUMUDA = 150 * MM;
const COURSE_KANTHA = 150 * MM;
const COURSE_KAPOTA = 150 * MM;
const PODIUM_H = COURSE_UPANA + COURSE_JAGATI + COURSE_KUMUDA + COURSE_KANTHA + COURSE_KAPOTA;
const DOOR_W = 1.8;
const DOOR_H = 3.4;
const WINDOW_BAND = 140 * MM;

// du anchors (provisional interpretations that survived the F2 arithmetic)
const FACADE_TOTAL_DU = 776;
const FACADE_M_PER_DU = PODIUM_W / FACADE_TOTAL_DU; // Reading B: 776 du = podium width
const BAY_DU = 112;
const BAY_W = BAY_DU * FACADE_M_PER_DU; // 2.287571
const WINDOW_M_PER_DU = 8.75 * MM; // candidate scale: 16 du → 140 mm band
const WINDOW_OPENING_DU = 156;

// selected design values (assumed; codex DIMS vertical solve adopted)
const WALK = 1.2;
const EAVE_OVERHANG = 0.6;
const WALL_T = 0.3;
const SIDE_BAYS = 10; // the ten-bay closure
const L1_SILL_ABOVE_TERRACE = 0.75;
const BAND_BOTTOM_Y = 5.05;
const BAND_T = 0.4; // band thickness — selected, NOT part of the blind solve
const L2_FFL_Y = 5.4;
const L2_SILL_ABOVE_FFL = 0.7;
const ROOF_RISE = 1.4;
const SPRING_OVER_RIDGE = 0.106; // visible spring just above the ridge
const AMALAKA_TOP_Y = 14.65; // the kalasha bearing plane
const DHVAJA_TOP_Y = 17.2;
const L1_OPENING_H = 2.0;
const L2_OPENING_H = 1.7;
// head/sill extras are DERIVED from the template parts further down —
// stale hand-copies failed the GEO audit (actual 0.375/0.350 vs 0.34/0.28)
const CORNICE_ZONE = 0.5; // reserved wall zone under the plate
/** door trim above the clear opening: three head bands + head cap.
 * The porch SOFFIT DERIVES from the trim (GEO audit: the trim once
 * reached within 28 mm of the verandah roof) */
const DOOR_TRIM_ABOVE = 3 * 0.11 + 0.1;
const DOOR_TRIM_CLEAR = 0.05;

// derived chain (real dependency expressions — the parametric graph)
const STRUCTURAL_W = PODIUM_W - 2 * WALK;
const BODY_D = SIDE_BAYS * BAY_W;
const PORCH_PROJECTION = PODIUM_D - 2 * WALK - BODY_D;
const PORCH_W = 5 * BAY_W;
const L1_SILL_Y = PODIUM_H + L1_SILL_ABOVE_TERRACE;
const BAND_TOP_Y = BAND_BOTTOM_Y + BAND_T;
const L2_SILL_Y = L2_FFL_Y + L2_SILL_ABOVE_FFL;
const RIDGE_Y = PLATE_Y + ROOF_RISE;
const SPRING_Y = RIDGE_Y + SPRING_OVER_RIDGE;
const KALASHA_H = TIP_Y - AMALAKA_TOP_Y;
const DOOR_HEAD_Y = PODIUM_H + DOOR_H;
const DOOR_TRIM_TOP_Y = DOOR_HEAD_Y + DOOR_TRIM_ABOVE;
const SOFFIT_Y = DOOR_TRIM_TOP_Y + DOOR_TRIM_CLEAR;
const WINDOW_OPENING_W = WINDOW_OPENING_DU * WINDOW_M_PER_DU;

// ===========================================================================
// BINDINGS — where the founder numbers attach (assumptions, recorded)
// ===========================================================================
export const bindings = {
  /** 52 × 88 ft binds to the OUTSIDE FINISHED PODIUM ENVELOPE — the widest
   * extent over ALL five courses. Course plan offsets at M3 are INWARD
   * from this envelope (kapota/upana may project relative to jagatī but
   * never beyond it). */
  podiumFootprintDatum: "outside-finished-envelope" as const,
  /** "body ≈ 30 ft" binds ground → main-eave WALL PLATE (approx in the
   * founder's words; exact-by-construction in the model) */
  bodyDatum: "ground-to-wall-plate" as const,
  /** ground = podium underside at finished grade (interpretation) */
  lowerDatum: "podium-underside-at-grade" as const,
  /** the five-bay front reads as five full WIDTHS, door bay centered */
  fiveBayReading: "five-widths" as const,
  /** door/window dims are CLEAR openings; framed adds bands/jambs */
  openingDimConvention: "clear-opening" as const,
};

// ===========================================================================
// PODIUM
// ===========================================================================
export const podiumCourses = {
  upana: dim(COURSE_UPANA, "doc-mm", "locked", "design doc §2.2: upāna ~150 rough foot"),
  jagati: dim(COURSE_JAGATI, "doc-mm", "locked", "design doc §2.2: jagatī ~300 plain"),
  kumuda: dim(COURSE_KUMUDA, "doc-mm", "locked", "design doc §2.2: kumuda ~150 smooth torus"),
  kantha: dim(COURSE_KANTHA, "doc-mm", "locked", "design doc §2.2: kaṇṭha ~150 pearl course"),
  kapota: dim(COURSE_KAPOTA, "doc-mm", "locked", "design doc §2.2: kapota ~150 cap + drip"),
} as const;

export const podiumHeight = dim(PODIUM_H, "derived", "locked", "sum of the five doc courses; asserted = 0.900");

/** Plan offsets per course, INWARD (negative) from the outside finished
 * envelope — the binding rule: no course ever projects beyond 52 × 88.
 * upāna is the widest (dx 0); everything else recesses. Render-scaled
 * selections, refined at the podium build; the boss course lives in the
 * kaṇṭha recess (M6). */
export const podiumProfile = {
  jagatiInset: dim(0.05, "assumed", "provisional", "jagatī face inset — the one step above the upāna foot"),
  kumudaApexInset: dim(0.005, "assumed", "provisional", "torus apex nearly flush — 5 mm inside the envelope"),
  kanthaRecess: dim(0.09, "assumed", "provisional", "kaṇṭha recess depth — hosts the Ø60 boss course"),
  kapotaFaceInset: dim(0.02, "assumed", "provisional", "kapota face — 20 mm inside the envelope"),
  kapotaTopInset: dim(0.06, "assumed", "provisional", "kapota top chamfer back to the terrace"),
  /** the REAL drip: a groove in the kapota underside behind a lip — water
   * cannot track past it (codex GEO: a fascia edge alone is cosmetic) */
  dripLipW: dim(0.012, "assumed", "provisional", "drip lip width at the kapota face"),
  dripGrooveW: dim(0.015, "assumed", "provisional", "drip groove width"),
  dripGrooveDepth: dim(0.014, "assumed", "provisional", "drip groove depth up into the soffit"),
  arcSamples: 10, // kumuda torus smoothness
} as const;

// ===========================================================================
// ENVELOPES
// ===========================================================================
export const envelopes = {
  podiumW: dim(PODIUM_W, "founder", "locked", "52 ft — number locked; BINDING per bindings.podiumFootprintDatum"),
  podiumD: dim(PODIUM_D, "founder", "locked", "88 ft — number locked; BINDING per bindings.podiumFootprintDatum"),
  walk: dim(WALK, "assumed", "provisional", "1.2 m wall-face inset (codex DIMS); outside-drip strip is only walk − overhang"),
  structuralW: dim(STRUCTURAL_W, "derived", "provisional", "podiumW − 2·walk"),
  eaveOverhang: dim(EAVE_OVERHANG, "assumed", "provisional", "selected 0.6 m — keeps the drip walk − overhang inside the edge"),
  wallThickness: dim(WALL_T, "assumed", "provisional", "300 mm brick+RC+plaster modeling assumption"),
} as const;

export const bodyDepth = dim(BODY_D, "derived", "provisional", "SIDE_BAYS × bay — the ten-bay closure (codex DIMS)");
export const porchProjection = dim(
  PORCH_PROJECTION,
  "derived",
  "provisional",
  "podiumD − 2·walk − bodyDepth — the depth residual IS the porch",
);

/** reported, PARTLY asserted: width + depth margins are checked against
 * the podium envelope; exact placement checks live in qa/measures.ts */
export const eaveEnvelope = {
  w: STRUCTURAL_W + 2 * EAVE_OVERHANG,
  d: BODY_D + 2 * EAVE_OVERHANG,
};

// ===========================================================================
// FACADE GRID
// ===========================================================================
export const facadeGrid = {
  totalDu: FACADE_TOTAL_DU,
  mPerDu: dim(FACADE_M_PER_DU, "locked-du", "provisional", "Reading B: 776 du = podiumW → 20.4247 mm/du"),
  bayDu: BAY_DU,
  bayW: dim(BAY_W, "derived", "provisional", "BAY_DU × facade scale"),
  sideBays: SIDE_BAYS,
} as const;

// ===========================================================================
// VERTICAL STATIONS (y-datums, ground = 0)
// ===========================================================================
export const stations = {
  groundY: dim(0, "assumed", "provisional", "lower datum: podium underside at finished grade — interpretation"),
  podiumTopY: dim(PODIUM_H, "derived", "locked", "top of kapota = pradakshina terrace"),
  l1SillY: dim(L1_SILL_Y, "derived", "provisional", "terrace + selected 0.75 sill height"),
  beamBandBottomY: dim(BAND_BOTTOM_Y, "assumed", "provisional", "codex DIMS solve — clears the door head by 0.75"),
  beamBandTopY: dim(BAND_TOP_Y, "derived", "provisional", "band bottom + selected 0.40 thickness (NOT from the blind solve)"),
  l2FloorY: dim(L2_FFL_Y, "assumed", "provisional", "L2 FFL — L1 story 4.5, L2 3.744"),
  l2SillY: dim(L2_SILL_Y, "derived", "provisional", "L2 FFL + selected 0.70 sill height"),
  plateY: dim(PLATE_Y, "founder", "assumed", "body ≈30 ft bound ground → wall plate — binding assumed, built exact", 0.005),
  mainRidgeY: dim(RIDGE_Y, "derived", "provisional", "plate + selected 1.40 rise — gentle hip; D4 study parameter"),
  towerSpringY: dim(SPRING_Y, "derived", "provisional", "ridge + selected 0.106; STRUCTURAL spring at the plate is distinct"),
  amalakaTopY: dim(AMALAKA_TOP_Y, "assumed", "provisional", "kalasha bearing plane — codex DIMS crown chain"),
  kalashaTipY: dim(TIP_Y, "founder", "locked", "52 ft TO THE KALASHA TIP — founder-confirmed; dhvaja excluded", 0.001),
  dhvajaTopY: dim(DHVAJA_TOP_Y, "render", "provisional", "flag pole top — REPORTED only, excluded from the 52 ft"),
} as const;

// ===========================================================================
// FACADE CONVENTIONS — the corner rule, DECLARED before the wall build
// (codex DIMS follow-up): two bay systems meet at each front corner.
// ===========================================================================
export const facadeConventions = {
  /** front/rear: five bays CENTERED; the residual (≈1.006 m each side)
   * is a SOLID CORNER PIER, not a bay */
  frontRear: "five-bays-centered-with-corner-piers" as const,
  cornerPierW: dim((STRUCTURAL_W - 5 * BAY_W) / 2, "derived", "provisional", "(structuralW − 5 bays)/2 ≈ 1.006"),
  /** sides: ten bays tile bodyDepth corner-to-corner, ZERO margin —
   * the side window edge sits (bay − frame)/2 ≈ 0.32 from the corner */
  sides: "ten-bays-corner-to-corner" as const,
  /** at the corner, the front pier meets the side bay edge; corner
   * pilasters belong to the FRONT/REAR pier, not the side grid */
  cornerRule: "pier-meets-side-bay-edge" as const,
} as const;

// ===========================================================================
// WINDOW TEMPLATE (doc §2.5 locked AS RENDERED; jali = separate study)
// ===========================================================================
/** template part dimensions (Fig 6 chain), render-scaled provisional.
 * All applied parts stand ≥ 2 mm proud (no CSG, nothing coplanar).
 * SINGLE SOURCE: the extras below and window.ts both read these. */
const WPARTS = {
  bandProud: 0.028, // raised frame band off the wall face
  architraveStep: 0.05, // outer step band width beyond the frame
  architraveProud: 0.014,
  headCapH: 0.11, // projecting head cap + drip lip
  headCapProud: 0.09,
  dentilH: 0.075,
  dentilW: 0.085,
  dentilGap: 0.075,
  dentilProud: 0.055,
  sillH: 0.09, // molded sill slab + drip
  sillProud: 0.08,
  corbelCount: 3, // non-system
  corbelW: 0.14,
  corbelH: 0.12,
  corbelProud: 0.06,
  jaliInset: 0.12, // grille plane back into the reveal
  jaliBarT: 0.03,
  jaliBarsV: 5, // NEUTRAL non-counted grille — never 12 (law 3);
  jaliBarsH: 7, // the reserved "screen" (pierced chakra) never appears
} as const;

export const windowSpec = {
  mPerDu: dim(WINDOW_M_PER_DU, "locked-du", "provisional", "CANDIDATE scale: 16 du band = 140 mm (F2-consistent)"),
  bandM: dim(WINDOW_BAND, "doc-mm", "locked", "design doc: raised frame band ~140"),
  openingW: dim(WINDOW_OPENING_W, "derived", "provisional", "156 du × window scale → 1.365 CLEAR opening"),
  l1OpeningH: dim(L1_OPENING_H, "render", "provisional", "L1 clear opening ≈ 2.0"),
  l2OpeningH: dim(L2_OPENING_H, "render", "provisional", "L2 clear opening ≈ 1.7 — shorter, same template"),
  /** DERIVED from parts: band + architrave + dentils + head cap = 0.375 */
  headExtraH: dim(
    WINDOW_BAND + WPARTS.architraveStep + WPARTS.dentilH + WPARTS.headCapH,
    "derived",
    "provisional",
    "band + architrave + dentil + head cap — GEO audit: never hand-copied",
  ),
  /** DERIVED from parts: band + sill + corbels = 0.350 */
  sillExtraH: dim(
    WINDOW_BAND + WPARTS.sillH + WPARTS.corbelH,
    "derived",
    "provisional",
    "band + sill + corbel — GEO audit: never hand-copied",
  ),
  parts: WPARTS,
} as const;

// ===========================================================================
// MOLDING BANDS (M6): the beam band between floors + the cornice under
// the plate — both wrap the body as closed rings; the boss courses ride
// their faces. Doc: bosses at junctions in registers, never mid-wall.
// ===========================================================================
export const bandSpec = {
  /** beam band: face proud of the wall, hosting the Ø90 course */
  beamProud: dim(0.055, "assumed", "provisional", "beam band face projection"),
  beamStep: dim(0.02, "assumed", "provisional", "top/bottom framing steps of the band"),
  /** the Ø90 register rides the band centerline */
  beamBossCenterY: dim((BAND_BOTTOM_Y + BAND_BOTTOM_Y + BAND_T) / 2, "derived", "provisional", "band centerline 5.25"),
  /** the Ø60 register rides the kaṇṭha course centerline */
  kanthaBossCenterY: dim(
    COURSE_UPANA + COURSE_JAGATI + COURSE_KUMUDA + COURSE_KANTHA / 2,
    "derived",
    "provisional",
    "kaṇṭha centerline 0.675 — derived from the course sums",
  ),
  /** cornice under the plate: stepped fascia + corona + drip zone.
   * Named steps (GEO audit: no literals in the profile builder). */
  corniceBottomY: dim(PLATE_Y - 0.444, "derived", "provisional", "cornice zone begins 0.444 under the plate"),
  corniceFasciaProud: dim(0.06, "assumed", "provisional", "mid fascia carrying the Ø50 course"),
  coronaProud: dim(0.105, "assumed", "provisional", "corona projection with drip"),
  corniceSteps: {
    firstStepProud: 0.03,
    firstStepRise: 0.025,
    grooveTop: 0.12,
    fasciaBottom: 0.145,
    fasciaTop: 0.27,
    coronaBottom: 0.295,
    dripInset: 0.018,
    dripBottom: 0.31,
    dripTop: 0.325,
    plateReturnInset: 0.02,
  },
  /** Ø50 register = mid of the named fascia (single source with the ring) */
  corniceBossCenterY: dim(
    PLATE_Y - 0.444 + (0.145 + 0.27) / 2,
    "derived",
    "provisional",
    "corniceBottom + fascia mid = 8.9075",
  ),
  /** hairline off the wall face — rings never sit coplanar on the wall */
  profileSurfaceOffset: 0.001,
  /** boss run end margins (centered residual per closure rule) */
  bossRunMargin: dim(0.16, "assumed", "provisional", "clear zone at each face end — corners stay quiet"),
} as const;

// ===========================================================================
// PILASTERS + DOOR LEAF DETAIL (wall-applied parts)
// ===========================================================================
export const pilasterSpec = {
  w: dim(0.24, "render", "provisional", "bay-boundary pilaster strip width"),
  proud: dim(0.05, "render", "provisional", "projection off the wall face"),
  cornerW: dim(0.38, "render", "provisional", "corner pilaster on the front/rear piers"),
} as const;

export const doorParts = {
  jambSteps: 3, // doc: three stepped jambs
  jambStepW: 0.11,
  jambStepProud: 0.055, // OUTERMOST proudest, stepping IN toward the leaf
  headStepH: 0.1,
  leafRecess: 0.16, // teak leaf FRONT FACE depth into the reveal
  leafT: 0.07,
  pullR: 0.09, // bronze ring pulls
  pullAtH: 1.15,
} as const;

/** the trim's true top: heads tile UP from the clear opening, cap above */
export const doorTrimTopY = dim(
  DOOR_TRIM_TOP_Y,
  "derived",
  "provisional",
  "terrace + clear H + three head bands + head cap = 4.73; soffit derives above it",
);

// ===========================================================================
// COLUMN (doc §2.3 locked as rendered) — endpoints, never a module
// ===========================================================================
export const columnSpec = {
  baseY: dim(PODIUM_H, "derived", "locked", "pedestal sits on the terrace"),
  soffitY: dim(SOFFIT_Y, "derived", "provisional", "door trim top + 0.05 — the porch clears the full dvāra trim"),
  totalH: dim(SOFFIT_Y - PODIUM_H, "derived", "provisional", "soffitY − baseY; du ratios distribute inside"),
  /** stack ratios (fractions of totalH), render-derived, sum = 1 */
  ratios: { pedestal: 0.14, base: 0.08, shaft: 0.55, neck: 0.05, bracket: 0.18 },
  ratiosProvenance: "render-derived stack proportions — refined against Fig 4 at the column build",
  /** plan widths per stack part (m) — Fig 4 template, render-scaled */
  widths: {
    pedestal: 0.46,
    baseSteps: [0.42, 0.36] as const, // the two-step molded base
    shaft: 0.3,
    neck: 0.34,
    bracketSteps: [0.36, 0.46, 0.56] as const, // three corbelled courses
  },
  /** recessed-panel read: the FRAME stands proud of the shaft face
   * (no CSG; applied parts ≥ 2 mm proud per the geometry rules) */
  panelFrameW: 0.035,
  panelFrameProud: 0.012,
  widthsProvenance: "assumed/render — the doc locks the STACK, widths refined at the study",
} as const;

// ===========================================================================
// VERANDAH
// ===========================================================================
export const verandah = {
  projection: dim(PORCH_PROJECTION, "derived", "provisional", "see porchProjection — depth-closure residual"),
  width: dim(PORCH_W, "derived", "provisional", "5 × bay — five-widths reading (bindings.fiveBayReading)"),
  eaveY: dim(SOFFIT_Y + 0.1, "derived", "provisional", "porch soffit + selected 0.10"),
  ridgeY: dim(SOFFIT_Y + 0.1 + 0.85, "derived", "provisional", "verandah eave + selected 0.85 shallow hip rise"),
} as const;

// ===========================================================================
// MASSING CONSTANTS (consumed by buildTemple — no hard-codes in builders)
// ===========================================================================
export const massing = {
  mainRoofRidgeInsetFactor: 0.42, // × eave width → hip length each end
  verandahRoofSideOverhang: 0.5,
  verandahRoofFrontOverhang: 0.6,
  verandahRoofBackReturn: 0.3, // roof laps into the wall face
  towerRearGap: 1.0, // tower center back from the rear wall face + halfBase
  stairTreadRun: 0.3,
  porchPostSize: 0.34,
  provenance: "massing-stage selections (render-proportioned); refined per component milestone",
} as const;

// ===========================================================================
// BOSS FAMILY (doc §2.4 — the ONE ornament family, three scales)
// ===========================================================================
export const bossFamily = {
  beam: { d: dim(90 * MM, "doc-mm", "locked", "beam course Ø~90"), pitch: dim(180 * MM, "doc-mm", "locked", "@~180") },
  kantha: { d: dim(60 * MM, "doc-mm", "locked", "kaṇṭha course Ø~60"), pitch: dim(120 * MM, "doc-mm", "locked", "@~120") },
  cornice: { d: dim(50 * MM, "doc-mm", "locked", "cornice course Ø~50"), pitch: dim(110 * MM, "doc-mm", "locked", "@~110") },
  riseFactor: 0.42,
  plateFactor: 1.15,
  beamShoulderFactor: 0.55,
  factorsProvenance: "relief proportions — lead's call, recorded in the plan",
  /** pitches never stretch: residual is centered, corners get the special */
  closureRule: "centered-residual" as const,
} as const;

// ===========================================================================
// DOOR (doc §2.5)
// ===========================================================================
export const doorSpec = {
  w: dim(DOOR_W, "doc-mm", "locked", "design doc: door ~1.8 wide (clear)"),
  h: dim(DOOR_H, "doc-mm", "locked", "design doc: door ~3.4 tall (clear)"),
} as const;

// ===========================================================================
// TOWER — three widths distinct; crown chains from the LOCKED tip
// ===========================================================================
export const towerSpec = {
  structuralBaseW: dim(4.2, "render", "provisional", "shaft base inside the building, plan width"),
  roofCurbW: dim(3.4, "render", "provisional", "curb where the shaft penetrates the main roof"),
  visibleSpringW: dim(3.0, "render", "provisional", "visible shaft width at the spring"),
  towerTopW: dim(1.24, "render", "provisional", "loft top width under the amalaka seat"),
  kalashaH: dim(KALASHA_H, "derived", "provisional", "tip − amalakaTop — closes the crown chain"),
  amalakaRx: dim(1.05, "render", "provisional", "amalaka half-width"),
  amalakaRyOverRx: 7.5 / 26,
  amalakaRibs: 24, // the sanctioned 24 — crown counts survive v3.3
  countsProvenance: "amalaka 24 = canon-counted survivor; rx:ry from the murti codex proportions",
} as const;

// ===========================================================================
// STAIR (axial dvāra)
// ===========================================================================
export const stairSpec = {
  riserCount: 9, // count, not meters — render-derived, provisional
  riserCountProvenance: "temple_v3 shows ≈9 risers to the terrace",
  riserH: dim(PODIUM_H / 9, "derived", "provisional", "podium height / riser count"),
  widenPerSideDu: 13,
} as const;

// ===========================================================================
// ASSERTIONS — npm run check:dims
// ===========================================================================
export const assertionsChecked = [
  "podium courses sum exactly 0.900",
  "founder numbers: podiumW=15.8496, podiumD=26.8224, plateY=9.144, tipY=15.8496",
  "stations strictly monotonic (incl. plate < ridge < spring)",
  "L1/L2 FULL window units (opening + head/sill extras) clear their zones",
  "door head clears the beam band and the porch soffit",
  "column endpoints meet; stack ratios sum to 1",
  "width walk-symmetry; depth ten-bay closure; porch width < wall width",
  "eave margins stay inside the podium envelope on BOTH axes",
  "crown chain closes exactly at the tip",
] as const;

export function assertDims(): string[] {
  const errs: string[] = [];
  const close = (a: number, b: number, tol: number) => Math.abs(a - b) <= tol;

  if (!close(PODIUM_H, 0.9, 1e-9)) errs.push(`podium courses sum ${PODIUM_H} ≠ 0.900`);

  // founder numbers asserted INDEPENDENTLY of the derivation chain
  if (!close(envelopes.podiumW.v, 15.8496, 1e-9)) errs.push("podiumW ≠ 15.8496");
  if (!close(envelopes.podiumD.v, 26.8224, 1e-9)) errs.push("podiumD ≠ 26.8224");
  if (!close(stations.plateY.v, 9.144, 1e-9)) errs.push("plateY ≠ 9.144");
  if (!close(stations.kalashaTipY.v, 15.8496, 1e-9)) errs.push("kalashaTipY ≠ 15.8496");

  const chain: [string, number][] = [
    ["groundY", stations.groundY.v],
    ["podiumTopY", stations.podiumTopY.v],
    ["l1SillY", stations.l1SillY.v],
    ["beamBandBottomY", stations.beamBandBottomY.v],
    ["l2FloorY", stations.l2FloorY.v],
    ["beamBandTopY", stations.beamBandTopY.v],
    ["l2SillY", stations.l2SillY.v],
    ["plateY", stations.plateY.v],
    ["mainRidgeY", stations.mainRidgeY.v],
    ["towerSpringY", stations.towerSpringY.v],
    ["amalakaTopY", stations.amalakaTopY.v],
    ["kalashaTipY", stations.kalashaTipY.v],
    ["dhvajaTopY", stations.dhvajaTopY.v],
  ];
  for (let i = 1; i < chain.length; i++) {
    if (chain[i][1] <= chain[i - 1][1]) {
      errs.push(`stations not monotonic: ${chain[i][0]} (${chain[i][1]}) ≤ ${chain[i - 1][0]} (${chain[i - 1][1]})`);
    }
  }

  // FULL window units clear their zones — extras are the DERIVED values
  // from the template parts (never hand-copied; GEO audit)
  const headExtra = windowSpec.headExtraH.v;
  const sillExtra = windowSpec.sillExtraH.v;
  const l1UnitTop = L1_SILL_Y + L1_OPENING_H + headExtra;
  const l1UnitBottom = L1_SILL_Y - sillExtra;
  if (l1UnitTop >= BAND_BOTTOM_Y) errs.push(`L1 unit top ${l1UnitTop.toFixed(3)} hits the beam band ${BAND_BOTTOM_Y}`);
  if (l1UnitBottom <= PODIUM_H) errs.push(`L1 unit bottom ${l1UnitBottom.toFixed(3)} buries into the terrace`);
  const l2UnitTop = L2_SILL_Y + L2_OPENING_H + headExtra;
  const l2UnitBottom = L2_SILL_Y - sillExtra;
  if (l2UnitTop >= PLATE_Y - CORNICE_ZONE) {
    errs.push(`L2 unit top ${l2UnitTop.toFixed(3)} enters the cornice zone ${(PLATE_Y - CORNICE_ZONE).toFixed(3)}`);
  }
  if (l2UnitBottom <= BAND_TOP_Y) errs.push(`L2 unit bottom ${l2UnitBottom.toFixed(3)} hits the beam band top ${BAND_TOP_Y}`);

  if (DOOR_HEAD_Y >= BAND_BOTTOM_Y - 0.3) errs.push(`door head ${DOOR_HEAD_Y.toFixed(3)} crowds the beam band`);
  if (DOOR_HEAD_Y >= SOFFIT_Y) errs.push("door head hits the porch soffit");
  // the FULL dvāra trim (heads + cap) must clear the soffit (GEO audit)
  if (DOOR_TRIM_TOP_Y >= SOFFIT_Y) errs.push(`door trim top ${DOOR_TRIM_TOP_Y.toFixed(3)} hits the soffit ${SOFFIT_Y}`);

  const stackSum = Object.values(columnSpec.ratios).reduce((s, r) => s + r, 0);
  if (!close(stackSum, 1, 1e-6)) errs.push(`column stack ratios sum ${stackSum} ≠ 1`);
  if (!close(columnSpec.baseY.v + columnSpec.totalH.v, columnSpec.soffitY.v, 1e-9)) {
    errs.push("column endpoints do not meet the soffit");
  }

  if (!close(STRUCTURAL_W + 2 * WALK, PODIUM_W, 1e-9)) errs.push("structuralW + 2·walk ≠ podiumW");
  if (!close(2 * WALK + BODY_D + PORCH_PROJECTION, PODIUM_D, 1e-9)) errs.push("depth closure broke");
  if (!close(BODY_D, SIDE_BAYS * BAY_W, 1e-9)) errs.push("bodyDepth ≠ ten bays");
  if (PORCH_W > STRUCTURAL_W) errs.push("porch width exceeds the wall width");

  // eaves stay inside the podium on BOTH axes (margin = walk − overhang)
  if (WALK - EAVE_OVERHANG < 0) errs.push("main eave overshoots the podium edge (walk < overhang)");
  if (eaveEnvelope.w > PODIUM_W) errs.push("eaveEnvelope.w exceeds podiumW");
  if (eaveEnvelope.d > BODY_D + 2 * WALK + PORCH_PROJECTION) errs.push("eaveEnvelope.d exceeds its podium zone");

  if (!close(AMALAKA_TOP_Y + KALASHA_H, TIP_Y, 1e-9)) errs.push("crown chain broke: amalakaTop + kalashaH ≠ tip");

  return errs;
}

/** Everything as plain JSON — the codex advisor's eyes. */
export function dimsReport(): Record<string, unknown> {
  return {
    framing: "parametric design visualization — design study, not for construction",
    founderDatums: {
      podiumEnvelopeFt: [52, 88],
      bodyFtAtPlate: 30,
      totalFtAtKalashaTip: 52,
      dhvajaExcluded: true,
    },
    bindings,
    podiumCourses,
    podiumHeight,
    envelopes,
    bodyDepth,
    porchProjection,
    eaveEnvelope,
    facadeGrid,
    stations,
    windowSpec,
    columnSpec,
    verandah,
    massing,
    bossFamily,
    doorSpec,
    towerSpec,
    stairSpec,
    assertionsChecked,
    assertFailures: assertDims(),
  };
}
