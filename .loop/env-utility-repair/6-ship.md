# Loop 6 — env-utility-repair — Ship

## Carry
slug: env-utility-repair | branch: feature/env-utility-repair | root: /mnt/workspace/code/isoroll-content
test-cmd: `make verify-fast` | e2e-cmd: none
criticality: low | verdict: padaria
criteria: C1 — every symlink under $HOME/ComfyUI/models/{checkpoints,embeddings,loras,upscale_models} resolves to an existing directory
  C2 — 4xUltrasharp_4xUltrasharpV10.pt exists under the resolved upscale_models dir (source per SETUP.md §3)
  C3 — if ComfyUI is already running, `curl -s localhost:8188/object_info` responds; if not running, note and skip (do NOT start services)
  C4 — SD checkpoints NOT downloaded (explicitly out of scope)
tasks: T1-T4, see 0-clarify.md micro-plan
context: /mnt/workspace/code/isoroll-content/CONTEXT.md, /mnt/workspace/code/isoroll-content/SETUP.md

## Ship
criteria-result:
  C1 — PASS. `mkdir -p /mnt/workspace/Models/diffusion/{checkpoints,embeddings,loras,upscale_models}` created the missing parent; all 4 symlinks under `$HOME/ComfyUI/models/` now resolve (verified via `test -e` + `readlink -f` on each).
  C2 — PASS. SETUP.md §3 names the source as "Civitai / OpenModelDB" but gives no literal URL — resolved via web search to a byte-identical HF mirror (`huggingface.co/MochaPixel/4XUltrasharpV10`, x-linked-etag matched a second independent mirror `HUGGHan/VAE`, size 66,961,958 B ≈ 63.9 MB matching OpenModelDB's stated size). Downloaded on attempt 1/2 to `/mnt/workspace/Models/diffusion/upscale_models/4xUltrasharp_4xUltrasharpV10.pt`. No retry needed.
  C3 — NOTED, not applicable. `curl -s --max-time 3 localhost:8188/object_info` → connection failed (ComfyUI not running; no comfy process in `ps aux`). Per instructions, did not start it.
  C4 — PASS. `/mnt/workspace/Models/diffusion/{checkpoints,embeddings,loras}` are empty; no SD checkpoint downloaded.
diff-scope: clean | extras: none (SETUP.md troubleshooting note + ROADMAP.md backlog line + .loop/ trail — all in-scope per Carry scope-files)
roadmap: updated /mnt/workspace/code/isoroll-content/ROADMAP.md (Backlog / Ideas — "Env utility repair (2026-07-08, padaria, done)")
commit: 30a6f78 pushed: no — repo has no configured remote (`git remote -v` empty); recorded here per task instructions instead of failing.
leftovers: none. Real-world side effects outside the repo (not part of any commit): created `/mnt/workspace/Models/diffusion/{checkpoints,embeddings,loras,upscale_models}` and placed `4xUltrasharp_4xUltrasharpV10.pt` (66,961,958 B) in `upscale_models`. Worktree at `/tmp/claude-1000/-mnt-workspace/bb9b9715-4ea6-4628-9115-ce47ee08dba4/scratchpad/wt-env-utility-repair` (branch `feature/env-utility-repair`, base `develop`) is left in place — not merged, merge is the user's call, `.loop/<slug>/` kept per `keep-trail: yes`.
executor: loop-medium model=sonnet tier=medium
