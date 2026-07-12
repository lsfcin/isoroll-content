## Carry
slug: isoroll-help-export | branch: loop/isoroll-help-export | root: /mnt/workspace/code/isoroll-content
test-cmd: `python -m pytest test/ -q` | e2e-cmd: none
criticality: low | verdict: padaria
criteria:
  C1: HELP string contains an `export-manifest` entry consistent with the existing entry formatting.
  C2: no code/behavior change outside the HELP string.
  C3: existing pytest suite stays green (`make verify-fast`, i.e. `python -m pytest test/ -q`).
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/src/cli/CONTEXT.md

## Clarify
intent: document the existing `export-manifest` CLI command in the `HELP` string of `src/cli/iso-cli.py` — `main()` already dispatches it (`elif command == "export-manifest"`), but `HELP` never lists it.
motivation: users running `iso-cli.py -h` (or an unknown-command fallback) get no indication `export-manifest` exists; the `mv-*` line documents multiview but the manifest exporter is undocumented.
refs: src/cli/iso-cli.py (HELP string, main() dispatch at the `elif command == "export-manifest"` line), src/cli/export_commands.py (run_export — argparse flags: --layout required, --kit default output/kit-guide, --view choices SW|SE|NE|NW default NW, --out default output/manifests/{layout.name}.manifest.json), src/cli/export_commands.pyi
scope-files: src/cli/iso-cli.py (HELP string only)
expected-result: `python iso-cli.py -h` output lists `export-manifest` with its flags, matching the formatting style of neighboring entries (command line + indented `--flag` description lines, or the compact single-line style already used for `mv-tile | mv-scene | mv-restyle`).
ambition: minimal
criticality: low tolerance: any regression is trivially reverted (one string literal, one file)
criteria: C1..C3 as above
innovation: none
verdict: padaria
keep-trail: yes

## Micro-plan
1. Add one `export-manifest` line to `HELP` in `src/cli/iso-cli.py`, right after the `mv-tile | mv-scene | mv-restyle` line, in the same compact single-line style (command + flags summary + description), since the full per-flag block style would push the file over the repo's 200-line code-size gate (file was already at 199 lines).
2. Verify `python iso-cli.py -h` renders the new line; run `python -m pytest test/ -q`, confirm still 33 passed.
3. No other file touched.

executor: loop-medium model=sonnet tier=medium
