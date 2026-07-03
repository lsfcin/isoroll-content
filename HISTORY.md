# History

Archive of completed work and resolved issues.

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
