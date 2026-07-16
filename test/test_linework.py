"""Seams for /linework (S3): floor grammar per Lucas 2026-07-15 —
closed horizontal borders, open vertical edges (horizontal continuity),
shared courses across variants, door chirality."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "pipeline"))

import linework as lw
from linework_doors import door


def _lines(svg):
    return [tuple(float(m.group(i)) for i in range(1, 5)) for m in
            re.finditer(r'<line x1="([\d.-]+)" y1="([\d.-]+)" x2="([\d.-]+)" y2="([\d.-]+)"', svg)]


def _verticalish(l):
    return abs(l[2] - l[0]) < 6 and abs(l[3] - l[1]) > 4


def test_floor_has_closed_horizontal_borders():
    for seed in range(1, 9):
        ys = [(l[1], l[3]) for l in _lines(lw.floor_stone(seed)) if l[1] == l[3]]
        assert (0.0, 0.0) in ys and (float(lw.T), float(lw.T)) in ys, seed


def test_floor_vertical_edges_are_open_for_horizontal_continuity():
    for seed in range(1, 9):
        for l in filter(_verticalish, _lines(lw.floor_stone(seed))):
            assert lw.EDGE_MARGIN <= l[0] <= lw.T - lw.EDGE_MARGIN, (seed, l)


def test_floor_variants_share_global_courses():
    course_sets = []
    for seed in range(1, 9):
        ys = sorted({l[1] for l in _lines(lw.floor_stone(seed)) if l[1] == l[3]})
        course_sets.append(tuple(ys))
    assert len(set(course_sets)) == 1, "variants must share course heights to stitch"


def test_wall_tiling_edges_are_open_too():
    for svg in (lw.wall_wood_side(1), lw.wall_stone_side(1)):
        for l in filter(_verticalish, _lines(svg)):
            assert lw.EDGE_MARGIN <= l[0] <= lw.T - lw.EDGE_MARGIN, l


def test_single_door_hinges_left_knob_right():
    svg = door(1, 2)
    hinges = [float(m.group(1)) for m in re.finditer(r'<rect x="([\d.-]+)" y="[\d.-]+" width="6"', svg)]
    assert hinges and all(x < 10 for x in hinges), "hinges must sit on the LEFT edge (chirality)"
    knobs = [float(m.group(1)) for m in re.finditer(r'<circle cx="([\d.-]+)"', svg)]
    assert knobs and all(x > lw.T / 2 for x in knobs)


def test_build_set_renders_everything(tmp_path):
    names = lw.build_set(out_dir=str(tmp_path))
    assert len(names) == 46  # 38 + grass x4 + road_cobble x4
    for n in names:
        png = tmp_path / "png" / f"{n}.png"
        assert png.exists() and png.stat().st_size > 120, n
    assert (tmp_path / "textures.json").exists()


# ---- Lucas 2026-07-15 feedback seams ----

def _course_joints(svg):
    from collections import defaultdict
    by_course = defaultdict(list)
    for l in filter(_verticalish, _lines(svg)):
        by_course[(l[1], l[3])].append((l[0], l[2]))
    return by_course


def test_stone_joint_lines_never_cross():
    for maker, seeds in ((lw.floor_stone, range(1, 9)), (lw.wall_stone_side, range(1, 5))):
        for seed in seeds:
            for joints in _course_joints(maker(seed)).values():
                joints.sort()
                for (t1, b1), (t2, b2) in zip(joints, joints[1:]):
                    assert t2 > t1 and b2 > b1, "crossing joints"


def test_door_hardware_sits_at_five_feet():
    from linework_doors import _hardware_y
    assert _hardware_y(lw.T) < lw.T / 2            # h=1: upper part
    assert _hardware_y(2 * lw.T) == lw.T           # h=2: exact middle
    assert _hardware_y(3 * lw.T) == 2 * lw.T       # h=3: middle of first 10ft


def test_keyhole_has_triangle_occluded_by_circle():
    svg = door(1, 2)
    assert '<polygon' in svg, "keyhole triangle missing"
    tri = svg.index('<polygon')
    filled_circles = [m.start() for m in re.finditer(r'<circle[^>]*fill="#3a3a3a"', svg)]
    assert any(c > tri for c in filled_circles), "circle must be drawn over the triangle"


def test_window_frame_is_thin():
    m = re.search(r'<rect x="(\d+)" y="\1"', lw.window_1x1())
    assert m and int(m.group(1)) <= 6, "frame must be thin for side-by-side continuity"
