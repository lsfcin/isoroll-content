# History

Archive of completed work and resolved issues.

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
