# Phase 1 (tiles) — Concept View Prompt

**Goal:** One approved single-view image per asset = the identity/material anchor for every
multiview grid call that follows (see `tile_multiview_prompt.md`). This is step 1 of the S0
pipeline (SPECS.md → Chosen Pipeline → Tiles).
**Output:** Save the approved image as `tiles/{name}/{name}_concept.png`.

---

## How to use

Open Nano Banana (Gemini app or AI Studio). Start a new conversation, no reference image yet.
Paste the starter message below, fill in the asset description, send.
Iterate in the same conversation ("make the stone darker", "less ornate, more weathered") until
the silhouette and material read is right. Download the approved image — that's the concept.

Camera is fixed for every asset: **SE-facing, 26.57° dimetric isometric** (2:1 diamond ratio) —
matches the module's camera and the multiview guide's own projection, so the concept image isn't
fighting the grid call later on a different angle.

---

## Starter message (copy-paste, fill in the bracket)

```
Create a single game-asset illustration for a dark-fantasy dungeon crawler, in the illustrated,
graphic style of Hades by Supergiant Games — not photorealistic, not a 3D render.

Asset: [DESCRIBE THE WALL/DOOR/PROP HERE]

Camera: isometric dimetric view, 26.57 degree elevation (2:1 diamond ratio — NOT true isometric,
NOT a straight-on flat elevation), facing south-east, so both the front face and the right end of
the object are visible along with a sliver of the top surface.

Style requirements:
- Illustrated / painterly, high contrast, strong readable silhouette
- Deep shadows, rich stone/wood/metal tones — weathered, lived-in dungeon material, not clean/new
- Consistent material family with the rest of this dungeon's tileset: rough-cut gray stone blocks,
  dark aged wood, worn iron fittings
- Crisp, clean edges — no motion blur, no depth-of-field softness

Composition requirements:
- The full object only, nothing cropped, no surrounding room or floor
- Pure black background (#000000) — no ground plane, no cast shadow onto a floor, no environment
- No text, no watermark, no decorative border or frame
- No other objects, characters, or props in frame
```

---

## Wall example

```
Asset: A stone dungeon wall segment, roughly cut gray granite blocks in a running-bond pattern,
mortar lines visible, a few chipped/weathered edges and a patch of dark moss near the base.
No door, no window, no decoration — a plain load-bearing wall segment.
```

---

## Door (closed) example

```
Asset: A closed wooden dungeon door set into a stone wall segment — same rough gray granite
blocks as the surrounding wall, forming a plain arch-topped frame around the door. The door leaf
itself is dark aged oak with two horizontal iron reinforcing bands and iron rivets, a black iron
ring handle centered at mid-height, and a keyhole plate below it. Door is fully closed, flush
with its frame, no gap visible. Two iron strap hinges visible on the left edge of the door leaf.
```

---

## Tips

- The door's concept image is generated **closed** only. The open-door variant is never a separate
  concept image — it's produced later from this same concept image + guide, specifically to test
  whether Nano Banana can hold material/frame identity consistent across a state change (see
  `tile_multiview_prompt.md` → "Door: open variant"). Generating a second, independent concept
  image for the open state would defeat that test.
- Keep the wall and door concept images in the same conversation/session if possible (or
  explicitly say "same stone as the wall tile" in the door prompt) — improves cross-asset material
  consistency in the same tileset, though don't expect it to be perfect (see research: identity
  anchoring degrades across separate generations).
- If Nano Banana adds a ground plane or environment: ask "remove the background and any ground,
  pure black only, just the object."
- If the camera angle drifts (too flat, too steep, wrong facing): re-state the camera line exactly
  as given above — vague angle language ("isometric view") is not enough on its own.
