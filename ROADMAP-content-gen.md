# ROADMAP — content-gen: F1 procedural + espinha multiview
> Sub-roadmap de [ROADMAP.md](ROADMAP.md). Sessão Fable 2026-07-07. Status vivo — atualizar a cada loop/merge.

## Decisão de execução (inline × /loops)

Build híbrido: **Fable inline** construiu o que tinha decisão arquitetural viva — compilador layout→massing, renderer de guia de cena, marks parametrizados p/ A/B, prompt NB v2, client NB — porque o design do instrumento (guia) e a iteração de prompt exigem julgamento contínuo. **Todo o resto é mecânico após as seams existirem** e ruteia via loop-engineering (`/loops`, executores pinados loop-low/medium): reparo de ambiente utilitário, testes+hardening do postproc, exporters, lane F2, restyle F4, tasks do isoroll-module. opencode/modelos externos: **proibidos em código do repo** (precedente kimi 2026-07: stub corrompido, zero código mergeado); permitidos p/ notebooks Colab e experimentos descartáveis. A/Bs NB: usuário executa (web/API) e eyeballa; modelos baratos processam resultados.

## Estado (2026-07-07)

- [x] Gitflow: `develop` + `feature/f1-procedural-spine` (content); module já tem `develop`.
- [x] F1 core inline: `layout_parse.py` + `layout_massing.py` + `guide_marks.py` + `scene_guide_render.py` + `scene_guide_sheet.py` — l-room renderizado nas 4 rotações + plan + marks (painter por célula; runs mesclados ficam pro manifest).
- [x] Smoke test chave Gemini: key VÁLIDA, lista `gemini-2.5-flash-image`/`3.1-flash-image`/`3.1-flash-lite-image`; geração 429 (quota free do DIA esgotada em todos os buckets — reseta meia-noite Pacific ≈ 4h Recife). Test-to-kill pronto pra disparar pós-reset ou via web app.
- [x] **Test-to-kill F1 EXECUTADO (2026-07-08, web app): single-pass de cena MORTA.** Estilo PASS (pedra/musgo/tochas, 5 painéis coesos). Geometria FAIL: footprint divergente entre painéis (NE nem era a mesma sala), NB releu símbolos flutuantes como legenda/callouts (desenhou círculos ciano como anotação + caption alucinada "corrected footprint"). Confirmado: NB segura geometria em escala de TILE, não de CENA.
- [x] **Pivô (regra pré-registrada): F1 = KIT ASSEMBLY (tinyglade real).** NB pinta só kit sheets por peça (tarefa tile-sized, regime validado); `scene_assemble.py` monta a cena deterministicamente do layout — geometria e paredes exatas por construção, zero NB por cena. Implementado: `kit_render.py` (6 peças camera-fixed + manifest de alinhamento; rotação = remapeamento de célula, nunca do sprite), `scene_assemble.py` (painter per-cell), demo l-room 4 views em `output/assembled/` ✓.
- [x] Guia v2 (ajustes do usuário 2026-07-08): wall_h=3 (voxel 1.5m → 4.5m), porta 1×2×0 vazada exata, janela 1×1×0 (z 1..2), **marks ancorados** (`scene_anchors.py`: âncoras 3D estáveis — cantos/aberturas/runs — projetadas por view, mesmo id = mesmo símbolo em toda view; modo default do `mv-scene`).
- [ ] Próximo experimento NB (tile-sized, ~6-12 chamadas): pintar o kit — braço A: `mv-tile` por peça; braço B: kit-sheet único (6 peças numa imagem = 1 estilo garantido). Depois: assembly com sprites pintados + rembg + normalização pela silhueta do guia.
- [ ] Leftover técnico: `getdata` deprecado (Pillow 14) em `sheet_grid.py:63`, `sheet_qc.py:34`, `test/test_sheet_grid.py` — padaria futura (`residue_count` já corrigido via histogram).
- [x] Loop `env-utility-repair` (padaria): SHIPPED `feature/env-utility-repair` (ead36e2) — symlinks resolvem, 4xUltrasharp 64MB baixado, SD ckpts fora de escopo. Verificado no filesystem.
- [x] Loop `postproc-tests` (standard): SHIPPED `feature/postproc-tests` (331d184→f2a9cbe, empilhada em feature/f1-procedural-spine) — `src/cli/sheet_qc.py` (IoU silhueta + resíduo), pytest 8/8 verde, e2e guia→marks→output-sujo→split+QC ok. Roteamento auditado: opus×2, sonnet×3, haiku×2, zero max-tier.
- [ ] Merges em develop: aguardando eyeball do usuário (gitflow) — ordem: f1-procedural-spine → postproc-tests → env-utility-repair; tag `pre-<slug>` antes de cada merge

## Papéis de ferramenta (verificado web 2026-07)

NB (Gemini 2.5 Flash Image, free ~500/dia) = geração primária; NB2 (~20/dia) reserva. ComfyUI = **trilho utilitário só** (rembg, upscale 4xUltrasharp, SAM2 tiny/small, LaMa) — geração local SD1.5 deu artefatos horríveis p/ personagens e é arquiteturalmente errada p/ viewpoint (ROADMAP.md S). Fallbacks se NB falhar: Hunyuan3D-2mini (5GB, fork 2GP p/ 6GB) / TripoSR (~6GB) p/ mesh; Qwen-Image-Edit GGUF Q2-Q4 / Flux Kontext Q4 (6GB, lento) p/ edit; Colab T4 16GB ~15-30h/sem + Kaggle 30h/sem p/ jobs grandes. WFC/grammar (CPU) p/ decoração procedural futura.

## Arquitetura — espinha de 4 camadas

Motor compartilhado: `tile_guide_render.py` (PIL, dimétrico 2:1 = 26.57°, faces grayscale TOP/LONG/CAP, linework magenta, banda quiral). Tile-única e cena usam as mesmas convenções → `sheet_grid.py` (magenta_mask/detect_grid/strip_linework) serve os dois.

1. **guide** (`src/pipeline/`)
   - `layout_parse.py`: DSL texto-grid → modelo. Chars: `#` parede, `.` piso, espaço vazio, `D` porta, `W` janela, `S` escada (sobe p/ N no v1). Diretivas `key: value` antes do grid (`name:`, `wall_h:` unidades, `cell:` px). Valida: porta/janela precisam estar num run de parede.
   - `layout_massing.py`: grid → caixas (u0,v0,l,d,h) com merge de runs de parede por eixo; aberturas viram recessos do run; escada = 4 degraus; piso = strips h=0.
   - `guide_marks.py`: registration marks como **pós-passe** sobre qualquer sheet de guia. Params A/B: scheme (colunas repetidas × variados), back_mode (occluded: símbolo só onde há fundo × faded-over: alpha sobre tudo), opacity, cor ciano `(0,255,255)` (key-out análogo ao magenta), densidade, seed.
   - `scene_guide_render.py`: massing → painel de cena por view (**rotação real** de coordenadas 0°/90°/180°/270° — mirror-trick da caixa única inverteria o layout), painter's sort por (u+v), faces TOP/LONG/CAP, recessos de portas/janelas, TOP = planta ortográfica; compõe sheet 6-cell (`NW|NE|TOP / SW|SE|caption`) com labels/caption idênticos ao `make_tile_guide.py`.
2. **nb** (`src/cli/`)
   - `imagegen_client.py`: Gemini API (`generateContent`, resposta inline b64) + ledger diário `output/gen-ledger.json` (quota 500/dia) + contrato de pastas p/ fallback manual: CLI salva `*_guide.png` + `*_prompt.txt` em `output/gen-inbox/`; usuário cola no web app e salva output com mesmo stem em `output/gen-outbox/`; postproc consome de lá igualzinho.
   - `multiview_commands.py`: verbos `mv-tile`, `mv-scene`, `mv-restyle` no `iso-cli.py`.
3. **post**: `sheet_grid.py` + `sheet_postproc.py` (split por linhas-guia) + **slice-by-construction** p/ cenas (posição de cada célula conhecida do layout — SAM desnecessário p/ geometria) + QC: resíduo de marks (contagem ciano+magenta), IoU de silhueta vs máscara do guia (alvo ≥0.9), consistência de material entre views (correlação de histograma), nota eyeball 1-5. Runs em `benchmarks/nb-ab/{run}/manifest.json`.
4. **export**: naming `{name}_{facing}.png` / `{name}_{stance}_{facing}.png` (SPECS.md) + manifest JSON por cena: tiles (`boundHeight`, `imageOffset`) + `WallDef[]` do layout (tileAnchor [0,1]², `door`/`sense`/`dir` — `isoroll-module/src/walls/wall-types.d.ts`).

Features → espinha: **F1** layout→massing→guia→NB→slice→manifest (paredes exatas por construção). **F3** = caso 1-tile (meio pronto). **F4** = restyle (sheet existente + marks + prompt de estilo). **F2** = SAM2+LaMa → refs por segmento → espinha. **F5** = matriz stances × espinha (pós module-token-facing). **6a/6b** (transições de animação, equipment swap): fora desta rodada; candidatos: interpolação de views + NB edit por camada — revisitar quando F5 shipar.

## Matriz A/B — guia v2 (registration marks)

| Var | A | B | Hipótese |
|---|---|---|---|
| V1 scheme | colunas de símbolo repetido | símbolos variados únicos por âncora | repetição = correspondência mais forte; variedade = menos vazamento pro output |
| V2 back_mode | occluded (símbolo só no fundo) | faded-over α=0.85 sobre parede | faded ajuda NB a "ver através"; occluded suja menos |
| V3 opacity | 0.85 | 0.60 | menor α = menos resíduo, correspondência ainda legível |
| V4 layout | 6cell | 9panel c/ transição SW→S→SE | sequência de rotação induz "girar" em vez de "flip" (E↔W swap observado) |
| V5 prompt | v2 estruturado (abaixo) | v1 atual | seções+negativos explícitos reduzem resíduo e flips |

Protocolo: 1 variável por rodada, 3 seeds/braço, métricas QC + eyeball; matar braço perdedor; ~6 rodadas ≈ 36 imagens ≪ 500/dia. Test-to-kill F1 antes de tudo: sala em L 6×5, 1 porta S, 1 janela E → guia 1 view → NB → aderência de paredes (IoU) ≥0.8 e estilo ok; falhou → densificar marks/chunk 2×2 salas; falhou → lane P-Kit (Blender paramétrico, reusa `blender_*` [OBSOLETE-MESH]).

## Prompt NB v2 (rascunho — braço A de V5)

```text
TASK: Repaint the schematic guide as a finished isometric game asset. Same object, every panel.

READ THE GUIDE (never draw guide elements):
- 3x2 grid of panels split by magenta lines; labels "1 NW", "2 NE", "3 TOP", "4 SW", "5 SE"; panel 6 = caption (ignore).
- All panels show the SAME object from different fixed cameras. 4->5 is the SAME object rotating on its base; nothing is mirrored.
- Grayscale faces encode light: light gray = top face, mid gray = long walls, dark gray = end caps. Keep this lighting.
- CYAN symbols are registration marks: the same symbol = the same physical spot across panels. Align features to them.
- Openings drawn as dark recesses are doors/windows: render them as real doors/windows at exactly those spots.

SUBJECT: {description}
STYLE: {style}; crisp silhouette; consistent palette and materials in ALL panels; neutral top-left daylight.

OUTPUT: same 3x2 grid, same panel geometry and scale, pure black background inside panels.
NEGATIVE: no cyan symbols, no magenta lines, no text or labels, no extra objects, no ground shadows, no perspective (dimetric only), no mirrored panels.
```

## Delegação /loops (todas `base: develop` no Carry; ver gitflow abaixo)

| slug | repo | tier | escopo | depende de |
|---|---|---|---|---|
| env-utility-repair | content | low (padaria) | consertar symlinks `~/ComfyUI/models/*` → destino real + baixar SÓ utilitários (rembg, 4xUltrasharp, SAM2 small, LaMa); SD ckpts NÃO | — |
| postproc-tests | content | medium | pytest p/ `sheet_grid`/`sheet_postproc`/QC novo + hardening do split | F1 core |
| export-manifest | content | medium | exporter naming+manifest (tiles+`WallDef[]`) validado contra `wall-types.d.ts` | F1 core |
| f2-segment-lane | content | medium | workflows SAM2+LaMa + verbo decompose | env-utility-repair |
| f4-restyle | content | medium | verbo restyle sobre a espinha (sheet existente → NB) | nb client |
| module-walls-import | module | medium | manifest → `createWallsFromDefs` (`wall-crud.ts`) | export-manifest |
| module-token-facing | module | medium | seleção de sprite 8-direções (placeholder `object-transform.ts`) | — |
| f5-token-stances | content | medium | matriz de stances × espinha | module-token-facing |

## Gitflow & recuperação (content e module)

`main` (estável, merge só pelo usuário) ← `develop` (integração) ← `feature/<slug>` (1 por loop/tarefa). Todo trabalho nasce em feature branch cortada de `develop`; Loop 6 pusha **sem merge**. Merge em develop só com verify verde + veredito + eyeball quando visual. Loop ruim = `git branch -D feature/<slug>` (develop intocada); trail `.loop/<slug>/` commitado na feature branch; force-push proibido; tag `pre-<slug>` antes de cada merge em develop.

## Verificação

`make verify-fast` verde; pytest verde quando existir; guias (tile v2 + cena) em `output/` p/ eyeball; test-to-kill com QC rodado e veredito registrado AQUI; manifest valida contra schema do módulo; fim-a-fim: tile v2 + cena F1 carregados no Foundry via flags. Hooks: arquivos ≤200 LOC, 1 responsabilidade, facade-gate, jscpd.
