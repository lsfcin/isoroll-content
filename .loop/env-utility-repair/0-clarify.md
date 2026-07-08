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
