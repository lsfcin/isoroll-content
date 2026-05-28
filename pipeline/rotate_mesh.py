#!/usr/bin/env python3
"""[OBSOLETE-MESH]
rotate_mesh.py — Apply a Y-axis rotation to a mesh OBJ before Mixamo upload.

Mixamo auto-rigger expects: Y-up, character facing -Z.
TripoSR output: Y-up, character likely facing +X or -X → needs ±90° Y-axis rotation.

Usage:
    # Try -90° (most likely fix — turns +X-facing to -Z-facing):
    python content/pipeline/rotate_mesh.py content/chars/rogue/mesh/mesh.obj --angle -90

    # Try +90° if -90 faces wrong direction:
    python content/pipeline/rotate_mesh.py content/chars/rogue/mesh/mesh.obj --angle 90

    # Try 180° if character faces backward:
    python content/pipeline/rotate_mesh.py content/chars/rogue/mesh/mesh.obj --angle 180

Output: saves rotated mesh to mesh_rotY_{angle}.obj alongside the original.
Upload the rotated OBJ to Mixamo and verify the character faces -Z (toward camera in the front view).

After confirming the correct angle, add --mesh-rotate-y {angle} to triposr_mesh.py runs
so all future meshes are exported pre-rotated.
"""

import argparse
import numpy as np
import trimesh
from pathlib import Path


def rotate_y(mesh: trimesh.Trimesh, degrees: float) -> trimesh.Trimesh:
    angle = np.radians(degrees)
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    R = np.array([
        [ cos_a, 0, sin_a, 0],
        [     0, 1,     0, 0],
        [-sin_a, 0, cos_a, 0],
        [     0, 0,     0, 1],
    ], dtype=np.float64)
    mesh.apply_transform(R)
    return mesh


def rotate_axis(mesh: trimesh.Trimesh, degrees: float, axis: np.ndarray) -> trimesh.Trimesh:
    if degrees == 0.0:
        return mesh
    R = trimesh.transformations.rotation_matrix(np.radians(degrees), axis)
    mesh.apply_transform(R)
    return mesh


def main():
    parser = argparse.ArgumentParser(description="Rotate OBJ mesh for Mixamo compatibility")
    parser.add_argument("mesh", type=Path, help="Input OBJ path")
    parser.add_argument("--rotate-x", type=float, default=0.0,   help="Rotation around X axis (degrees)")
    parser.add_argument("--rotate-y", type=float, default=0.0,   help="Rotation around Y axis (degrees)")
    parser.add_argument("--rotate-z", type=float, default=0.0,   help="Rotation around Z axis (degrees)")
    parser.add_argument("--output",   type=Path,  default=None,   help="Output path (default: auto-named in same dir)")
    args = parser.parse_args()

    if not args.mesh.exists():
        print(f"Error: {args.mesh} not found")
        raise SystemExit(1)

    print(f"Loading {args.mesh} ...")
    mesh = trimesh.load(str(args.mesh), force="mesh")
    print(f"  Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}")
    print(f"  Bounds:   {mesh.bounds}")

    # Apply rotations in order: X → Y → Z
    for deg, axis, label in [
        (args.rotate_x, [1, 0, 0], "X"),
        (args.rotate_y, [0, 1, 0], "Y"),
        (args.rotate_z, [0, 0, 1], "Z"),
    ]:
        if deg != 0.0:
            print(f"  Rotating {deg:+.0f}° around {label}")
            mesh = rotate_axis(mesh, deg, axis)

    print(f"  Bounds after: {mesh.bounds}")

    if args.output is None:
        tag = f"rotX{int(args.rotate_x)}_Y{int(args.rotate_y)}_Z{int(args.rotate_z)}"
        args.output = args.mesh.parent / f"mesh_{tag}.obj"

    mesh.export(str(args.output))
    print(f"Saved: {args.output}")
    print("Upload to Mixamo — character should face forward (toward -Z) in front view.")


if __name__ == "__main__":
    main()
