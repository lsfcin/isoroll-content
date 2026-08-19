# isorolling Specs

This file documents the current code and source structure so future agents can modify the project
without rediscovering the same constraints.

<!-- routing:start -->
## Routing

| Shard | Description | Governs |
|-------|-------------|---------|
| [`SPECS-debt.md`](SPECS-debt.md) | What the runtime assumes, the pattern to prefer, and the debt not yet paid. | src/ |
| [`SPECS-layout.md`](SPECS-layout.md) | What lives where, which CLI entry points exist, and how src/cli/ is arranged. | src/ |
| [`SPECS-manifests.md`](SPECS-manifests.md) | The benchmark and asset manifests, and how a tile, variant and file are named. | benchmarks/, assets/ |
| [`SPECS-pipeline.md`](SPECS-pipeline.md) | The pipeline that was chosen, and the concept-art prompts fed into it. | src/pipeline/ |
| [`SPECS-render.md`](SPECS-render.md) | The Blender camera rig, the VRAM budget, and the style path it has to hold. | src/pipeline/ |
| [`SPECS-workflow.md`](SPECS-workflow.md) | What a ComfyUI workflow must expose, the render profiles, the detailer state. | src/cli/workflows/ |
<!-- routing:end -->
