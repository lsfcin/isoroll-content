# Model Comparison — Evaluation

**Prompt:** `medieval rogue character, full body, standing pose, dark cloak, detailed face, highly detailed, clean simple dark background, isometric game asset style`  
**Workflow:** `character_quality.json` — 640x960, 36-step base + 12-step refine  
**Seed:** 42 (fixed for comparability)  
**Generation time:** ~26–28s each (GPU)

---

## Results

### dreamshaper_8 ★★★☆☆
Semi-realistic fantasy. Full body with staff, good proportions, clean cloak. Hands acceptable. Reliable and versatile but no standout feature for isometric work. Solid baseline.

### ghostmix_v20Bakedvae ★★★★☆
Similar to dreamshaper but slightly more polished — baked VAE gives better color consistency out of the box. Dual-blade pose, cleaner face. Best single-character quality of the realistic models.

### cetusMix_Whalefall2 ★★★★☆
Anime/semi-realistic hybrid. Cleaner, more graphic edges — good for sprite work where clean silhouettes matter. Consistent style across the full figure. Strong candidate for isoroll assets.

### toonyou_beta6 ★★★☆☆
Distinctly cartoon style. Warmer palette, exaggerated features, more casual game-art feel. Less photorealistic. Works well if the target aesthetic is colorful/casual rather than dark-fantasy.

### lyriel_v16 ★★★★★ — RECOMMENDED FOR ISOROLL
**Standout result.** Generated a spontaneous full character sheet — 8+ views of the same character (front, side, back, 3/4, close-ups) in a single image. This is exactly what the isoroll pipeline needs for multi-direction sprites. Character identity is consistent across views. This behavior may be exploitable by adding "character sheet, multiple views, turnaround" to the prompt explicitly.

---

## Recommendation

| use case | model |
|----------|-------|
| Multi-direction sprites (isoroll primary) | `lyriel_v16` |
| Best single-character quality | `ghostmix_v20Bakedvae` |
| Clean stylized sprites | `cetusMix_Whalefall2` |
| Casual/colorful aesthetic | `toonyou_beta6` |
| General fallback | `dreamshaper_8` |

## Next Steps

- Update isoroll workflows to use `lyriel_v16` as default checkpoint
- Test explicit character sheet prompting: add `"character sheet, multiple views, front back side, turnaround"` to prompt
- The `dreamshaperPixelart_v10` originally in workflows is not downloaded — `lyriel_v16` is the superior replacement
