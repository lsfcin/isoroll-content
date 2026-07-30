# Loop 6 — Ship — dsl-v2-python

## Carry
slug: dsl-v2-python | branch: loop/dsl-v2-python | root: code/isoroll-content
test-cmd: `python3 -m pytest -q` (53 pass) | e2e-cmd: none
criticality: normal | verdict: standard
criteria:
  C1 parse — all v2 fixtures parse; R/S voxels mismatching group spans → error; voxel double-booking (two chars claiming same voxel via groups vs grids) → error
  C2 round-trip — parse→serialize reproduces fixture verbatim (modulo trailing whitespace) for every fixture
  C3 massing — per-column runs match rig semantics: wallish runs with opening sub-runs (merged contiguous D/W with same side), per-level derived diagonals (diagSolid rule), floor plates with fh, group surfaces via grpBaseData/grpCellVoxels port (stairs stepped 45°=5ft or half=2.5ft only)
  C4 manifest — level→tile elevation, side→WallDef.dir, wallish run length→boundHeight aggregate, group cells→per-cell placements; HUD-count semantics: walls/diags count voxels, openings count RUNS
  C5 guide render — scene_guide_render consumes massing v2; multi-level fixture renders without error; l-room render change (if any) is deliberate and noted
  C6 existing pytest suite stays green
tasks:
  T1 — port group/diag geometry helpers to new layout_groups.py — high
  T2 — parser v2 (levels + attr grids + group lines + rotate) — high
  T3 — v2 validation (R/S vs group span, double-booking, stair incl) — high
  T4 — serializer updateDsl port (round-trip) — high
  T5 — massing v2 (run merge, openings, diagonals, floor fh, groups) — high
  T6 — manifest v2 + scene_assemble._piece_for + HUD counts — high
  T7 — guide render v2 consumes massing v2 — medium
  T8 — fixtures (l-room v2 + multilevel + groups) + golden tests — medium
context: code/CONTEXT.md, code/isoroll-content/CONTEXT.md, code/isoroll-content/SPECS.md, code/isoroll-content/src/pipeline/CONTEXT.md

## Ship

diff-scope: clean
  - Modified: ROADMAP-content-gen.md, src/pipeline/{CONTEXT.md,layout_massing.py,layout_massing.pyi,layout_parse.py,layout_parse.pyi,scene_assemble.py,scene_guide_render.py,scene_manifest.py,scene_manifest.pyi}, test/{CONTEXT.md}
  - Added: src/pipeline/{layout_dsl_v2.py,layout_dsl_v2.pyi,layout_groups.py,layout_groups.pyi,layout_serialize.py,layout_serialize.pyi}, test/fixtures/golden/{dsl_v2_groups.txt,dsl_v2_invalid_badincl.txt,dsl_v2_invalid_misplaced_r.txt,dsl_v2_lroom.txt,dsl_v2_multilevel.txt}, test/test_dsl_v2_{manifest,massing,parse,render,serialize}.{py,pyi}
  - No out-of-scope files; .loop/dsl-v2-python/ audit trail included per keep-trail: yes

roadmap: updated ROADMAP-content-gen.md (marked dsl-v2-python ✓ done with outcome summary)

commit: 0a4d990 pushed: yes
  Message: "feat(dsl-v2-python): DSL v2 parser, serializer, massing, and manifest integration"
  Pushed to: https://github.com/lsfcin/isoroll-content (branch: loop/dsl-v2-python)
  PR template: https://github.com/lsfcin/isoroll-content/pull/new/loop/dsl-v2-python

leftovers: none
  - All criteria fully met (C1–C6 per 5-user.md verdict: PASS)
  - Code review passed (verify-fast green, no regressions)
  - Test suite stable at 53 green tests
  - Lint warnings re: file line counts (layout_dsl_v2.py 166, layout_parse.py 175, layout_massing.py 165, scene_guide_render.py 166) are architectural — single-concern modules covering grammar, parsing, validation, serialization, and multi-level geometry; future refactor candidate if splitting improves cohesion (not a blocker per workspace standards)
  - Ready for user review and merge-to-develop per gitflow (do not merge — user's call)

executor: loop-low model=haiku tier=low
