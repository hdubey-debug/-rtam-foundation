/** THE MOTIF ALLOWLIST — what may appear on the exterior (design law 4:
 * ONE boss family + precise moldings; everything else is reserved).
 * Every reflect-fix review checks shots against this list; anything
 * outside it is a canon violation even if temple_v3.jpeg shows it (the
 * render carries AI ornament noise the canon has already killed).
 */

export const allowedMotifs = [
  // the one ornament family
  "boss-beam-90-180",
  "boss-kantha-60-120",
  "boss-cornice-50-110",
  // precise moldings
  "molding-upana",
  "molding-jagati",
  "molding-kumuda-smooth-torus",
  "molding-kantha-recess",
  "molding-kapota-drip",
  "molding-corona",
  "molding-stepped-fascia",
  "molding-shadow-groove",
  // the locked window template (jali = separate study; placeholder is a
  // NEUTRAL non-counted orthogonal grille — the reserved "screen" is the
  // pierced chakra motif, which never appears)
  "window-head-cap-drip",
  "window-dentil-blocks",
  "window-architrave-step",
  "window-frame-band-140",
  "window-jali-placeholder-neutral",
  "window-sill-corbels",
  // the locked column stack
  "column-pedestal",
  "column-two-step-base",
  "column-recessed-panel-shaft",
  "column-neck-band",
  "column-bracket-three-course",
  // door + approach
  "door-three-stepped-jambs",
  "door-stepped-head",
  "door-bronze-pulls",
  "chandrashila",
  "stair-cheek-walls",
  "stair-ball-finials", // present in the locked render — allowlisted (lead's call)
  // roofs + crown
  "roof-tile-rows",
  "roof-ridge-hip-caps",
  "roof-fascia",
  "tamra-skirt",
  "tower-vertical-ribs",
  "tower-bhumi-bands",
  "vedi-band",
  "amalaka-24-ribs", // the sanctioned 24 (crown count survives v3.3)
  "kalasha",
  "dhvaja",
] as const;

export type Motif = (typeof allowedMotifs)[number];

/** RESERVED — never on the exterior until their studies conclude. */
export const forbiddenMotifs = [
  "petal", // all lotus profiles wait for the murti's 3D lotus
  "sun-disc", // the twelve-sun door band is DEFERRED (v3.3)
  "drop-pendant",
  "pierced-chakra-screen", // the one reserved screen
  "icon-wallpaper", // any count riding a repeating element (law 3)
  "allover-wall-relief", // temple_v3's AI surface noise — walls stay plain plaster
] as const;

export function isAllowed(motif: string): boolean {
  return (allowedMotifs as readonly string[]).includes(motif);
}
