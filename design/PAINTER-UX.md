# Painter UX — P6.5 interaction design
> Living doc for the "feels like magic" requirement. Prototype-first: iterate here + in the feel rig BEFORE any Foundry painter code (P7 implements what this doc approves).

## Feel rig (clickable prototype)

**Play it: https://claude.ai/code/artifact/fce5e565-f376-4912-8ca7-7c19f6932ad4** (🧱, private artifact)

- Paints directly on the **isometric view** (inverse dimetric projection hit-testing) — and on TOP view; uses the REAL gray kit sprites + the same projection (`Cam.pt` twin), painter order (`scene_assemble` twin), and rotation-as-cell-remapping as the pipeline.
- Exports **real layout DSL** live — what you paint is literally `src/pipeline/layouts/*.txt` input. Copy button → run it through guide/assembly/manifest.
- Source: session scratchpad `feel-rig/` (rig.frag + build.py injects kit base64; kept out of repo — the 200-line hook gate is for product code, the rig is a design artifact hosted on the Artifact URL). Regenerable on request; update = republish same URL.

## Interaction grammar (v1 — validate in the rig)

| Interaction | Behavior | Why it feels like magic |
|---|---|---|
| Paint wall/floor (drag) | continuous strokes; runs merge by construction (massing) | no tile-picking — one tool per intent |
| Paint door/window | ONLY accepted on wall cells; axis (door_u/door_v) auto from wall-run direction, horizontal wins ties | tool refuses nonsense + orients itself; user never chooses a variant |
| Paint on non-wall with door tool | gentle hint "doors live on walls" (no error modal) | teaches the grammar in-flow |
| Rotate Q/E | true rotation (cell remap, NEVER mirror — chirality) | room "turns" in your head; hinges stay on the same side |
| TOP view (T) | orthographic plan, same paint tools | the 9th view is also an editor |
| Erase | dedicated tool + right-click anywhere | redundancy: keyboard/mouse/HUD all reach every action |
| Undo ⌃Z | full stroke granularity | fearless experimentation |
| HUD counts | walls/doors/windows/floor live | the mechanics registration made visible |

Input redundancy matrix: every action reachable by (a) tool rail click, (b) keyboard (1-5, X, Q/E, T, ⌃Z), (c) mouse gesture where natural (RMB erase). This triple-redundancy is a P7 acceptance criterion.

## Open feel-questions (Lucas iterates in the rig, answers land here)

1. Iso-paint vs TOP-paint — which is the primary editing surface in practice?
2. Rotation: instant vs short tween (~150ms)? (Tiny Glade tweens; instant may read as "teleport".)
3. Per-stroke instant re-render: enough, or do pieces want a settle/pop micro-animation?
4. First missing affordance: flood-fill floor / rectangle wall drag / shift-straight-line?
5. Stairs: rig renders procedural steps (no kit piece yet) — good enough placeholder for P7 or does S need kit art earlier?

## Decisions log

- 2026-07-10 — rig v1 published; grammar table above is the P7 baseline pending Lucas feel-session (☐ checkpoint).
- 2026-07-10 — **Lucas round 1 feedback → rig v2** (same URL):
  1. Foundry integration trust — noted; rig validates grammar only, P7 implements it as an isoroll canvas layer over the same contract.
  2. Camera control missing → ADDED: wheel zoom at cursor, MMB/Space pan, C reset. **P7 requirement: painter must never fight Foundry's own pan/zoom — reuse canvas navigation, add nothing.**
  3. Camera auto-moved on edit → FIXED: camera is user-owned; fit only on load/rotate/top/reset. **P7 rule: no camera moves on edit operations, ever.**
  4. Couldn't paint top of scene → FIXED: full-board faint diamond grid = paintable-area affordance. **P7 rule: editable extent always visible in paint mode.**
  5. Door/window unreadable in gray kit → MITIGATED: amber/cyan cell badges (editor overlay, not art). Art-level legibility = P5 painted-kit question + a "paint-mode overlays" toggle in P7.
  6. Stairs wrong shape + no orientation → FIXED: true massing wedge (4 rising slices, `_stair_boxes` twin) + directional glyphs `^>v<` (real DSL vocabulary, arrows follow view rotation); paint-again spins, R rotates hovered. **Grammar addition: re-applying a directional tool on its own cell rotates it.**
- 2026-07-10 — **Lucas rounds 2–4 → rig v3** (same URL):
  1. Magenta → cyan: kit linework remapped at load. Display-only; pipeline key-out stays magenta for now — flipping the pipeline convention would collide with cyan registration marks, needs its own decision.
  2. **Drag gestures**: wall/roof drag = straight LINE (dominant axis); floor/erase drag = RECTANGLE; ghost preview, commit on release, one undo per stroke. P7 baseline gesture set.
  3. **Openings have a SIDE**: nearest wall face under cursor (live edge highlight), re-click moves it, side rotates with view. CONTRACT GAP: layout DSL has no side field (manifest `WallDef.dir` can carry it) → queued: DSL extension `sides:` directive + massing/export wiring.
  4. **Configurable height + elevation** (UX-skill rationale: brush defaults live with the tool, property edits happen ON the object, wheel+modifier = level-editor convention): wall brush height stepper on rail; Alt+wheel over wall/stair/roof = height/rise in place; Shift+Alt+wheel = base elevation → holes/floating segments, dashed footprint marks gaps. CONTRACT GAP: DSL `wall_h` is global — queued: per-cell h/z overrides.
  5. **Stairs rise configurable** (default 1 cube) — massing already parameterizes `STAIR_RISE`; per-cell rise joins the same DSL extension.
  6. **ROOFS** (Lucas: strongly wanted, cheap on current base — CONFIRMED): tool 6; procedural gable prism; **ridge axis auto from the roof run** (same contextual rule as door axis); base defaults to wall-top z=3; Alt+wheel ridge height, Shift+Alt base. Pipeline path: roof kit pieces = 2 new NB pieces (`roof_u`/`roof_v` + gable ends) reusing the wall-piece process; runtime path: roofs = overhead tiles fading via existing occluder when tokens go inside. CONTRACT GAP: `R` char + roof dims → same DSL extension batch.

**Queued contract extension (one loop, after P3/P4 ship): DSL v2** — `sides:`/`dims:` directives (or per-cell attribute block) carrying opening side, per-cell h/z, stair rise, roof cells; massing consumes; manifest export maps side→`WallDef.dir`, h/z→`boundHeight`/elevation. Feel-rig already produces the data; parser twin lands in both Python and the module's TS layout parser.
