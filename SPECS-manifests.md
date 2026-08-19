# Manifests and naming
> The benchmark and asset manifests, and how a tile, variant and file are named.
> governs: benchmarks/, assets/

## Benchmark Manifest

Each `benchmarks/{comparison-name}/` folder carries its own `manifest.json` —
a flat list, one entry per image, using this shape (actual convention as
practiced, not a single root index — see `benchmarks/README.md`):

```json
[
  {
    "model": "lyriel_v16.safetensors",
    "prompt": "medieval rogue character, full body, standing pose, ...",
    "seed": 77,
    "time_s": 90.1,
    "file": "benchmarks/hades-comparison/lyriel_v16.png"
  }
]
```

`prompt` is optional when every image in the folder shares one prompt (state
it once in the folder's own notes instead). `file` is repo-root-relative.

## Asset Manifest Schema

Each packed asset folder emits a `manifest.json` with this shape:

```json
{
  "id": "warrior-base",
  "type": "character",
  "layer": 2,
  "source_concept": "assets/chars/warrior/concept/warrior_concept_01.png",
  "source_workflow": "src/cli/workflows/character_quality.json",
  "checkpoint": "lyriel_v16.safetensors",
  "style_path": "A",
  "dimensions": { "w": 256, "h": 384 },
  "anchor": { "x": 0.5, "y": 0.9 },
  "bounds_3d": { "width": 1.0, "depth": 1.0, "height": 2.0 },
  "directions": ["SE", "E", "NE", "N", "NW", "W", "SW", "S", "TOP"],
  "animations": {
    "idle":         { "frames": 20, "fps": 12, "loop": true },
    "walk":         { "frames": 24, "fps": 12, "loop": true },
    "attack_melee": { "frames": 30, "fps": 12, "loop": false },
    "attack_ranged":{ "frames": 28, "fps": 12, "loop": false },
    "defend":       { "frames": 20, "fps": 12, "loop": false },
    "hurt":         { "frames": 15, "fps": 12, "loop": false },
    "cast":         { "frames": 30, "fps": 12, "loop": false },
    "crouch":       { "frames": 15, "fps": 12, "loop": false },
    "prone":        { "frames": 10, "fps": 12, "loop": false },
    "death":        { "frames": 40, "fps": 12, "loop": false },
    "fly_idle":     { "frames": 20, "fps": 12, "loop": true }
  },
  "equipment_slots": ["weapon_main", "weapon_off", "armor_chest", "armor_head"],
  "tags": ["humanoid", "warrior", "dark-fantasy"],
  "date": "2026-05-26",
  "notes": ""
}
```

---

## Tile Variant Naming Convention

Aspirational — not yet implemented. Current `assets/tiles/{name}/` holds a
flat `{name}_{facing}.png` set (see root `CONTEXT.md` Repository Shape); the
autotile bitmask variants below are a future v2 addition, not the current
shape.

```
assets/tiles/{terrain}/
  concept/
    ...
  atlas/
    floor_{terrain}_inner.png
    floor_{terrain}_edge_N.png      # open edge north (no neighbor to north)
    floor_{terrain}_edge_E.png
    floor_{terrain}_edge_S.png
    floor_{terrain}_edge_W.png
    floor_{terrain}_corner_NE.png   # convex open corner NE
    floor_{terrain}_corner_NW.png
    floor_{terrain}_corner_SE.png
    floor_{terrain}_corner_SW.png
    floor_{terrain}_corner_in_NE.png  # concave inner corner (v2)
    floor_{terrainA}_x_{terrainB}_edge_N.png  # cross-type transition
    wall_{type}_straight.png
    wall_{type}_corner_in.png       # concave wall corner
    wall_{type}_corner_out.png      # convex wall corner
    wall_{type}_end_N.png           # wall end cap
    wall_{type}_T.png               # T-junction
```

Seam strategy summary:
- **Same-type seams**: Blender UV repeating texture eliminates seams geometrically. Make-seamless
  filter for 2D-only tiles.
- **Cross-type transitions**: Pre-rendered blend tiles (8 per pair). Blender gradient UV mask
  between two terrain textures.
- **Wall/floor junctions**: Z-sorting via 3D bounds + transparent wall base alpha. No blend texture needed.
- **Autotile**: 4-bit bitmask → look up variant table. 9 variants per terrain covers ~90% layouts. See AP1-T in ROADMAP.

---

## File Naming Convention

```
assets/chars/{name}/
  concept/
    {name}_concept_{n:02d}.png          # external tool concept art (source of truth)
  sheet/
    tpose_front.png  tpose_back.png  front_full.png
    view_3q.png      equipment.png    palette.png
  _renders/
    {state}/
      frame_{n:04d}_{direction}.png         # raw Blender/intermediate render (RGBA)
      frame_{n:04d}_depth_{direction}.png   # depth pass (ControlNet)
  stances/
    {state}/
      frame_{n:04d}_{direction}.png         # final sprite after SD style pass + rembg
      {prefix}_{n:05d}_{direction}.png      # sprites from external tools (S4 path)
  equipment/{slot}/
    {state}/
      frame_{n:04d}_{direction}.png         # equipment overlay (alpha PNG)
  atlas/
    {name}_{direction}_{state}.png      # packed spritesheet per direction × state
    manifest.json
```

Direction labels: `SE`, `E`, `NE`, `N`, `NW`, `W`, `SW`, `S`, `TOP`

Animation state labels: `idle`, `walk`, `attack_melee`, `attack_ranged`, `defend`, `hurt`, `cast`,
`crouch`, `prone`, `death`, `fly_idle`

---
