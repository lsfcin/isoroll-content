# fixtures
> Committed inputs and expected outputs the suite asserts against, so a regression is a diff.
> spec: none

Everything here is read, never written, by a test. Three kinds live in [`golden/`](golden/):
the v2 DSL sources (`dsl_v2_*.txt`, including the two `invalid_*` cases that must raise), the
PNG sheets the postproc tests measure, and the cabin manifests the PLAYABLE fixture checks per
view.

A fixture is regenerated only when the contract it pins changes on purpose — re-baking one to
make a red test green is how a golden stops being an oracle.

<!-- routing:start -->
## Routing

| File | Description |
|------|-------------|
| [`golden/dsl_v2_groups.txt`](golden/dsl_v2_groups.txt) | ← add first-line comment |
| [`golden/dsl_v2_invalid_badincl.txt`](golden/dsl_v2_invalid_badincl.txt) | ← add first-line comment |
| [`golden/dsl_v2_invalid_misplaced_r.txt`](golden/dsl_v2_invalid_misplaced_r.txt) | ← add first-line comment |
| [`golden/dsl_v2_lroom.txt`](golden/dsl_v2_lroom.txt) | ← add first-line comment |
| [`golden/dsl_v2_multilevel.txt`](golden/dsl_v2_multilevel.txt) | ← add first-line comment |
<!-- routing:end -->
