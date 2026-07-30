#!/usr/bin/env python3
"""multiview_commands.py — mv-tile / mv-scene / mv-restyle verbs: render guide, fill prompt template, call the image provider or stage manual."""

import argparse
import subprocess
import sys
from pathlib import Path

import imagegen_client

_PIPELINE = Path(__file__).resolve().parents[1] / "pipeline"
_PROMPTS = _PIPELINE / "prompts"
_GUIDES_DIR = imagegen_client.OUTPUT_DIR / "guides"


def _run_pipeline(script, script_args):
    cmd = [sys.executable, str(_PIPELINE / script)] + script_args
    subprocess.run(cmd, cwd=_PIPELINE, check=True)


def _marks_args(args):
    extra = []
    if args.marks:
        extra = ["--marks", "--marks-mode", args.marks_mode,
                 "--back-mode", args.back_mode, "--opacity", str(args.opacity)]
    return extra


def _fill_prompt(template_name, description, style):
    template = (_PROMPTS / template_name).read_text(encoding="utf-8")
    return template.format(description=description, style=style)


def _dispatch(args, guide_path, prompt, stem):
    result = None
    if args.manual:
        result = imagegen_client.drop_manual(stem, prompt, guide_path)
    else:
        out_path = imagegen_client.OUTBOX / f"{stem}.png"
        result = imagegen_client.generate(prompt, out_path, guide_path=guide_path, alias=args.model)
    return result


def _add_common(parser):
    parser.add_argument("--desc", required=True, help="subject description for the prompt")
    parser.add_argument("--style", default="painterly isometric RPG asset")
    parser.add_argument("--model", choices=list(imagegen_client.MODELS), default="nb")
    parser.add_argument("--manual", action="store_true", help="stage guide+prompt for the web app instead of calling the API")
    parser.add_argument("--marks", action="store_true", help="apply registration marks to the guide")
    parser.add_argument("--marks-mode", choices=["anchored", "columns", "varied"], default="anchored")
    parser.add_argument("--back-mode", choices=["occluded", "faded"], default="occluded")
    parser.add_argument("--opacity", type=float, default=0.85)


def _cmd_tile(args):
    stem = f"tile_{args.name}"
    guide = _GUIDES_DIR / f"{stem}_guide.png"
    guide.parent.mkdir(parents=True, exist_ok=True)
    tile_args = ["--width", str(args.width), "--height", str(args.height),
                 "--depth", str(args.depth), "--layout", "6cell", "--output", str(guide)]
    _run_pipeline("make_tile_guide.py", tile_args)
    if args.marks:
        scheme = args.marks_mode if args.marks_mode in ("columns", "varied") else "columns"
        mark_args = ["--input", str(guide), "--output", str(guide), "--layout", "6cell",
                     "--scheme", scheme, "--back-mode", args.back_mode, "--opacity", str(args.opacity)]
        _run_pipeline("guide_marks.py", mark_args)
    prompt = _fill_prompt("multiview_tile_v2.txt", args.desc, args.style)
    return _dispatch(args, guide, prompt, stem)


def _cmd_scene(args):
    layout_path = Path(args.layout).resolve()
    stem = f"scene_{layout_path.stem}"
    guide = _GUIDES_DIR / f"{stem}_guide.png"
    guide.parent.mkdir(parents=True, exist_ok=True)
    scene_args = ["--layout", str(layout_path), "--output", str(guide), "--cell-px", str(args.cell_px)]
    if args.marks:
        scene_args = scene_args + _marks_args(args)
    _run_pipeline("scene_guide_sheet.py", scene_args)
    prompt = _fill_prompt("multiview_scene_v2.txt", args.desc, args.style)
    return _dispatch(args, guide, prompt, stem)


def _cmd_restyle(args):
    sheet = Path(args.input).resolve()
    stem = f"restyle_{sheet.stem}"
    prompt = _fill_prompt("multiview_tile_v2.txt", args.desc, args.style)
    return _dispatch(args, sheet, prompt, stem)


def run_mv_command(command, argv):
    """Entry used by iso-cli.py for any command starting with mv-."""
    parser = argparse.ArgumentParser(prog=f"iso-cli.py {command}")
    if command == "mv-tile":
        parser.add_argument("name", help="asset name (files become tile_<name>_*)")
        parser.add_argument("--width", type=int, required=True)
        parser.add_argument("--height", type=int, required=True)
        parser.add_argument("--depth", type=int, default=1)
        _add_common(parser)
        handler = _cmd_tile
    elif command == "mv-scene":
        parser.add_argument("layout", help="layout DSL file (see pipeline/layouts/)")
        parser.add_argument("--cell-px", type=int, default=640)
        _add_common(parser)
        handler = _cmd_scene
    elif command == "mv-restyle":
        parser.add_argument("input", help="existing multiview sheet to restyle")
        _add_common(parser)
        handler = _cmd_restyle
    else:
        raise SystemExit(f"[FAIL] unknown mv command: {command} (mv-tile | mv-scene | mv-restyle)")
    args = parser.parse_args(argv)
    handler(args)
