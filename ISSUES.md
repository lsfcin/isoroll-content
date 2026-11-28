# isoroll-content issues
> What is currently untrue that we know about in this repo: hand-written issues
> first, every measured number inside its own generated block.

## Player artwork has no entry point in the Observatório prototype

Its character builder chooses a coded model by player index. Its lightweight renderer reads baked images of those same models. A player can bring a finished portrait but cannot select it as their character. Reproduce by joining a room and looking for a way to use a new image. Follow [art-direction] in ROADMAP.md to test identity, hidden views and the cost of adding another asset. [src: agent 2026-11-28]

## Shortlinks `lucassf.pages.dev/isoroll/*` in `refs/REFS.md` return HTTP 404

Ten `isoroll/*` shortlinks in `refs/REFS.md` (and `../isoroll-module/refs/REFS.md`) resolve to HTTP 404 on `lucassf.pages.dev`. Their targets live in `code/wos/core/tools/links/links.txt` and are missing from root `core/tools/links/links.txt` (or unpublished via `cfpages build --push`). Reproduce with `curl -sI https://lucassf.pages.dev/isoroll/oil-paint`. [src: agent 2026-11-28]
