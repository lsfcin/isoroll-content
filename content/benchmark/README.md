# isorolling Benchmark Outputs

This folder is for tracked reference outputs only.

Raw ComfyUI generations stay ignored under `content/characters/`. Promote an image here only when it is useful as a benchmark for future workflow changes, such as comparing `fast`, `balanced`, `quality`, YOLO detailer, or hand-detailer behavior.

## Structure

```text
  content/benchmark/
  README.md
  manifest.json
  images/
```

## Rules

- Keep this folder small and intentional.
- Every tracked image must have a `manifest.json` entry.
- Record at least: file path, prompt, profile, workflow, and why the sample matters.
- Prefer stable, comparable prompts over one-off experiments.
- Do not store raw batches here.

## Adding a Sample

1. Generate normally into `content/characters/...`.
2. Pick one representative image.
3. Copy it into `content/benchmark/images/`.
4. Add a matching entry to `content/benchmark/manifest.json`.
