# DSL v2 — Architecture Decision Memo
> Feeds the DSL-v2 implementation loop and the Painter MVP (P6.5/P7). Decisions here are the contract both twins (`layout_parse.py`, `src/assemble/layout-parse.ts`) implement.
> Companion: SCENE-CREATION.md (contract), PAINTER-UX.md (queued extensions this memo resolves).
> Status: 2026-07-10 — proposed by architecture consult, ☐ Lucas sign-off before the loop.

Format per section: **Decision · Rationale · Cost · v1 scope vs deferred.**

---

## 1. Cell encoding — MULTIPLE NAMED ALIGNED LAYER GRIDS

**Decision.** Reject 4-char-per-cell. Adopt named aligned layer grids: one required `layer kind:` grid (today's `# . D W ^>v< / \ R` vocabulary, 1 char/cell) plus optional aligned grids `layer h:`, `layer z:`, `layer side:`, `layer mat:`, each 1 char/cell, right-padded to the same rect. Omitted layer = per-cell default. Existing top-of-file directives (`name`, `wall_h`) stay as scalar defaults. A single-grid v1 file (no `layer` header) parses exactly as today — **backward compatible**.

```
name: crypt
layer kind:
######
#..D.#
#....#
######
layer z:
000000
011110
011110
000000
```

**Rationale.**
- *Hand-editability / diffability* — the decisive axis. The `kind` grid still *looks like the room*; walls remain visible lines you can trace. 4-char cells destroy this (every cell an opaque blob, columns no longer align to walls, opening a doorway means editing a 4-char token instead of typing `D`). Each attribute layer diffs independently: change one height, git shows one grid, one line. 4-char cells couple all four attributes into every token's diff.
- *Parser complexity, both twins* — smallest delta. Both parsers already split a header block (`layer kind:` is just today's directive syntax) from an aligned grid body via `_split_directives`/`splitDirectives`. v2 loops that same block reader per `layer X:` header, then zips grids by `(u,v)`. No fixed-field slicing, no width bookkeeping. 4-char cells force a second, different tokenizer (fixed-stride field extraction) that must reflow when a 5th attribute lands — a forward-compat trap.
- *Forward-compat* — new attribute = new optional layer, zero churn to existing files or the other layers. Roofs (`R` in kind), diagonals (`/ \` in kind), materials (`mat`) all slot in without a format bump. 4-char is width-locked.
- *Round-trip with painter* — the painter holds a per-cell record; it emits one grid per *populated* layer and omits the rest. The feel-rig already produces exactly this per-cell data (PAINTER-UX v3). Trivial serialization, stable diffs on re-export.
- *Rejected — sparse attribute directives* (`side: (2,1)=N …`). Good only for genuinely rare attributes; **fails on dense ones** — multi-story `z`/`h` touch most cells, and coordinate-addressed directives silently break when a row is inserted (hardcoded `(u,v)` drift). Keep directives for scalars/defaults only.

**Cost.** One extra parse pass + a per-layer alphabet (digits `0-9`, then `a-z` → 36 levels; enough for h/z/rise). Alignment invariant: layers right-pad to the kind rect; a ragged layer is a validation error. ~30 lines each twin, symmetric.

**v1:** `kind` (required) + `h`, `z`, `side`, `mat` (optional). **Deferred:** compression/RLE for huge maps; layer aliases.

---

## 2. Diagonal 45° walls — ACCEPTED, minimal v1

**Decision.** `/` and `\` in the `kind` grid = a single diagonal wall piece per cell (corner-to-corner). No merged diagonal runs, no openings on diagonals, no mitred junction art in v1.

**Rationale / representation.**
- *Massing* — a `/`/`\` cell emits one wall `Box` flagged `diag: "/"|"\\"` (footprint = the cell's corner-to-corner segment, not the square). Keep it one-cell; **do not** try parallelogram merges in v1 — the greedy run-merge in `_merged_wall_boxes` is axis-aligned and diagonals would need a whole second merge pass.
- *Kit pieces* — dimetric rotation = cell remapping, so a `/` under a 90° turn *becomes* `\`; SW's `/` art equals SE's `\` art. But within a single view both chiralities are visible at once, and mirroring is BANNED (chirality). So NB paints **2 new base silhouettes** (`wall_slash`, `wall_backslash`); the 4 dimetric views come free via remap. Cardinal regime adds its own 2 when P8 lands. Openings-on-diagonals would add `door_slash/backslash`, `window_slash/backslash` = **4 more** — deferred.
- *Module / walls-import* — free. Foundry wall segments take arbitrary endpoints; the exporter sets `ax,ay,bx,by` to the diagonal's two corners. No new WallDef field.
- *Depth-sort* — `depthZIndex = (row − col + elev)·SCALE` takes fractional row/col. Assign the diagonal piece the cell-center band (`row=v+0.5, col=u+0.5`). Honest caveat: the piece visually spans two bands, so a token straddling the diagonal can sort a hair off — acceptable for v1, refine only with evidence.
- *Autotile / junction* — where a diagonal meets an orthogonal wall, reuse the existing standalone **PILLAR** at the joint (already the junction fallback); no new corner art. Diagonal-to-diagonal just abuts.

**Cost.** 2 new NB silhouettes (dimetric) + a `diag` flag through massing→assemble→exporter + `pieceFor` cases. Bounded, no module wall-engine change.

**v1:** plain `wall_slash`/`wall_backslash`, pillar-covered junctions, cell-center depth. **Deferred:** openings on diagonals (4 pieces), merged diagonal runs, mitred junction art, sub-cell depth banding for diagonals.

---

## 3. Elevation semantics — pure transform, zero new art

**Decision.** Per-cell `z` (base elevation, `layer z:`, default 0) + `h` (height, `layer h:`, default `wall_h`). A cell's solid spans `[z, z+h]` in voxels. "Active elevation level E" is a **painter-only** view state; the DSL stores absolute per-cell `z`/`h`, not a level index.

**Rationale / data model.**
- *Massing* — `Box` gains `z0` (base); it already has `h`. Box spans `[z0, z0+h]`.
- *Manifest / WallDef* — maps onto **existing** fields: tile `baseElevation` + `WallDef.topOffset`/`bottomOffset` (grid units relative to baseElevation). `z→bottomOffset`, `z+h→topOffset`. **No new WallDef field for elevation** — confirmed against `wall-types.ts`.
- *Depth-sort* — already elevation-aware: `depthZIndex(row,col,elev)`. Elevated cells sort above ground automatically; multi-story falls out.
- *Fog / vision* — Wall Height ecosystem consumes top/bottom wall elevation, exactly what `topOffset`/`bottomOffset` feed. A wall at `z=3` only blocks the token band it occupies → multi-story vision correct by construction.
- *Painter grammar* — level stepper for active E; things grounded off-E render ~20% opacity (ghost); Shift+Alt+wheel writes per-cell `z` (already specced PAINTER-UX v3). E is UI state; export always writes absolute `z`.
- *CONTENT side* — kit pieces are **level-agnostic**: a wall is a wall at any z. Assembly offsets the sprite vertically by `z · voxel_px`. **No new NB art for elevation.** This is the honest headline: elevation is free on the art side; all cost is painter UX + carrying `z0` through massing/export.

**Cost.** `z0` field through massing→assemble→exporter; painter level stepper + ghost render pass. No art, no module wall-engine change.

**v1:** per-cell `z`/`h`, ghost off-level at ~20%, absolute-z export. **Deferred:** auto floor-fill between stacked levels; per-level fog isolation UI beyond what Wall Height gives free.

---

## Folded contract items

**Opening SIDE** (`layer side:`, char = `N/E/S/W`; diagonals reuse `/ \` sense). Massing carries it on `Opening`; exporter maps `side → WallDef.config.dir`. Mostly a vision/WallDef concern (one-way, secret) + which wall face shows the recess. **v1:** wire `side→dir`; the camera-facing recess uses today's `door_u`/`door_v` art. **Deferred:** distinct front/back recess silhouettes.

**Adjacent-opening MERGE.** The merge lives in **massing**: when merging a wall run, coalesce adjacent same-kind openings into one `Opening` with a `span` (offsets `[i..j]`) → one wide recess, no interior jamb. **Kit = COMPOSITED, not new art:** assemble emits `opening_end` + `opening_mid×(span−1)` + `opening_end`, reusing the straight/end autotile taxonomy (same trick as wall runs). **v1:** massing coalesces + assembly composites. **Deferred:** dedicated wide-recess pieces (only if compositing seams show).

**MATERIALS** (`layer mat:`, char = material id). Honest multiplication table: pieces = materials × surface-types. **Contain it — scope `mat` to FLOOR (and later ROOF) surfaces only, never walls.** So cost = M floor pieces (e.g. 5 materials → 5 floor tiles + autotile set), not M × every kit piece. **v1:** flat per-cell material fill, hard cut at boundaries. **Deferred:** material transition/blend edges (grass→road) — that is dual-grid autotile *per material pair*, genuinely multiplicative; do not open it without a concrete scene that needs it.

---

## Implementation order (for the DSL-v2 loop)
1. Layer-grid parser + validation (both twins, golden-diff parity) — the spine; unblocks everything.
2. Massing: `z0` field, `diag` flag, opening `span` coalescing.
3. Exporter: `z/h→topOffset/bottomOffset`, `side→dir`, diagonal endpoints, composited wide recess.
4. NB batch: 2 diagonal silhouettes; material floor tiles as scenes demand them.
5. Painter: level stepper + ghost, diagonal tool, `side` edge-pick (feel-rig already emits the data).

Steps 1–3 are content+module code (no art, cheap); step 4 is the only NB spend and it is small (2 pieces) until openings-on-diagonals or material blends are pulled from Deferred.
