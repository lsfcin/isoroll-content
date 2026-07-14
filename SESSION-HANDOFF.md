# SESSION HANDOFF — scene-creation program (Fable session ended 2026-07-14, post-freeze execution day 1)
> READ FIRST next session, with SCENE-CREATION.md + design/PAINTER-UX.md (rounds 1–19 + freeze banner) + design/RENDER-RESTYLE-MEMO.md + the approved plan `~/.claude/plans/isoroll-scene-creation-program-cached-graham.md`. NOTHING here is assumed — all in files. When unsure, ASK Lucas.

## What is DONE and SHIPPED (do not redo)
| Piece | Where | Proof |
|---|---|---|
| P0–P4, P6 | per previous handoff (see git history) | shipped pre-freeze |
| P6.5 **GRAMMAR FROZEN 2026-07-13 @ rig v16.2** (19 rounds) | artifact 🧱 `https://claude.ai/code/artifact/fce5e565-f376-4912-8ca7-7c19f6932ad4`; source `design/feel-rig/` (NORMATIVE reference) | Lucas: "painter can be freezed"; PAINTER-UX log |
| D1 DSL v2 Python (parse/serialize/massing/manifest/guide-render) | content `loop/dsl-v2-python` (0a4d990+45a2f97) | pytest 53/53; trail `.loop/dsl-v2-python/` |
| P5.1 kit renderer + arm sheets | content `loop/kit-module-renderer` (b56abc0+189c90c) | pytest 82; sheets+81 masks staged `output/gen-inbox/` (gitignored) |
| D2 DSL v2 TS twin | module `loop/dsl-v2-ts-twin` (aad8dac) | verify:fast 92 green; live twin-diff vs Python 9/9; trail kept |

## THE MODEL (frozen — carry forward)
Per-voxel scene: levels 0–9, one char per VOXEL, substitution-on-write, stack moves with riders. Openings = D/W voxels (per-tool heights). Sloped-surface GROUPS unify roofs (flat/shed1/shed2, 1–5ft, per-side enclosure) + stairs (solid/thin, slopes ONLY 45°=5ft or half=2.5ft — crop-clean into voxels). Floors fh 0–2ft. Derived corner-smoothing per level. Selection priority: slice voxels > stairs > roofs. DSL v2: `level N:` blocks + `layer side:/type:/wmat:/fh:` + `roof:`/`stair:` lines authoritative, R/S voxels derived/validated.

## IN FLIGHT / NEXT
1. **P7a painter-mvp-1 (module) at Loop 4b** — Loops 0–4a done (`.loop/painter-mvp-1/`: plan 6 rows, arch PASS w/ pinned risks, 34 red unit tests at model/gestures/reassemble-plan/perf seams). NEXT: spawn loop-medium for 4b (green = 93 baseline + 34 new), then Loop 5 (live-Foundry e2e — executor MAY start server, world isoroll-test), Loop 6 ship (keep-trail, contamination fence). Then ☐ Lucas usability session → P7b clarify (groups/opacity/group-ops).
2. **☐ Lucas: NB web runs** — 3 arm sheets in `output/gen-inbox/` + prompts `src/pipeline/prompts/restyle_arm_{b,bc,a}.md` → results to `output/gen-outbox/` → fire P5.4 QC loop (decision rule pre-registered in RENDER-RESTYLE-MEMO; baseline A0 = Lucas's existing NB-from-guide sheet).
3. **☐ Lucas merge eyeball queue** (gitflow, nothing merged): content `loop/dsl-v2-python` → `loop/kit-module-renderer`; module `loop/dsl-v2-ts-twin`.
4. P8 (multiview cardinal) after P5 verdict + P7; P9 last. Loop specs land in ROADMAPs then.

## Orchestration field notes (this execution model works — reuse)
- Loops ran as background `loop-low/medium/high` agents; orchestrator holds verdicts only. 3 loops shipped ≈1.4M subagent tokens, zero max-tier spawns (max-tier work done inline by orchestrator: Loop 0s, one RETURN-loop=3 ruling).
- **Base-branch trap**: content `develop` has NO design/ tree — always base content loops on the doc-branch lineage (correction pattern: append-only "Plan Correction (orchestrator)" section).
- **Module tree contamination**: uncommitted floor-fog-spike dirt in module tree — loops fence it (never touch/commit those paths; pattern in `.loop/dsl-v2-ts-twin/6-ship.md`). T8 facade leftover folded into P7a.
- **RETURN loop=3 handling**: Loop 5 integration-gap → orchestrator rules inline at max tier (design held, seams sharpened, 4a/4b re-entry at medium). Worked perfectly — groups gap caught by e2e, closed same day.
- **Executor death (session limit)**: resume = fresh executor reads 4a + partial 4b, reruns test-cmd for true state, continues append-only. Cheap (~90s).

## Environment facts
- Foundry v14: `node /home/lucas/FoundryVTT/resources/app/main.js --dataPath=/home/lucas/foundrydata-v14`; world isoroll-test; check `curl localhost:30000`.
- Gemini API key: image models limit:0 — web app ONLY (route decided).
- Loop executors: `core/flows/loop-engineering.md`; opencode banned in repo code.
- 200-LOC hook: .frag exempt (INBOX→VERIFY routed: scope exemption by path design/**).

## How to work with Lucas (unchanged + new)
Fast structural rounds; design-first; surface conflicts + propose elegant resolution (he accepts big refactors happily — v15 per-voxel + v16 group unification were HIS pushes); one-shot round quality; answers clarifying questions gladly; unify/reuse over new concepts ("make it simpler, interface AND code"). New: he watches session limits — prefer handoff at loop-file seams over starting big executor runs late.
