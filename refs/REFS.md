# References
> Tier-1 capture: one line per ref. Promote to `<slug>.yaml` when a ref earns real study.

## 3D-generation models
- [Hunyuan3D 2.1](https://github.com/tencent-hunyuan/hunyuan3d-2.1) — image→3D generation
- [HunyuanWorld 1.0](https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0) — scene/world generation
- [HY-World 2.0](https://github.com/Tencent-Hunyuan/HY-World-2.0/tree/main) — world generation, v2

## Visual inspiration
- [bodam.sketch — 3D flower shop sketch (Feather 3D)](https://www.instagram.com/reel/DZNl9VJz7XO/) — target visual level/type for isoroll content
- [Caio Figueiredo — "Suburb Buildings" lowpoly](https://www.instagram.com/p/CZRzKTKKAOA/) — Blender geometry-nodes style ref for isoroll content
- [Miaugic TCG — transparent modular cards](https://www.instagram.com/reel/Daks3P5xQf-/) — layering power (character + items composition); consider for texpace/spacemantics

## Prompt/skill packs for the NB lane
- [Banana Pro Director + Cinema World Builder](https://www.instagram.com/reel/Dax-38bjV8R/) — two Claude skills by "Joey": the first builds character sheets, outfit references, scene layouts and image prompts **explicitly tuned for nano banana** (our primary generator, see CONTEXT.md); the second turns those images into video prompts with camera/lens/shot-style baked in. The character-sheet + scene-layout half maps onto the kit-assembly pipeline; the video half does not apply. ⚠ DM-bait post — the skills are not linked, only named. Found via the reel's speech track, its caption says nothing

## Technique — tiles & lighting
- [Beno Raistrick — seamlessly tileable painted textures](https://www.instagram.com/reel/Daz5qSRMvV-/) — how to make hand-painted textures tile without seams (krita/blender/unreal). Directly on the P5 kit-paint problem: NB paints tile-sized pieces and tileability is the failure mode. Author says a full tutorial is coming
- [normal maps on 2D sprites](https://www.instagram.com/reel/DZLABeVx3qk/) — flat pixel-art sprite + normal map = dynamic per-pixel lighting and moving shadows, no 3D geometry. Candidate for giving isoroll scenes real light without leaving 2D; Lucas flagged it as a possibility under consideration

## Technique — Wang / corner tiles (researched 2026-07-30; assessment in ROADMAP § Research finding)
- [Cohen, Shade, Hiller, Deussen — Wang Tiles for Image and Texture Generation](https://graphics.uni-konstanz.de/publikationen/Cohen2003WangTilesImage/index.html) (SIGGRAPH 2003) — the foundational one: a small set of edge-coloured tiles generates boundless non-periodic texture, tiled stochastically in O(1) per tile
- [Lagae & Dutré — An Alternative for Wang Tiles: Colored Edges versus Colored Corners](https://graphics.cs.kuleuven.be/publications/LD06AWTCECC/LD06AWTCECC_paper.pdf) (TOG 25(4), 2006) — **the variant that matters for us**: edge tiles leave diagonal neighbours unconstrained (the *corner problem*); corner tiles constrain all neighbours, halve texture memory, are easier to tile. Corner-based == what "dual-grid" is in game-dev vocabulary
- [Derouet-Jourdan, Salvati, Jonchier — Procedural Wang Tile Algorithm for Stochastic Wall Patterns](https://ar5iv.labs.arxiv.org/html/1706.03950) (arXiv 1706.03950; CGF 2019 as "Generating Stochastic Wall Patterns On-the-fly with Wang Tiles") — **our exact case**: a Wang tile set for stone/brick walls, placed by hash functions, boundless, with control over max line length and the "no cross / no long lines" constraints artists care about. Earlier companion: [A linear algorithm for Brick Wang tiling](https://ar5iv.labs.arxiv.org/html/1603.04292)
- [Lagae & Dutré — Non-periodic Tiling of Procedural Noise Functions](https://dl.acm.org/doi/10.1145/3233306) (2018) — same trick applied to noise, relevant if the bake goes procedural rather than graphcut
- [BorisTheBrave / cr31 mirror — Wang tiles, blob tileset, isometric-3d tiles](https://www.boristhebrave.com/permanent/24/06/cr31/stagecast/wang/intro.html) — the practical game-dev treatment; has a page drawing 2-corner tilesets in **isometric** style, plus the blob-47 set. Same author's [Constraint-Based Tile Generators](https://www.boristhebrave.com/2021/10/31/constraint-based-tile-generators/) situates Wang vs WFC
- Implementations worth reading before writing our own: [nothings/stb `stb_herringbone_wang_tile.h`](https://github.com/nothings/stb/blob/master/stb_herringbone_wang_tile.h) (self-contained C, herringbone Wang map generator), [Wangscape](https://github.com/Wangscape/Wangscape) (corner-based terrain-transition tileset generator), [IJDykeman/wangTiles](https://github.com/IJDykeman/wangTiles) (procedural infinite world)

## Tools — tileset generation
- [PixelLab — Create Tileset](https://www.pixellab.ai/docs/tools/create-tileset) (Lucas 2026-07-30) — commercial tileset generator; exports **Wang tileset, dual-grid 15-tileset, 3x3**. Its structure vocabulary (inner/outer description, transition size 0.25/0.5/1 tile, tileset adherence) is a useful design reference for our painter grammar and arm A′. Also ships [Create isometric tile](https://www.pixellab.ai/docs/tools/create-isometric-tile) and an 8-directional sprite/rotate lane — pixel-art scale (16/32px), so off-target for our look, and generated rotation collides with the frozen "rotation passes through geometry" rule
- [PixelLab — tileset tutorial (YouTube)](https://www.youtube.com/watch?v=q9z2Vhpz-Z8) (Lucas 2026-07-30) — walkthrough of the same tool: tileset explanation, reference tiles, export, import into Godot, then `extend map` to build a house. Watch the 0:30–4:00 "tileset explanation" segment for how a shipping tool frames main/transition/lower tiles
- [Sprite Sheet Creator](https://github.com/blendi-remade/sprite-sheet-creator) ([post](https://www.instagram.com/reel/DbUJiTmiIRA/), Lucas 2026-07-31: *"tenho que olhar isso!"*) — [src: web:instagram.com] open-source, prompt→2D pixel sprite sheets, with an **isometric RPG mode** alongside side-scroller: walk/attack/idle animations, parallax backgrounds, top-down world maps. Same tension as PixelLab — pixel-art scale is off-target for our look, and prompt-generated views collide with the frozen "anything that rotates passes through geometry" rule — so the value is in its **sheet layout and animation-state vocabulary**, not its pixels. Assessment task tracked in ROADMAP Backlog

## Process — level/scene creation
- [Beakman Studios — level-creation process (Barrow and Blade)](https://www.instagram.com/reel/DXpDJCACt2V/) — how an indie roguelike settled its level-creation workflow; Lucas: "útil pro isoroll content" (INBOX 2026-07-23). Assessment task tracked in ROADMAP Backlog — extract anything transferable to the kit-assembly / scene-stitching pipeline.
