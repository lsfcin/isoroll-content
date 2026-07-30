# History

Archive of completed work and resolved issues.

## Completed — 2026-07-29

### MVP-first replan (Lucas + inline)
- [x] Strategic revisit of the whole scene-creation approach, triggered by Lucas losing confidence in the
  path while stalled on arm-A stair enclosure masks. Outcome: renderer seam frozen, content strategy
  demoted from prerequisite to A/B behind it, MVP-first milestone order (SEAM → PLAYABLE → BAKEOFF →
  RICHNESS). Decisions D1–D7 recorded in ROADMAP.md; new kill-log rows in SCENE-CREATION.md (reusable
  sprite vs continuity, per-module enclosure masks, slice/seam vocabulary, tile extraction from scene
  images).
- [x] Doc restructure: one live-state file (`ROADMAP.md`, absorbed `ROADMAP-content-gen.md`), spec made
  status-free (`SCENE-CREATION.md`, P0–P9 retired), `SESSION-HANDOFF.md` folded here, `design/S4-REVIEW-
  ROUNDS.md` moved to `archive/`. Three live docs instead of six — the confusion was three parallel plans
  with three vocabularies (`P0–P9` / `S1–S8` / `rounds 1–4b`), not file count.
- [x] arm_a renderer engine merged to `develop` (tag `pre-arm-a`, 64 commits, `make verify-fast` 142
  passed): `texture_map.py`, `texture_warp.py`, `texture_resample.py`, `face_edges.py`, `face_masks.py`,
  `kit_module_render.py`. The step-4b enclosure-mask refinements were committed intact (`92b6c50`) before
  parking the lane, so it can resume whole if arm A wins the bake-off.

### S4 arm_a homography (session 2026-07-17, folded from SESSION-HANDOFF.md)
- [x] Per-face texture homography shipped through Lucas review rounds 1–4b — full decision log in
  `archive/S4-REVIEW-ROUNDS.md`. Landed: `texture_map.py` + `texture_warp.py` + `project_face`, arm_a
  rewrite, per-module sheet composer, 512 px/voxel + 2× supersample→LANCZOS, edge lines on normal-change
  boundaries, doors/windows as standalone 0.1-voxel slabs (hole = a wall column not placed), roofs/stairs
  cover-only with enclosure emitted as masks, zigzag stair solid, backface culling for all modules.
  Board (arm_a, style verdict never given): https://claude.ai/code/artifact/b75e182b-19cb-4e97-896d-f76126a85edb
- [x] NOBUG verified: stair y45/y225 and roof y135/y315 have ~0 lateral area (edge-on) → enclosure masks
  correctly absent there by geometry.

## Completed — 2026-07-05

### M1 — Stabilize `iso-cli`
- [x] Normalize CLI encoding and messages — no mojibake or Portuguese strings remain (resolved by the `iso-cli.py` module split; verified clean ASCII + intentional Unicode across all `src/cli/*.py`).
- [x] Replace prompt-injection heuristic with literal `REPLACE_PROMPT` substitution — `workflow_ops.py::inject_prompt()`.
- [x] Remove duplicate seed randomization — `apply_random_seeds()` is called exactly once per command.
- [x] Make `COMFY_URL` configurable via env var — `comfy_client.py::COMFY_BASE_URL = os.environ.get("COMFY_URL", ...)`.
- [x] Validate `COMFY_DIR` and workflow path before submitting — `get_comfy_dir()` raises if unset; each command checks its workflow path exists before running.
- [x] Return nonzero exit code on generation failure — `sys.exit(1)` on missing workflow, submit failure, and generation timeout.

### M2 — Workflow and Profile Contract
- [x] Decided whether profiles are active configuration or metadata: metadata-only, never wired to workflow nodes. Deleted `profiles/` outright rather than building the application layer — confirmed zero code references before removal.

## Completed — 2026-07-03

### M0 — Repository Baseline
- [x] Create project-local `.gitignore`.
- [x] Keep generated character images out of Git.
- [x] Add `CONTEXT.md`, `SPECS.md`, and `ROADMAP.md`.
- [x] Create `content/benchmark/` for tracked reference images plus prompt/profile metadata.
- [x] Create `content/cli/`, `content/profiles/`, and `foundry/` top-level areas.
- [x] Benchmark model comparison done: lyriel_v16 recommended for dark-fantasy style.

### Phase C — GPT Concept + Sheet Input Pipeline
- [x] Generate `sheet_template.png` (blank, for GPT upload) and `sheet_template_guide.png` (labeled, human reference)
- [x] Write `concept_art_prompt.md` — copy-paste ready, includes rogue example
- [x] Write `sheet_prompt.md` — copy-paste ready, includes rogue example

### S1 — Novel View Synthesis
- [x] Download stable_zero123.ckpt — at `/mnt/workspace/Downloads/stable_zero123.ckpt` (8 GB)

### S3 — TripoSR Mesh + Mixamo Rig + Blender Render
- [x] Implement `triposr_mesh.py`
- [x] Implement `s3_batch.sh`
- [x] Fix TripoSR ViT key remapping (`_remap_vit_keys` in `/home/lucas/TripoSR/tsr/system.py`)
- [x] Fix Blender FBX axis conversion (`axis_up='Y'` in `_FBXOperatorStub` + load call)
- [x] Fix Blender transparent renders (`_apply_solid_material` for `--no-materials` mode)
- [x] Generate rogue T-pose images and T-pose mesh
- [x] Phase A (Mixamo orientation fix): correct rotation confirmed 2026-05-27 — raw TripoSR output needs Z=+90°; `triposr_mesh.py` default is now `--mesh-rotate-z 90`.

### S4 — External Generation + Local Post-Processing
- [x] Implement `content/cli/sprite_splitter.py` (split + rembg + save)

## Completed — 2026-07-14 (post-freeze execution day 1)
- P6.5 painter UX design: grammar FROZEN @ feel-rig v16.2 after 19 rounds (2026-07-13; rounds 16–19 same-day: per-voxel model, sloped-group unification roofs+stairs, two crop-clean stair slopes, skirt-clip fix, selection priority). Full log: design/PAINTER-UX.md.
- Loop dsl-v2-python SHIPPED (0a4d990+45a2f97): DSL v2 parser/serializer/massing/manifest/guide-render, 53/53 pytest. One Loop-5 integration gap (groups→manifest) caught and closed via RETURN loop=3 inline ruling.
- Loop kit-module-renderer SHIPPED (b56abc0+189c90c): flat-shaded KIT V2 module renderer, per-face masks, shared px-per-voxel manifest, 3 P5 arm sheets staged to gen-inbox. 82 pytest.
- Module loop dsl-v2-ts-twin SHIPPED (aad8dac): TS parser/massing/manifest twin, 92 tests + 9/9 live twin-diff vs Python.
- P5 strategy: render→restyle lane R promoted to candidate-primary (RENDER-RESTYLE-MEMO; arms b/b+c/a; flat-shaded; whole-sheet; web app); P-CTRL/P-Kit relabeled lane-R siblings.

## Completed — 2026-07-16 (session: cleanup → texture set)

- Face masks reworked: human-visible id encoding (MASK_BASE 40 + step 8), machine
  artifacts moved out of gen-inbox to output/masks/ — gen-inbox = only the 6 files
  Lucas hand-feeds NB (f7b6b02).
- Image relic cleanup: 40 broken/black/v1 files + ~33 killed-lane relics (triplicated
  guides, box-kit era, assembled previews) removed; kit-guide fixture restored after
  discovering it is a live test dependency (lesson: gitignored ≠ disposable).
- /linework SVG texture generator: 50 textures covering the full painter vocabulary
  (floor stone/wood, wall wood/stone sides+tops, window, 5 door sizes, roof shingles,
  stair tread/riser strips, grass, cobble + dirt roads), 3 Lucas feedback rounds
  applied (keyhole shape+5ft rule, no-cross joints, thin window frame, one keyhole per
  double door), 11 seam tests, suite 93/93 (4a02fb4..75085e0).
- anchored-kit-marks loop: clarify/plan/ground/arch all PASS, then PARKED by Lucas —
  marks must work as a texture warped by homography, not a separate layer.
- Module painter P7a Loop 4b: 127/127 green, WIP commit 3987979 (facade debt noted).
- Plan refined to content-first S1-S8 (ROADMAP-content-gen § Plano refinado) with
  step-by-step + eyeball-gate standing rules; decisions logged in RENDER-RESTYLE-MEMO.
