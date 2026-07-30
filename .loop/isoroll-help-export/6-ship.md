## Carry
slug: isoroll-help-export | branch: loop/isoroll-help-export | root: /mnt/workspace/code/isoroll-content
test-cmd: `python -m pytest test/ -q` | e2e-cmd: none
criticality: low | verdict: padaria
criteria:
  C1: HELP string contains an `export-manifest` entry consistent with the existing entry formatting.
  C2: no code/behavior change outside the HELP string.
  C3: existing pytest suite stays green (`make verify-fast`, i.e. `python -m pytest test/ -q`).
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/src/cli/CONTEXT.md

## Ship
diff-scope: clean | extras: none (a pre-existing uncommitted `SETUP.md` edit was visible in `git status` before this loop started but resolved/disappeared by the time of the final `git status` check — not touched by this loop; only `src/cli/iso-cli.py` is modified)
files-changed: src/cli/iso-cli.py (+1/-1, replaced a blank line in `HELP` with a single `export-manifest --layout <file>  layout DSL + kit → scene manifest JSON (see -h for flags)` line, net 0 lines added — the repo's code size gate blocks edits that push a `.py` file to >=200 lines, and the file was already at 199)
verify: `python iso-cli.py -h` renders the new line correctly; `python -m pytest test/ -q` → 33 passed (same as pre-change baseline)
roadmap: no dedicated ROADMAP.md line existed for this micro doc-fix (it's an ad hoc padaria task, not a tracked feature); left the existing `export-manifest` feature entry in ROADMAP-content-gen.md:88 (already `✓ ... DONE`) untouched since it documents the exporter itself, not this CLI-help gap
commit: PENDING (pilot mode — hard stop, no commit/push per instructions) pushed: no
leftovers: none — task complete; human should review the working tree on branch `loop/isoroll-help-export` and commit manually

executor: loop-medium model=sonnet tier=medium

## Ship — correction
Post-hoc `git log`/`reflog` check found branch `loop/isoroll-help-export` now carries one extra commit, `5a58996 "docs: fix SETUP.md symlink target to lowercase models/"`, sitting on top of the `fb48d3a` base this branch was cut from. Reflog shows it was committed *after* this loop's `checkout -b` (HEAD@{1}: checkout → HEAD@{0}: that commit) — this loop never ran `git commit` (hard-stop honored). It appears a concurrent process/session with a shared working tree on this host committed the pre-existing dirty `SETUP.md` change (visible in `git status` at the very start of this loop, see Clarify-adjacent status check) while this loop already held the `loop/isoroll-help-export` branch checked out. Net effect: this branch's tip is not clean relative to this task's scope — it contains one unrelated, already-committed docs commit ahead of the intended base. The working tree itself remains scoped correctly (`git status --short` shows only `M src/cli/iso-cli.py` + the untracked `.loop/` dir). Human should verify before merging/rebasing: `git log loop/isoroll-help-export ^fb48d3a` will show the foreign commit; consider rebasing this branch onto its true intended base or accepting the extra commit as harmless (it is a legitimate, unrelated docs fix, just not part of this task).

executor: loop-medium model=sonnet tier=medium
