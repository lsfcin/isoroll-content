# S0-E2 — Tile Multiview Prompt Template

**Goal:** Given a concept image (identity/material anchor) + a script-generated guide schematic
(`make_tile_guide.py`), get Nano Banana to fill the guide's panel layout with real, consistent art.
**Inputs:** `tiles/{name}/{name}_concept.png` + `benchmarks/tile-guide-test/.../guide_*.png` (or a
freshly generated guide at the asset's real W×H×D).
**Output:** one filled grid image, split by `cli/sprite_splitter.py` (S0-E3) into per-facing files.

Research grounding for every design choice below is in the S0 session notes — the short version:
Nano Banana has no ControlNet-style hard conditioning (Autodesk APS test — geometry gets
"reinterpreted," not preserved), so the guide is a strong suggestion we reinforce in text, not a
mask it's forced to obey. Explicit per-region text binding measurably beats relying on color
alone (GLIGEN/BoxDiff literature). Multi-object/multi-panel scenes score far worse than single-
object ones on view-direction fidelity (GenSpace: 59%→25%), so expect regens. Reference images set
aspect ratio far more reliably than text alone. Instruction-based *removal* is an unreliable edit
category (NeIn) — so the primary variant never asks Nano Banana to draw lines and then remove
them; it asks for clean art from the start.

---

## Primary variant — clean art, no lines drawn at all (recommended default)

```
I'm providing two images:
- Image 1: the concept reference. This defines the object's identity — materials, weathering,
  color palette, and style. Match it exactly across every panel below.
- Image 2: a layout guide. It shows panel boundaries and, in flat color, which face of the object
  each panel represents. Match its geometry, proportions, and camera angle per panel — but treat
  the guide's own grid lines, panel numbers, magenta borders, and flat color fills as layout
  instructions only. Do not draw any of that in your output. Every panel should contain finished,
  fully rendered art, not a colored block and not a line drawing.

Panel meanings (by the guide's color coding):
- Red panel(s) = the object's TOP surface, seen from directly above.
- Gray panel(s) = the NORTH/back face.
- Green panel(s) = the SOUTH/front face — the side that faces the player.
- Blue panel(s) = the WEST end cap.
- Purple panel(s) = the EAST end cap.
- The isometric panels (labeled NW/NE/SW/SE) each combine the top surface with one long face and
  one end cap, at a 26.57-degree dimetric camera angle — match this exact angle in every isometric
  panel, do not flatten it and do not use a steeper/shallower angle between panels.
- The bottom-right panel is a caption/legend cell in the guide, not part of the object — leave it
  as plain, simple background in your output. Do not add text, objects, or a border there.

Render the object in the same illustrated, high-contrast dark-fantasy style as the concept image —
not photorealistic, not a 3D render. Keep proportions and silhouette faithful to the guide's
geometry in every panel — same wall thickness, same height, same number of visible construction
units — do not reinterpret or simplify the structure.

Output aspect ratio must match Image 2 exactly.

Do not add any text, watermark-looking element, sticker border, decorative frame, ground plane,
characters, or props anywhere in the output.
```

---

## Variant B — bake lines, then clean up (fallback only, if the primary variant leaves visible guide artifacts)

Only use this if the primary variant's "don't draw the lines" instruction doesn't fully work in
practice. If a two-pass edit is needed, phrase the second pass as a **positive reconstruction**,
never as a removal/negation instruction — research (NeIn) found negation wording
("remove X") is the specific case models most often botch, sometimes substituting an unwanted
artifact instead of a clean deletion.

Pass 1: same as the primary variant's prompt above, but drop the "do not draw... lines" instruction
(let the grid/labels bake into the output alongside the art).

Pass 2 (do NOT say "remove the lines"):
```
Re-render this exact image with every surface as one continuous, seamless material — no dividers,
no borders, no panel seams, no labels. Keep every material, color, weathering detail, and camera
angle in each panel pixel-for-pixel identical to what's there now. Only the seams/dividers/labels
change; nothing else does.
```

---

## Variant C — guide only, no concept image (control, for benchmarking)

Same as the primary variant, but omit Image 1 entirely and replace the identity paragraph with a
plain text material/style description (whatever's in the concept image's own generation prompt). This
isolates whether the concept image actually improves cross-panel consistency over guide+text alone —
run this alongside the primary variant during the S0-E4 benchmark, don't assume the concept image helps
without checking.

---

## Door: open variant (identity consistency across two separate generations)

This is the hardest of the three S0 test cases — it's structurally the one thing the literature
review found no direct precedent for (hard region boundaries + identity consistency held across
two *separately generated* images). Treat it as the test that tells us whether this pipeline can
handle stateful assets at all, not just a third example.

Reuse the door's **closed** concept image as Image 1 (never generate a separate "open" concept image — that
would let the model invent a new identity instead of proving it can hold one). Guide image is the
same door asset's guide, generated fresh at whatever W×H×D the open state needs (an open door
guide may need different visible geometry — e.g. the door leaf swung into the wall thickness or
against the frame — decide the actual target geometry before generating that guide).

Add this to the primary variant's prompt, right after the identity paragraph:

```
The object shown in Image 1 is the same door in its closed state. Render it here in its OPEN
state instead: same frame, same door leaf material/color/ironwork/weathering, same wall stone
around it — only the door leaf's position changes, swung open. Do not change the stone material,
the door's material, its ironwork, or its proportions from Image 1 — only its open/closed state.
```

Run the closed-door grid and the open-door grid as two separate S0-E4 benchmark entries, and
compare them directly against each other (not just each against its own guide) — material/color
drift between the two is the actual failure mode being tested here.

---

## Test matrix (S0-E4)

| Asset | Concept image | Guide layout | Notes |
|---|---|---|---|
| Wall | `wall_concept.png` | `6cell` (default) | Baseline case — no identity-across-generations risk |
| Door — closed | `door_concept.png` | `6cell` | |
| Door — open | `door_concept.png` (reused) | `6cell`, regenerated for open-state geometry | Hardest case — see above |

Run each asset through all 3 prompt variants (primary / B-fallback / C-control) at least once
before picking a winner — per the "5 prompts vs. 1" discussion, we don't yet know which wins.
