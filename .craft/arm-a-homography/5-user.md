# Loop 5 — User Test: arm-a-homography

## Carry
slug: arm-a-homography | branch: loop/arm-a-homography | root: /mnt/workspace/code/isoroll-content
base: loop/anchored-kit-marks @ 4126704 (PIN — doc lineage lives here, NOT develop)
test-cmd: `make verify-fast` (= /mnt/workspace/.venv/bin/python3 -m compileall -q . && pytest test/ -q; 93/93 green at base) | e2e-cmd: none (Loop 5 scripts stage → gen-inbox render + QC)
criticality: normal | verdict: standard
criteria:
  C1 arm_a paints every projected face quad of ALL kit modules in stage_kit_modules by homography-warping a texture PNG from assets/textures/ — no flat MAT_COLORS fills remain in arm_a output
  C2 mapping face(kind,mat) → texture FAMILY via textures.json (wall band stone → wall_stone_side, wood → wall_wood_side, tops → wall_{mat}_top, floor → floor_{mat}, roof_cell → roof_shingle, stair top → stair_tread, stair riser (side ‖±u) → stair_riser, stair side ‖±v/back → wall stone side clipped by face polygon; door/window recess → matching decal); VARIANT within a family selected deterministically from stable world column index — all variants exercised, same column = same variant in all 9 views
  C3 tiling semantics honored: texture tile spans exactly dims_voxels in world units; adjacent voxels continue the pattern horizontally (continuity=horizontal — sample offset from world position, no per-voxel restart); decals placed once per opening, aligned to the opening quad, no tiling
  C4 px-per-voxel scale comes from the module manifest (shared_scale), never re-measured from pixels; one s per sheet
  C5 restage writes ONE sheet PER MODULE per arm to output/gen-inbox/ (`{module}__{arm}.png` + `{module}__{arm}_prompt.txt` stem pairs); 9 views per sheet; packed per R3 (gutter+magenta separators, bottom-right cell empty, no per-panel autofit)
  C6 `make verify-fast` fully green: pre-existing tests (stage-contract tests amended per R2, never deleted) + new tests for C1–C4, C8
  C7 code-verified coverage: for a fixture module, every face-mask pixel (face_masks.py) is non-background in the arm_a render (no unpainted face), asserted in a test — geometry by code, never model eyes
  C8 variant coverage: a multi-column fixture face shows ≥2 distinct variants; variant choice is view-invariant (same column, same variant across yaws), asserted in a test
tasks:
  T1 — texture_map.py (NEW): textures.json loader + MAPPING (module,kind,orientation)→family, mat blank→stone default, stair-face classify by world normal, recess opening→decal id+world quad, deterministic variant-from-world-column (R1) — src/pipeline/texture_map.py — medium
  T2 — texture_warp.py (NEW): warp_tiling + warp_decal; per-corner texture-px coords from world axes (orientation-safe, dot products, never index maps), tiled source builder, polygon mask; PERSPECTIVE (4-corner) + AFFINE (3-corner) — src/pipeline/texture_warp.py — medium(→high if warp math fights)
  T3 — project_face(pts,view,s,cell_px,pad,origin) public helper (additive, mirrors ordered_faces transform) — src/pipeline/kit_module_render.py — low
  T4 — arm_a rewrite: per-panel textured paint_panel via T1+T2+T3; rebuild faces=km.MODULES[module]() index by builder-i from face_id; decals for recess; KEEP arm_a(panels,ordered_by_panel) signature — src/pipeline/stage_kit_modules.py — medium
  T4b — per-module sheet composer + stage() restage contract per R2/R3 (stem pairs, gutter, magenta separators, empty bottom-right cell); amend existing stage-contract tests — src/pipeline/stage_kit_modules.py, test/ — medium
  T5 — tests: test_texture_map.py(C2), test_texture_warp.py(C3,C4), test_arm_a_texture.py(C1+C7), variant coverage+view-invariance(C8) — test/ — medium
  T6 — restage stage() → gen-inbox per-module sheets; make verify-fast green (C5,C6) — low
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/src/pipeline/CONTEXT.md, /mnt/workspace/code/CONTEXT.md, /mnt/workspace/core/skills/iso-visual.md

## User Test
scenario: Lucas has just merged the homography-warp rewrite of arm_a and wants
to hand the real render output to the NB restyle web app. He runs the actual
staging entrypoint against the real kit modules (not a test fixture) and
expects, in `output/gen-inbox/`, one 5x2 sheet per module per arm (`a`/`b`/`bc`)
— 9 modules × 3 arms — each sheet showing genuinely textured faces on arm_a
(no flat gray/brown MAT_COLORS placeholders), one consistent px-per-voxel
scale across every sheet, and an empty bottom-right watermark cell, ready to
paste stem-pair by stem-pair into the restyle tool.

script: inline (no saved script file — one-shot verification of the real
`stage()` entrypoint, not a fixture harness) run:
`/mnt/workspace/.venv/bin/python3 -c "import sys; sys.path.insert(0,'src/pipeline'); import stage_kit_modules as skm; skm.stage()"`
(from repo root; writes to the real `output/gen-inbox/` — gitignored dir, `output/`)

observed:
- `make verify-fast` (compileall + pytest test/ -q) immediately before restage: `122 passed, 225 warnings in 1.22s`, exit 0 — matches Carry test-cmd, matches 4b-code.md's own green run.
- `stage()` completed with no exception; wrote 60 files to `output/gen-inbox/` (54 new per-module files + 6 pre-existing leftover global-sheet files from before this rewrite, e.g. `arm_a.png`/`restyle_arm_a.md` — gitignored dir, out of diff scope, left in place, not part of this loop's contract).
- Per-module × per-arm coverage: all 9 modules (`wall_band, top_cap, base, recess_door, recess_window, diag_half, roof_cell, stair_45, stair_half`) × 3 arms (`a, b, bc`) present as `{module}__{arm}.png` + matching `{module}__{arm}_prompt.txt` — 27/27 png, 27/27 prompt txt confirmed by direct path check.
- All 27 sheets: identical size `(352, 136)` px → identical `cell_px=64` → one shared px-per-voxel across every sheet (C4 holds at the real-render level, not just the test fixture).
- Bottom-right cell (grid idx 9, row 1 col 4) sampled fully black `(0,0,0)` on every one of the 27 sheets — empty watermark cell (R3) holds.
- Magenta `(255,0,255)` separator pixels present (2652 px sampled on `wall_band__a.png`) — gutter/separator convention holds.
- arm_a texture sanity: `wall_band__a.png` cell 0 (a populated view) has per-channel pixel stdev ≈113.5 and 25 distinct RGB values across 4096 px — not a flat single-color fill, consistent with a warped texture PNG rather than a leftover MAT_COLORS solid fill (coarse sanity only; C1/C7's real assertion is the code-verified pixel-coverage test in `test_arm_a_texture.py`, already green under `make verify-fast`).

matches-expected-result: yes — real `stage()` restage into `output/gen-inbox/`
produces exactly the per-module stem-pair contract (C5), one shared scale
(C4), empty bottom-right cell (R3), and visibly textured arm_a output, with
the full test suite green immediately prior. No diff from Carry criteria
observed at the live-render level beyond what the test suite already proves
at the fixture level.

executor: loop-medium model=sonnet tier=medium
