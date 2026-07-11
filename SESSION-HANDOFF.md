# SESSION HANDOFF — scene-creation program (Fable session ended 2026-07-11 at ~17% context)
> READ FIRST in the next Fable session, together with SCENE-CREATION.md + design/PAINTER-UX.md (full decisions log, rounds 1–15) + design/DSL-V2-MEMO.md. NOTHING here is assumed — it is all in files. When unsure, ASK Lucas; never assume, never redo shipped work.

## What is DONE and SHIPPED (do not redo)
| Piece | Where | Proof |
|---|---|---|
| P0 consolidation + P1 `/iso-visual` skill | this repo + core/skills | committed |
| P2 seam BOTH sides | `feature/export-manifest` (content) + `feature/module-walls-import` (module) | gray l-room imports into live Foundry, walls block movement, verify:full green |
| P3 scale-consistency | `feature/scale-consistency` | 33 tests, bidirectional QC, byte-identical legacy |
| P4 TS assembler | `feature/ts-assembler` (module) | 59 tests, 4-view golden ≤1% vs Python, novel-fixture oracle 7/7 |
| P6 floor spike + DECISION | `.loop/floor-fog-spike` (module) | **floor = iso-tiles** (Lucas decided; fog-correct, oracle-verified) |
| P6.5 feel-rig v13 | Artifact `https://claude.ai/code/artifact/fce5e565-f376-4912-8ca7-7c19f6932ad4` (🧱) | 15 design rounds with Lucas; source PRESERVED at `design/feel-rig/` (rig.frag + build.py + kit_b64.txt); to update: `python3 design/feel-rig/build.py` then Artifact tool with `url:` param = the URL above |

Loop-engineering `[pilot]` is DONE (multiple real loops shipped; routing audits in `.loop/*/`; keep-trail everywhere).

## THE MODEL (crystallized through the rounds — this is the core insight to carry)
**Scene ground truth = VOXEL GRID (Minecraft-underneath).** Layers 0–9, each an independent map (multi-story). Tools are brushes writing voxels; kit sprites are voxel skins. Editing slice = single source of truth (place/hover/erase at slice). Per-voxel opacity (opaque window + fade). Rotation = remapping, NEVER mirroring (chirality). Openings have sides, pierce through, merge when adjacent. Diagonals derived from wall corners (cross-cell rule). Roofs = group objects (form flat/shed1/shed2, dir, slope 1–5ft, per-side enclosure none/edge/inset w/ corner self-fill, eaves) occupying voxels (R in level grids; params as `roof:` lines). Full grammar + all decisions: `design/PAINTER-UX.md`.

## IN FLIGHT / NEXT
1. **☐ Lucas may still send rig rounds** — iterate `design/feel-rig/rig.frag`, rebuild, republish SAME artifact URL. When a session passes without structural change → **grammar freeze** → start P7.
2. **P5 image generation — STRATEGY UPDATE NEEDED (Lucas agrees)**: API key has `limit: 0` for image models (no free tier; web app works). First NB kit-sheet result exists (Lucas ran web app — ask him to save it as `output/gen-outbox/kit-dimetric-sheet.png` if not there). Learnings from it: (a) NB replicated door side ignoring rotation — door_u/door_v need stronger differentiation or per-piece calls; (b) NB watermark sits in the BOTTOM-RIGHT cell — redesign sheets to keep that cell empty/caption (verify exact watermark placement online); (c) **KIT V2 = VOXEL MODULES**: the painter renders walls as base + 1-voxel bands + top cap — art should be generated in exactly those modules (band, cap, base, per-side recess bands, diag half-band, roof cells), not 3-tall monoliths. Staging script preserved: `design/feel-rig/stage_kit_paint.py`.
3. **DSL v2 loop** (after freeze): multi-level grids + attr layers + roof lines + sides/types — memo `design/DSL-V2-MEMO.md` + the rig's live export is the reference; parser lands in Python + TS twins.
4. **P7 painter MVP** (module): implements the frozen grammar over the shipped assembler/import; floor = iso-tiles w/ perf gate.
5. **P8 multiview 8+1, P9 polish** per SCENE-CREATION.md program.

## Environment facts
- Foundry v14 server: `node /home/lucas/FoundryVTT/resources/app/main.js --dataPath=/home/lucas/foundrydata-v14` (may still be running, check `curl localhost:30000`); world `isoroll-test` active.
- Gemini key at `~/.gemini_key` (0600; exported in ~/.bashrc as GEMINI_API_KEY; **no image quota — don't retry API image gen without billing/OpenRouter decision**). Lucas was advised to rotate the key later (it touched chat).
- Git: everything on stacked feature branches, NOTHING merged to develop (gitflow: Lucas eyeballs merges). Content stack: scene-creation-consolidation → export-manifest → scale-consistency (docs kept landing on its tip). Module: module-walls-import → ts-assembler → floor-fog-spike (+ `refactor/phase-6-cleanup` holds a preserved WIP commit `0c5473d` that predates this program — Lucas's call).
- Loop executors: spawn `loop-low/medium/high` per `core/flows/loop-engineering.md`; opencode banned in repo code.
- 200-line hook gate on code files; `.frag`/`.txt` exempt (that's why the rig source is a .frag).

## How to work with Lucas on this (learned this session)
Fast structural rounds on the rig (he tests within minutes — publish same artifact URL every time); design-first, never implementation-ease-first; when his idea conflicts with something existing, surface the conflict and propose the elegant resolution (he accepts big refactors happily — layers, voxel semantics); one-shot quality expected: think the whole round through before editing; he answers clarifying questions gladly (the eaves question).
