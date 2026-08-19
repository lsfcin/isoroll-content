# Layout and entry points
> What lives where, which CLI entry points exist, and how src/cli/ is arranged.
> governs: src/

## Source Boundaries

Versioned source should include:

- CLI code: `src/cli/iso-cli.py`, `src/cli/iso-cli.bat`
- ComfyUI API workflows: `src/cli/workflows/*.json`
- Pipeline scripts: `src/pipeline/*.py`
- Curated benchmark references: `benchmarks/README.md` and each `benchmarks/{comparison-name}/`
  folder (images + its own `manifest.json`)
- Tracked tile art: `assets/tiles/`
- Future Foundry module code under `foundry/`
- Project docs: `CONTEXT.md`, `SPECS.md`, `ROADMAP.md`

Generated or local-only artifacts should not be committed by default:

- `assets/chars/`
- generated images under `assets/**/*.png`, `assets/**/*.jpg`, `assets/**/*.jpeg`, `assets/**/*.webp`
- local experiment bundles such as `*.zip`
- local ComfyUI outputs and temp folders
- `.env`, logs, Python caches, virtualenvs

Note: `profiles/` (render profile JSONs) existed but was deleted — confirmed zero
references from any code (`grep` across `src/`). If profile-driven generation is
revisited, recreate it under `src/profiles/` and wire it into `gen_commands.py`
rather than reintroducing inert metadata.

Benchmark images are the only generated images intended to be tracked in this repository. They are
manually promoted from raw outputs and must have metadata in that folder's own `manifest.json`.

## CLI Entry Points

From the repository root:

```powershell
.\src\cli\iso-cli.bat gen-character "medieval rogue with red cloak" --profile quality --out assets\chars\rogue-test
```

From inside `src/cli/`:

```powershell
.\iso-cli.bat gen-character "medieval rogue with red cloak" --profile quality --out ..\..\assets\chars\rogue-test
```

## `src/cli/` module layout

`iso-cli.py` was split into focused modules (each under the 200-line hook
limit) — this replaces the old single-file description. Current shape:

- `iso-cli.py` — argument parsing + command dispatch (`gen-character`,
  `style-concept`, `ipadapter-ref`, `detail-image`, `face-restore`,
  `blender-stylize`, `blender-ipadapter`). No business logic lives here.
- `comfy_client.py` — ComfyUI API primitives: `get_comfy_dir()`,
  `get_output_dir()`, `upload_image()`, `send_prompt()`, `snapshot_pngs()` /
  `wait_for_new_png()` (before/after snapshot — the actual output-tracking
  mechanism; `/history`+`prompt_id` from M1 was never implemented),
  `load_workflow()`, `copy_to_dir()`.
- `workflow_ops.py` — workflow-JSON mutation helpers: `apply_random_seeds()`,
  `inject_prompt()`, `inject_input_image()`, `inject_concept_image()`,
  `set_base_denoise()`, `set_ipadapter_weight()`, `inject_output_size()`.
- `gen_commands.py` — `gen_character()`, `style_concept()`, `ipadapter_ref()`.
- `image_commands.py` — `detail_image()`, `face_restore()`.
- `blender_commands.py` — `blender_stylize()`, `blender_ipadapter()`.

There is no `PROFILE_DIR` / `load_profile()` anymore — `profiles/` was
deleted (confirmed zero references from any code before removal). Workflow
selection is purely by filename: `character_{profile_name}.json`.

## Folder structure

See root `CONTEXT.md` → `## Repository Shape` for the authoritative current
tree (`src/`, `assets/`, `benchmarks/`). The `outputs/{benchmark,characters,
tiles,items,effects}/` nesting once proposed here (2026-05-26) was never
built — real layout is flat `assets/{chars,tiles}/` and top-level
`benchmarks/`, kept in one place to avoid two competing diagrams drifting
apart again.

Still pending from M1 (see ROADMAP.md): `argparse`, `doctor` command,
`/history`-based output tracking, batch mode, nonzero exit codes.
