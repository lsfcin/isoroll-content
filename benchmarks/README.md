# isorolling Benchmark Outputs

This folder is for tracked reference outputs only.

Raw ComfyUI generations stay ignored under `assets/chars/`. Promote outputs
here only when useful as a benchmark for future workflow changes, such as
comparing checkpoints, profiles, or a detailer pass.

## Structure

Actual convention (not the single-`images/`+root-`manifest.json` scheme
this file used to describe — that was never adopted; zero samples, deleted
2026-07-04): one folder per comparison, each with its own images and its
own `manifest.json`.

```text
  benchmarks/
    README.md
    {comparison-name}/
      *.png
      manifest.json    # [{model, seed, time_s, file, prompt?}, ...] — see SPECS.md
    tile-guide-test/    # deterministic script QC output, not AI-generation comparisons
```

## Rules

- Keep this folder small and intentional — one folder per question being answered.
- Every tracked image must have a `manifest.json` entry (`file` path relative to repo root).
- Prefer stable, comparable prompts/seeds across the images in one folder.
- When a comparison gets a new round, replace the folder's contents in place
  (or rename off the version suffix once superseded) rather than keeping
  `-v2`/`-v3` copies indefinitely — git history already has the old round.

## Adding a Sample

1. Generate normally into `assets/chars/...` (gitignored).
2. Pick the representative image(s) for the comparison.
3. Copy them into `benchmarks/{comparison-name}/`.
4. Add matching entries to `benchmarks/{comparison-name}/manifest.json`.
