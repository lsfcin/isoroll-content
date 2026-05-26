"""
preprocess.py — Step 1 of the art pipeline.

Takes concept art from an external tool (GPT Image, Nano Banana, MidJourney, etc.),
removes the background, resizes to target dimensions, and saves into the correct
outputs folder for the next pipeline step.

Usage:
    python preprocess.py --input path/to/image.png --type tile --name dungeon_floor
    python preprocess.py --input path/to/image.png --type character --name rogue

Output structure:
    content/outputs/tiles/{name}/concept/
        {name}_concept_raw.png      # original, untouched
        {name}_concept_clean.png    # background removed, resized

    content/outputs/characters/{name}/concept/
        {name}_concept_raw.png
        {name}_concept_clean.png

Requirements:
    pip install "rembg[gpu]" Pillow
    (CPU fallback: pip install rembg Pillow)
"""

import argparse
import shutil
import sys
from pathlib import Path


# ── Canonical output dimensions ───────────────────────────────────────────────
# These are "concept clean" sizes — intermediate before Blender + SD passes.
# Final atlas sizes defined in SPECS.md.

TARGET_SIZES = {
    "tile":      (512, 512),   # square — isometric tile
    "character": (512, 768),   # portrait — full body
    "item":      (512, 512),
    "effect":    (512, 512),
}

VALID_TYPES = list(TARGET_SIZES.keys())

# Plural folder name per type
FOLDER_NAMES = {
    "tile":      "tiles",
    "character": "characters",
    "item":      "items",
    "effect":    "effects",
}


def remove_background(input_path: Path) -> "Image.Image":
    try:
        from rembg import remove
        from PIL import Image
    except ImportError:
        print("ERROR: rembg or Pillow not installed.")
        print("  pip install \"rembg[gpu]\" Pillow")
        sys.exit(1)

    print(f"  Removing background from {input_path.name} ...")
    with open(input_path, "rb") as f:
        data = f.read()
    result_bytes = remove(data)

    from io import BytesIO
    img = Image.open(BytesIO(result_bytes)).convert("RGBA")
    return img


def resize_with_padding(img: "Image.Image", target_size: tuple[int, int]) -> "Image.Image":
    from PIL import Image

    img = img.copy()
    img.thumbnail(target_size, Image.LANCZOS)

    canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
    offset_x = (target_size[0] - img.width) // 2
    offset_y = (target_size[1] - img.height) // 2
    canvas.paste(img, (offset_x, offset_y), mask=img)
    return canvas


def find_content_root(start: Path) -> Path:
    current = start.resolve()
    for parent in [current, *current.parents]:
        if (parent / "content").is_dir() and (parent / "CONTEXT.md").is_file():
            return parent
    raise RuntimeError(
        f"Cannot find isoroll repo root from {start}. "
        "Run from inside the isoroll project directory."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preprocess external concept art for the isoroll pipeline."
    )
    parser.add_argument("--input", required=True, help="Path to input image from external tool.")
    parser.add_argument(
        "--type", required=True, choices=VALID_TYPES,
        help=f"Asset type: {', '.join(VALID_TYPES)}"
    )
    parser.add_argument("--name", required=True, help="Asset name slug (e.g. dungeon_floor, rogue).")
    parser.add_argument(
        "--no-resize", action="store_true",
        help="Skip resize — keep native resolution after background removal."
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    repo_root = find_content_root(Path.cwd())
    folder = FOLDER_NAMES[args.type]
    concept_dir = repo_root / "content" / "outputs" / folder / args.name / "concept"
    concept_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy raw original (never modify the source)
    raw_dest = concept_dir / f"{args.name}_concept_raw{input_path.suffix}"
    shutil.copy2(input_path, raw_dest)
    print(f"  Saved raw:   {raw_dest.relative_to(repo_root)}")

    # 2. Remove background
    clean_img = remove_background(input_path)

    # 3. Resize (unless --no-resize)
    if not args.no_resize:
        target = TARGET_SIZES[args.type]
        clean_img = resize_with_padding(clean_img, target)
        print(f"  Resized to:  {target[0]}×{target[1]} with padding")

    # 4. Save clean PNG (always PNG to preserve alpha)
    clean_dest = concept_dir / f"{args.name}_concept_clean.png"
    clean_img.save(clean_dest, format="PNG")
    print(f"  Saved clean: {clean_dest.relative_to(repo_root)}")

    print()
    print(f"Done. Next step: use {clean_dest.name} as input to ComfyUI img2img")
    print(f"  or as IP-Adapter reference for multi-view generation.")


if __name__ == "__main__":
    main()
