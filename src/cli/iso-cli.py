"""iso-cli — isoroll content pipeline CLI. Run with -h for usage."""

import sys

from blender_commands import blender_ipadapter, blender_stylize
from gen_commands import gen_character, ipadapter_ref, style_concept
from image_commands import detail_image, face_restore

HELP = """
iso-cli — isoroll content pipeline

Commands:
  gen-character <prompt>      txt2img character generation
    --profile  fast|balanced|quality  (default: balanced)
    --out      <dir>                  copy result here

  style-concept <image_path>  img2img style pass on concept art
    --prompt   <text>                 style description (required)
    --denoise  <0.0-1.0>             style strength    (default: 0.55)
    --out      <dir>                  copy result here

  ipadapter-ref <image_path>  Path B — IP-Adapter identity lock from concept art
    --prompt   <text>                 character/style description (required)
    --weight   <0.0-1.0>             IP-Adapter strength         (default: 0.8)
    --out      <dir>                  copy result here

  blender-stylize <image_path>  Path A — ControlNet Tile stylization of Blender render
    --prompt   <text>                 asset description (required)
    --denoise  <0.0-1.0>             style strength    (default: 0.70)
    --out      <dir>                  copy result here

  blender-ipadapter <image_path>  Path A+B hybrid — IP-Adapter identity + ControlNet Tile structure
    --concept  <concept_img>          concept art as IP-Adapter reference (required)
    --prompt   <text>                 character description (required)
    --denoise  <0.0-1.0>             style strength    (default: 0.65)
    --weight   <0.0-1.0>             IP-Adapter weight (default: 0.6)
    --out      <dir>                  copy result here

  detail-image <image_path>    Pure upscale: 4xUltrasharp → target size, no SD, no pose drift
    --size     character|tile         output size preset (default: character = 1024x1536, tile = 1024x1024)
    --rembg                           also strip background (for Path B outputs)
    --out      <dir>                  copy result here

  face-restore <image_path>    Visible-face characters only: UltimateSDUpscale + CodeFormer
    --prompt   <text>                 generation prompt for SD context in tiles (required)
    --rembg                           also strip background
    --out      <dir>                  copy result here
  mv-tile | mv-scene | mv-restyle   multiview generation via guides + registration marks (each has -h)
  export-manifest --layout <file>  layout DSL + kit → scene manifest JSON (see -h for flags)
Examples:
  python iso-cli.py gen-character "dark fantasy rogue" --profile quality
  python iso-cli.py ipadapter-ref ../../assets/chars/rogue/concept/rogue_concept_clean.png \\
      --prompt "dark fantasy rogue, hooded, teal cloak, SE isometric view" \\
      --out ../../assets/chars/rogue/stances/neutral-idle
  python iso-cli.py detail-image ../../assets/chars/rogue/stances/neutral-idle/pathB_00002_SE.png \\
      --rembg --out ../../assets/chars/rogue/stances/neutral-idle
  python iso-cli.py blender-stylize ../../assets/chars/rogue/_renders/neutral-idle/frame_0001_SE.png \\
      --prompt "dark fantasy rogue, hooded assassin, teal cloak" \\
      --out ../../assets/chars/rogue/stances/neutral-idle
  python iso-cli.py blender-ipadapter ../../assets/chars/rogue/_renders/neutral-idle/frame_0001_SE.png \\
      --concept ../../assets/chars/rogue/concept/rogue_concept_v2.png \\
      --prompt "dark fantasy rogue, hooded assassin, teal-blue cloak, black leather armor, SE isometric view" \\
      --out ../../assets/chars/rogue/stances/neutral-idle
"""


def get_arg(args: list[str], flag: str, default: str | None = None) -> str | None:
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            return args[idx + 1]
    return default


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(HELP)
        return

    command = args[0]

    if command == "gen-character":
        if len(args) < 2:
            print("[FAIL] gen-character requires a prompt.")
            sys.exit(1)
        gen_character(
            prompt=args[1],
            profile_name=get_arg(args, "--profile", "balanced"),
            output_path=get_arg(args, "--out"),
        )

    elif command == "style-concept":
        if len(args) < 2:
            print("[FAIL] style-concept requires an image path.")
            sys.exit(1)
        prompt = get_arg(args, "--prompt")
        if not prompt:
            print("[FAIL] style-concept requires --prompt.")
            sys.exit(1)
        style_concept(
            input_image=args[1],
            prompt=prompt,
            denoise=float(get_arg(args, "--denoise", "0.55")),
            output_path=get_arg(args, "--out"),
        )

    elif command == "ipadapter-ref":
        if len(args) < 2:
            print("[FAIL] ipadapter-ref requires an image path.")
            sys.exit(1)
        prompt = get_arg(args, "--prompt")
        if not prompt:
            print("[FAIL] ipadapter-ref requires --prompt.")
            sys.exit(1)
        ipadapter_ref(
            input_image=args[1],
            prompt=prompt,
            weight=float(get_arg(args, "--weight", "0.6")),
            output_path=get_arg(args, "--out"),
        )

    elif command == "detail-image":
        if len(args) < 2:
            print("[FAIL] detail-image requires an image path.")
            sys.exit(1)
        detail_image(
            input_image=args[1],
            size=get_arg(args, "--size", "character"),
            run_rembg="--rembg" in args,
            output_path=get_arg(args, "--out"),
        )

    elif command == "face-restore":
        if len(args) < 2:
            print("[FAIL] face-restore requires an image path.")
            sys.exit(1)
        prompt = get_arg(args, "--prompt")
        if not prompt:
            print("[FAIL] face-restore requires --prompt.")
            sys.exit(1)
        face_restore(
            input_image=args[1],
            prompt=prompt,
            run_rembg="--rembg" in args,
            output_path=get_arg(args, "--out"),
        )

    elif command == "blender-stylize":
        if len(args) < 2:
            print("[FAIL] blender-stylize requires an image path.")
            sys.exit(1)
        prompt = get_arg(args, "--prompt")
        if not prompt:
            print("[FAIL] blender-stylize requires --prompt.")
            sys.exit(1)
        blender_stylize(
            input_image=args[1],
            prompt=prompt,
            denoise=float(get_arg(args, "--denoise", "0.70")),
            output_path=get_arg(args, "--out"),
        )

    elif command == "blender-ipadapter":
        if len(args) < 2:
            print("[FAIL] blender-ipadapter requires an image path.")
            sys.exit(1)
        concept = get_arg(args, "--concept")
        if not concept:
            print("[FAIL] blender-ipadapter requires --concept <concept_img>.")
            sys.exit(1)
        prompt = get_arg(args, "--prompt")
        if not prompt:
            print("[FAIL] blender-ipadapter requires --prompt.")
            sys.exit(1)
        blender_ipadapter(
            input_image=args[1],
            concept_image=concept,
            prompt=prompt,
            denoise=float(get_arg(args, "--denoise", "0.65")),
            weight=float(get_arg(args, "--weight", "0.6")),
            output_path=get_arg(args, "--out"),
        )

    elif command.startswith("mv-"):
        from multiview_commands import run_mv_command
        run_mv_command(command, args[1:])

    elif command == "export-manifest": from export_commands import run_export; run_export(args[1:])
    else:
        print(f"[FAIL] Unknown command: {command}")
        print(HELP)
        sys.exit(1)


if __name__ == "__main__":
    main()
