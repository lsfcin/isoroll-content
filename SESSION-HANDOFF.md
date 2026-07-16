# SESSION HANDOFF — scene-creation program (Fable session ended 2026-07-16, texture-set day)

## Where we are
Content-first plan S1-S8 live in `ROADMAP-content-gen.md` § "Plano refinado" (canonical).
Standing rules: passo-a-passo (cada spawn = go do Lucas), eyeball gate em todo passo com
imagem (board artifact), geometria por código (`core/skills/iso-visual.md`).

- **S3 DONE (initial set)**: 50 linework textures em `assets/textures/` (svg+png+
  textures.json), gerador `src/pipeline/linework{,_doors,_extra}.py`, 3 rodadas de
  feedback do Lucas aplicadas. Suite 93/93. Tip: `75085e0`, branch `loop/anchored-kit-marks`.
- **S1 PARKED**: marks devem ser TEXTURA warpada por homografia (não camada própria);
  loop trail em `.loop/anchored-kit-marks/` congelado em arch-PASS.
- **NEXT = S4**: arm_a real por homografia (textura → quad projetado por face; mapping
  face kind+mat → texture id via `textures.json`) + **S4t dry-run sem NB** (sheet
  esquemático como fake output → crop → assembly). Executor: /loops chain nova.
- Depois: S5 NB round 1 (Lucas, 3 arms), S6 vocabulário+costura+máscaras de transição,
  S7 painter close (+P7b: 9 views, bug B28 luz-gira-com-câmera → module KNOWN-BUGS),
  S8 normal maps GO (opção do module).

## State
- content: `loop/anchored-kit-marks@75085e0`, tree clean, pytest 93/93.
- module: `loop/painter-mvp-1@3987979` (painter 4b verde 127/127, WIP commit; facade
  debt T8 documentado no commit), 16 dirty = floor-fog-spike fence + KNOWN-BUGS B28 novo.
- Lucas ainda deve: 5 PNGs de textura dele → `assets/textures/` (entram via UV-map JSON
  no S4); veredito estético do set no board.
- Boards: status https://claude.ai/code/artifact/b75e182b-19cb-4e97-896d-f76126a85edb ·
  plano https://claude.ai/code/artifact/b1ff5a4a-58a8-4890-a549-477f787980b5

## Read first (next session)
1. `ROADMAP-content-gen.md` § Plano refinado (S4 row) + `design/RENDER-RESTYLE-MEMO.md`
2. `assets/textures/textures.json` + `src/pipeline/stage_kit_modules.py` (arm_a atual)
3. `core/flows/loop-engineering.md` (orquestração) + `core/skills/iso-visual.md`
