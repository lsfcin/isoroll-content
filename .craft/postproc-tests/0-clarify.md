# Loop 0 — postproc-tests

## Carry
slug: postproc-tests | branch: feature/postproc-tests (base: feature/f1-procedural-spine — F1 core not yet merged to develop) | root: /mnt/workspace/code/isoroll-content
test-cmd: `/mnt/workspace/.venv/bin/python3 -m pytest test/ -q` | e2e-cmd: none
criticality: normal | verdict: standard
criteria: C1 — pytest suite exists, green, covering sheet_grid.detect_grid + strip_linework on synthetic magenta-grid fixtures
  C2 — guide_marks.residue_count tested: synthetic image with K cyan symbols → count in expected band; 0 on clean image
  C3 — new silhouette-IoU QC function (own file ≤200 LOC) comparing an NB output cell's silhouette vs the guide box mask; unit tests: ≈1.0 identical masks, <0.5 disjoint
  C4 — sheet_postproc split tolerates ±2px grid-line drift on a synthetic sheet (test proves it)
  C5 — `make verify-fast` still green; every file ≤200 LOC; no NB/API calls in tests
tasks: TBD (Loop 1 fills)
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, src/cli/CONTEXT.md, src/pipeline/CONTEXT.md, ROADMAP-content-gen.md

## Clarify
intent: real pytest suite + objective QC seam for NB postproc (grid split, mark residue, silhouette IoU).
motivation: the registration-marks A/B matrix needs numeric metrics; repo currently has zero tests (verify = compileall).
refs: ROADMAP-content-gen.md § post + § Matriz A/B; src/cli/sheet_grid.pyi; src/pipeline/guide_marks.py (residue_count); src/cli/sheet_postproc.py.
scope-files: test/** (new), one new QC module, src/cli/sheet_postproc.py (harden only).
expected-result: pytest green locally; QC functions importable by a future ab-runner.
ambition: solid
criticality: normal tolerance: unit-level only; no network, no GPU
innovation: none
verdict: standard
keep-trail: yes
