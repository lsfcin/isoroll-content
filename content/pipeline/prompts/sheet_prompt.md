# Phase 2 — Character Sheet Prompt

**Goal:** One-shot GPT session. Takes approved concept image + blank grid → 6-panel character sheet.
**Inputs to upload:** `sheet_template.png` + your approved concept image (from Phase 1)
**Output:** Save the generated sheet, then run `sheet_to_tpose.py` to extract panels.

---

## How to use

1. Open ChatGPT (GPT-4o with image generation)
2. Upload both files: `sheet_template.png` and your approved concept PNG
3. Paste the prompt below — no character description needed, the image IS the reference
4. If output misaligns: re-run, or use `--offset-x/y` in `sheet_to_tpose.py`

---

## Prompt (copy-paste as-is)

```
I am attaching two images:
1. A blank grid template — 3 columns × 2 rows = 6 labeled panels
2. My character concept — use this as the sole visual reference for all panels

Fill each labeled panel with the content below.
The character's face, body proportions, and style must be consistent across all panels.

TOP ROW (left to right):

Panel "T-POSE FRONT":
The character's body in a T-pose, front view. STRICT REQUIREMENTS:
- Wearing ONLY a plain light-gray (#C0C0C0) fitted bodysuit — NO armor, NO leather, NO hood,
  NO cape, NO accessories, NO weapons, NO boots. Just the bare body shape in a neutral suit.
- Arms extended straight out at shoulder height, palms facing down
- Feet shoulder-width apart, flat on the ground, toes forward
- Head fully visible — bare or close-fitting cap, face clearly shown, no shadow on face
- Light-gray suit must be clearly visible against the black background

Panel "T-POSE BACK":
Identical bodysuit T-pose, same pose requirements, seen from directly behind.
Light-gray suit. No accessories. Head from behind.

Panel "FRONT":
The character from the front, full detail — all armor, accessories, weapons, hood, cape exactly
as shown in the concept image. High fidelity to the reference.

BOTTOM ROW (left to right):

Panel "3/4 VIEW":
Same character, full detail, viewed from a 30–45° angle to the right, slight downward look.

Panel "EQUIPMENT":
All weapons, accessories, and distinctive items from the character's design, placed separately
on the black background. No character body. Generous space between items. Same art style.

Panel "PALETTE":
8 rectangular color swatches in a vertical column.
Small text label below each swatch (never overlapping it):
primary cloth, secondary cloth, metal, leather, skin, hair, accent/glow, shadow.

OUTPUT RULES (all panels):
- Pure black (#000000) background — true black, not dark gray
- Characters must NOT touch panel borders — generous black margin on all sides
- Character height fills ~85% of each panel's vertical space, centered
- NO text or labels overlapping any character body
- Palette labels appear below each swatch only
- Grid border lines must remain visible between panels
- Art style: illustrated, high contrast, graphic — consistent with the uploaded concept
```

---

## After generation

```bash
# Extract all panels (run from project root)
python content/pipeline/sheet_to_tpose.py path/to/sheet.png --character rogue

# Check crops with debug overlay
python content/pipeline/sheet_to_tpose.py path/to/sheet.png --character rogue --debug

# Fine-tune if misaligned
python content/pipeline/sheet_to_tpose.py path/to/sheet.png --character rogue --offset-x 15 --debug

# Feed T-pose front to Zero123 / visual culling pipeline
# content/chars/rogue/concept/rogue_tpose_front.png → ComfyUI Zero123 workflow → 8 views
# See ROADMAP S1 for Zero123 setup
```

---

## Known GPT limitations

- **Scale drift between panels:** ~5–10% variation. Fine for TripoSR (single-view). NOT fine for
  visual hull multi-view reconstruction — use Zero123 (stable_zero123.ckpt) for that instead.
- **Bodysuit in T-pose:** GPT may add seams, logos, or faint texture. Ignore unless it creates
  strong edges that confuse rembg. Light gray on black = rembg handles it cleanly.
- **Cape in T-pose panels:** if GPT adds it, re-run with "NO cape, bodysuit only" emphasized,
  or manually crop/mask the cape from the extracted panel.
