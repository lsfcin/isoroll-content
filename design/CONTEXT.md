# design
> ← add description

<!-- routing:start -->
## Routing

| File | Interface | Description |
|------|-----------|-------------|
| [`DSL-V2-MEMO.md`](DSL-V2-MEMO.md) | — | Feeds the DSL-v2 implementation loop and the Painter MVP (P6.5/P7). Decisions here are the contract both twins (`layout_parse.py`, `src/assemble/layout-parse.ts`) implement. Companion: SCENE-CREATION.md (contract), PAINTER-UX.md (queued extensions this memo resolves). Status: 2026-07-10 — proposed by architecture consult, ☐ Lucas sign-off before the loop. |
| [`PAINTER-UX.md`](PAINTER-UX.md) | — | **GRAMMAR FROZEN 2026-07-13 @ rig v16.2** (Lucas: "painter can be freezed", after 19 rounds). The rig source (`feel-rig/rig.frag`) is the NORMATIVE reference implementation for DSL v2 + P7. Changes now require unfreeze + a new round below. Living doc for the "feels like magic" requirement. Prototype-first: iterate here + in the feel rig BEFORE any Foundry… |
| [`RENDER-RESTYLE-MEMO.md`](RENDER-RESTYLE-MEMO.md) | — | **FROZEN decision record** (decided 2026-07-13/14, see the two "Lucas decided" sections). Status-free by |
| [`art-direction-memo.md`](art-direction-memo.md) | — | Decision memo for [art-direction] (2026-11-28): translated player-image target, option costs, outside panel verdicts, 3D customizer boundary, and conditional D4 reopen gate. |
| [`feel-rig/build.py`](feel-rig/build.py) | [`feel-rig/build.pyi`](feel-rig/build.pyi) | build.py — assemble painter-feel-rig.html from rig.frag + kit_b64.txt (repo copy; publish via Artifact tool, same URL) |
| [`feel-rig/kit_b64.txt`](feel-rig/kit_b64.txt) | — | ← add first-line comment |
| [`feel-rig/stage_kit_paint.py`](feel-rig/stage_kit_paint.py) | [`feel-rig/stage_kit_paint.pyi`](feel-rig/stage_kit_paint.pyi) | stage_kit_paint.py — one-off: stage P5 kit-painting inputs into output/gen-inbox (arm A + arm B) |
<!-- routing:end -->
