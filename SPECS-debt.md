# Requirements and known debt
> What the runtime assumes, the pattern to prefer, and the debt not yet paid.
> governs: src/

## Runtime Requirements

See [`SETUP.md`](SETUP.md) for full environment setup: ComfyUI install, required models, extensions,
and `COMFY_DIR` configuration.

Runtime expectations (enforced by code):

- ComfyUI running at `http://127.0.0.1:8188` (not yet configurable via flag — see M1)
- `COMFY_DIR` env var pointing to local ComfyUI root
- `requests` importable in Python
- ComfyUI output dir: `${COMFY_DIR}/output`

Do not hardcode local paths in versioned files — always use `COMFY_DIR` or CLI flags.

## Preferred Implementation Pattern

For major generation changes:

1. Add a new workflow JSON instead of overwriting the working baseline.
2. Add a profile only if the CLI can select and validate it.
3. Preflight required ComfyUI node classes and model names.
4. Run one end-to-end generation.
5. Compare output quality against `balanced`, `quality`, and `quality_x4`.
6. Only promote the workflow after it improves quality without unacceptable time or VRAM cost.

## Known Technical Debt

- CLI strings show mojibake in Portuguese messages. Normalize file encoding and messages later.
- `COMFY_URL` is not configurable.
- The CLI should use `argparse` or similar instead of manual index parsing.
- Output tracking should ideally use ComfyUI `prompt_id` and `/history` instead of filesystem snapshots.
- There are no automated tests.
- All workflow JSONs still hardcode `dreamshaperPixelart_v10.safetensors` — update to `lyriel_v16.safetensors`.

---
