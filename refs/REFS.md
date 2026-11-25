# References
> Tier-1 capture: one line per ref. Promote to `<slug>.yaml` when a ref earns real study.

- [soundbox — Soundbox](https://lucassf.pages.dev/isoroll/soundbox) — [src: web:instagram.com reel DfBSFBwCikQ, gittrend.io; github:HamSanders/soundbox] Project advertises local audio generation and agent integration. Assessment: ../ROADMAP.md [soundbox].
- [spritefusion-normals — Sprite Fusion](https://lucassf.pages.dev/isoroll/sprite-normals) — [src: web:instagram.com reel Det3bCRPqpP, sprite.fusion; github:Hugo-Dz/spritefusion-sprite-normals] Candidate sprite-lighting tool; inferred normals are not verified geometry. Assessment: ../ROADMAP.md [spritefusion-normals].

## 3D-generation models
- [idol — Idol](https://lucassf.pages.dev/isoroll/idol) — [src: web:instagram.com reel DfOD1PGDhLt, aiwithbibek; github:speridlabs/idol-sdk] Single-image Gaussian-splat generation; inferred hidden surfaces remain unverified. Offline prop-view assessment: ../ROADMAP.md [idol].
- [Hunyuan3D 2.1](https://github.com/tencent-hunyuan/hunyuan3d-2.1) — image→3D generation
- [HunyuanWorld 1.0](https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0) — scene/world generation
- [HY-World 2.0](https://github.com/Tencent-Hunyuan/HY-World-2.0/tree/main) — world generation, v2
- [Scenario 3D OS](https://github.com/scenario-labs/skills) — [src: web:instagram.com via Partnerinai, botsgone.wild] Demo advertises 3D generation, rigging and expert tools; generation needs a Scenario account. [Additional capture](https://www.instagram.com/reel/DfsjQP3SWbi/). Assessment: [ROADMAP](../ROADMAP.md) [scenario-3d-os]; texpace stress test: ../../spacemantics/ROADMAP.md [scenario-texpace].
- [ludo-directional — Ludo Directional Sprites](https://ludo.ai/docs/directional-sprites) — [src: web:ludo.ai; instagram.com/ludo.ai] One 3D model supplies directional animation sheets; the [reel](https://www.instagram.com/reel/Dfr7j4KKtXJ/) claims six moves × eight directions. Rights, export and method assessment: [ROADMAP](../ROADMAP.md) [ludo-directional].

## Visual inspiration
- [bodam.sketch — 3D flower shop sketch (Feather 3D)](https://www.instagram.com/reel/DZNl9VJz7XO/) — target visual level/type for isoroll content
- [Caio Figueiredo — "Suburb Buildings" lowpoly](https://www.instagram.com/p/CZRzKTKKAOA/) — Blender geometry-nodes style ref for isoroll content
- [Miaugic TCG — transparent modular cards](https://www.instagram.com/reel/Daks3P5xQf-/) — layering power (character + items composition); consider for texpace/spacemantics
- [Craft RPGs](https://www.craftrpgs.com/) — plataforma SaaS de RPG com IA (sucessor do fables.gg), battle maps 2D em grade e diálogos VN; proprietário (sem repo no GitHub), não substitui nossa pipeline isométrica de assets — assessment task tracked in ROADMAP.md

## Prompt/skill packs for the NB lane
- [Banana Pro Director + Cinema World Builder](https://www.instagram.com/reel/Dax-38bjV8R/) — two Claude skills by "Joey": the first builds character sheets, outfit references, scene layouts and image prompts **explicitly tuned for nano banana** (our primary generator, see CONTEXT.md); the second turns those images into video prompts with camera/lens/shot-style baked in. The character-sheet + scene-layout half maps onto the kit-assembly pipeline; the video half does not apply. ⚠ DM-bait post — the skills are not linked, only named. Found via the reel's speech track, its caption says nothing

## Technique — tiles & lighting
- [vertex-paint — per-instance material blending](https://www.instagram.com/reel/DgInYB7xLL9/) — [src: web:instagram.com] Demo stores mortar, efflorescence and grime masks in placed-wall vertex colours to vary reused meshes/materials; assess offline-bake fit in [ROADMAP](../ROADMAP.md) [vertex-paint].
- [Pixel Art Lighter](https://www.moonfell-rpg.com/pixel-lighter) — [src: web:moonfell-rpg.com; instagram.com/moonfell_rpg] Editable normal maps and light masks with lighting preview; [reel](https://www.instagram.com/reel/Dfa3hBGvH9q/). Compare against geometry-derived maps in [ROADMAP](../ROADMAP.md) [spritefusion-normals].
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

## Tools — video, not sprites
- [CapCut, one recording into many cuts](https://www.instagram.com/reel/Ddboo3axo9t/) — [src: web:instagram.com] a
  creator claims every cut in the reel came from a **single** take, and points at a shared CapCut project. Lucas: *"será
  que o capcut pode ser útil pro isoroll?"* (INBOX 2026-09-18). It edits video, so it reaches devlog/promo and
  table-session capture and never the sprite pipeline — the frozen rule that anything which rotates passes through
  geometry rules the second use out by construction. Assessment task tracked in ROADMAP Backlog, mirrored in
  `brain/goals/rpg-isoroll.md` [capcut-um-take].

## Process — level/scene creation
- [diorama — procedural Three.js scenes](https://github.com/sloemo01/diorama) — [src: github:sloemo01/diorama; instagram.com] Palette, dither, ink, joint animation and per-entity frame checks; [reel](https://www.instagram.com/reel/DfEdYDOiIoq/). Offline assessment: [ROADMAP](../ROADMAP.md) [diorama]; runtime comparison: ../../isoroll-module/ROADMAP.md [isoroll-2].
- [Beakman Studios — level-creation process (Barrow and Blade)](https://www.instagram.com/reel/DXpDJCACt2V/) — how an indie roguelike settled its level-creation workflow; Lucas: "útil pro isoroll content" (INBOX 2026-07-23). Assessment task tracked in ROADMAP Backlog — extract anything transferable to the kit-assembly / scene-stitching pipeline.

- [Drift](https://www.instagram.com/reel/DeI3Zulji05/?utm_source=ig_web_copy_link) — [src: web:instagram.com, gittrend.io] desktop video-editor demonstration; author's claims to test. Assessment in code/isoroll-content/ROADMAP.md; full extraction in outputs/virada/inbox-2026-10-06-links.json.

- [Animater — Lunatic Dice](https://www.youtube.com/watch?v=miVmM-EMRm8) — [src: web:youtube.com] Text, captions and speech describe animated Foundry effects; visual extraction waived by Lucas. Check projection, elevation, occlusion and assets. Assessment: ../ROADMAP.md [animater].

- [Universal Modder — gittrend.io](https://www.instagram.com/reel/DeJdwzZiDQA/?utm_source=ig_web_copy_link) — [src: web:instagram.com] Demonstration names rehan-remade/universal-modder: discovery, asset production, live-game verification and reusable field notes; compare with our workflow before adoption. Assessment: ../ROADMAP.md [modder-patterns].

- [Object brush — Canvas of Kings / Might of Merchants](https://www.instagram.com/reel/DeHQ3vrKB26/?utm_source=ig_web_copy_link&stkn=NTc4MTIwNjQ2YQ==) — [src: web:instagram.com] Demonstration shows density, erase, auto-height, collision and grid controls; compare the experience with our frozen painter grammar. Assessment: ../ROADMAP.md [object-brush].

- [UniMate — theartificialintelligens](https://www.instagram.com/p/DeGM6u4AZ9r/?utm_source=ig_web_copy_link) — [src: web:instagram.com] Seven slides present “One Unified Model to Animate Diverse Skeletons”; availability, license, rig inputs and performance unverified; source notes difficult contact/foot grounding. Assessment: ../ROADMAP.md [unimate].

- [V] [Motion, anime.js and web UI candidates](https://motion.dev/) — [src: web:instagram.com] Browser animation; Bklit/Kokonut identities inferred, not sprite geometry; [capture](https://www.instagram.com/reel/DfGjKw7uAl7/); assessment: ../ROADMAP.md [web-motion].
- [C] [Hype-versus-reality carousel and official tool checks](https://help.blotato.com/start-with-an-ai-agent/llm/automations.md) — [src: web:instagram.com] Creator opinions; bars are estimates, not printed scores or benchmarks; [capture](https://www.instagram.com/p/DeZjFVZALGO/); assessment: ../ROADMAP.md [rated-tools].
- [C] [Anatomy isometric animation](https://github.com/wheresryan22/anatomy) — [src: web:instagram.com] Browser isometric animation; checker still owns geometric truth; [capture](https://www.instagram.com/reel/Del82x1DVA1/); assessment: ../ROADMAP.md [anatomy].
- [C] [Workload-specific GPU throughput](https://github.com/Zagitta/GPU-UNLOCK) — [src: web:instagram.com] Workload-specific matrix result; no universal or RTX3050 speedup established; [capture](https://www.instagram.com/reel/DfAy1NHseqU/); assessment: ../ROADMAP.md [gpu-unlock].
- [V] [AFK Journey environmental animation](https://www.instagram.com/p/DeTHW7JAVjj/) — [src: web:instagram.com] Environmental animation inspiration; sampled frames do not verify loops; assessment: ../ROADMAP.md [isoroll-environment-life].
- [PixelFX](https://github.com/patch-gg/pixelfx) — [src: web:instagram.com reel DfW9S0wjlTI via gittrend.io] 244 procedural pixel art VFX/animations in JS/canvas with acting/timing and spritesheet exporter; assess acting state vocabulary and skill — assessment in ../ROADMAP.md [pixelfx-sheets].
- [NVIDIA MotionBricks](https://github.com/NVIDIA/MotionBricks) — [src: web:instagram.com post DfQfOlqjPXD via theaifield] open-source real-time 3D character animation framework; assess transferability for character rigging and animation preview — assessment in ../ROADMAP.md [nvidia-motionbricks].
- [Qwen-Image-2.1-Turbo-GGUF](https://huggingface.co/AtomicChat/Qwen-Image-2.1-Turbo-Uncensored-GGUF) — [src: web:instagram.com reel Debla6vTCkU via nedz_reclassified] text encoder quantizado GGUF (3.3-8.7GB) para geração rápida em GPU local; requer pipeline Turbo e validação de nós ComfyUI — assessment em ../ROADMAP.md [qwen-turbo-comfy].
- [T3-Video](https://lucassf.pages.dev/wos/t3-video) — Instagram/simplifyinai: native 4K research; paper speedups do not establish local hardware feasibility; [post](https://lucassf.pages.dev/wos/t3-video-post); task: ../ROADMAP.md [t3-video].
- [Undershine lighting](https://lucassf.pages.dev/isoroll/undershine-light-post) — Second per-pixel map (wall, depth) so a fire lights each wall. [spritefusion-normals].
- [Brush-shader snowboard](https://lucassf.pages.dev/isoroll/brush-snowboard-post) — three.js painterly shader; reproduce in the offline bake. [style-tests].
- [Low-poly as pixel art](https://lucassf.pages.dev/isoroll/lowpoly-pixel-post) — 32x32 textures, 360 px render, upscaled. [style-tests].
