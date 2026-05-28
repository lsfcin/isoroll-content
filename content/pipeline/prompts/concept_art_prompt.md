# Phase 1 — Concept Art Prompt

**Goal:** Iterate with ChatGPT until character visual is approved. One approved image = one Phase 2 session.
**Output:** Save final image as `content/chars/{name}/concept/{name}_concept_clean.png`

---

## How to use

Open ChatGPT (GPT-4o with image generation). Start a new conversation.
Paste the **starter message** below, fill in your character description, send.
Keep iterating ("try heavier cloak", "make the weapon more visible", "darker tones") until satisfied.
When done, download the image. That's your concept reference.

---

## Starter message (copy-paste, fill in the bracket)

```
Create a full-body character illustration for a dark fantasy action-RPG in the style of Hades by Supergiant Games.

Character: [DESCRIBE YOUR CHARACTER HERE]

Style requirements:
- Illustrated, graphic, high contrast — not photorealistic
- Strong readable silhouette — the shape alone should communicate the character type
- Heroic proportions (7–8 heads tall)
- Deep shadows, rich jewel tones, accent highlights (gold, crimson, or teal glow work well)
- Reference aesthetic: Zagreus, Megaera, Thanatos from Hades

Composition requirements:
- Full body from head to feet, nothing cropped
- Pure black background (#000000) — no ground, no environment, no drop shadow
- Character centered horizontally, front-facing (slight 3/4 angle acceptable if face is visible)
- No text, no watermarks, no decorative frames
- High contrast silhouette against black — character edges must be crisp
```

---

## Rogue example (fill-in for the rogue character)

```
Character: A hooded rogue-assassin. Dark leather armor layered over cloth wrappings.
Short asymmetric cape over one shoulder. Carries two short daggers worn at the hips.
Teal bioluminescent rune glow on the forearm bracers and dagger pommels.
Angular face, partially shadowed by the hood. Agile, lean build — not bulky.
Color palette: charcoal leather, midnight blue cloth, teal glow accents, dull gold hardware.
```

---

## Tips

- Squint at the image — if the silhouette reads clearly, it will work for 3D
- Cape/cloak that clearly separates from the body silhouette is better for TripoSR mesh
- If GPT adds background or ground plane: ask "remove the background, pure black only"
- Identity anchor: once you have a good concept, keep that image — it becomes the sheet reference
