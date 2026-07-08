# Loop 0 — env-utility-repair

## Carry
slug: env-utility-repair | branch: feature/env-utility-repair | root: /mnt/workspace/code/isoroll-content
test-cmd: `make verify-fast` | e2e-cmd: none
criticality: low | verdict: padaria
criteria: C1 — every symlink under $HOME/ComfyUI/models/{checkpoints,embeddings,loras,upscale_models} resolves to an existing directory
  C2 — 4xUltrasharp_4xUltrasharpV10.pt exists under the resolved upscale_models dir (source per SETUP.md §3)
  C3 — if ComfyUI is already running, `curl -s localhost:8188/object_info` responds; if not running, note and skip (do NOT start services)
  C4 — SD checkpoints NOT downloaded (explicitly out of scope)
tasks: TBD (padaria micro-plan below)
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/SETUP.md

## Clarify
intent: repair the ComfyUI utility-model environment — dead symlinks plus the missing upscale model, nothing else.
motivation: every local CLI command fails at ComfyUI runtime today; the NB lane is unaffected but the utility rail (upscale/rembg) is needed for postproc.
refs: ROADMAP-content-gen.md § Delegação /loops; SETUP.md §3 (model list + URLs).
scope-files: none in repo besides .loop trail (optional: one-line SETUP.md troubleshooting note); real work under $HOME/ComfyUI/models and /mnt/workspace/Models/diffusion.
expected-result: symlinks resolve; upscale model file present; `upscale_pass.json` loadable by a running ComfyUI.
ambition: minimal
criticality: low tolerance: partial OK — any download that fails after 2 attempts becomes a leftover line, not a retry hunt
innovation: none
verdict: padaria
keep-trail: yes

## Micro-plan (padaria)
- T1: mkdir -p target dirs under /mnt/workspace/Models/diffusion/{checkpoints,embeddings,loras,upscale_models} so all 4 symlinks resolve (C1).
- T2: download 4xUltrasharp_4xUltrasharpV10.pt into resolved upscale_models dir; SETUP.md §3 names source "Civitai / OpenModelDB" but gives no literal URL — resolved via web search to a verified HF mirror, max 2 attempts (C2).
- T3: curl localhost:8188/object_info if ComfyUI already running; do not start it (C3). No SD checkpoint downloaded (C4).
- T4: run `make verify-fast` in worktree; optional one-line SETUP.md note.
executor: loop-medium model=sonnet tier=medium

## Ground
branch-created: feature/env-utility-repair base: develop (worktree: /tmp/claude-1000/-mnt-workspace/bb9b9715-4ea6-4628-9115-ce47ee08dba4/scratchpad/wt-env-utility-repair)
paths: 2/2 ok ($HOME/ComfyUI/models exists; SETUP.md exists in worktree) | missing: none
test-cmd-runs: yes (`make -n verify-fast` resolves to `python3 -m compileall -q .`)
executor: loop-medium model=sonnet tier=medium
