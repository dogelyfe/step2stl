#!/usr/bin/env python3
"""
Simple STEP (.step/.stp) to STL (.stl) converter using FreeCAD's Python API.

Two modes:
1) Drop-folder mode (double-click friendly):
   - Place STEP files in `STEP-INPUT/` next to this script.
   - Double‑click a wrapper like `Step2Stl.command` (see repo) or run with FreeCADCmd.
   - Outputs to `STL-OUTPUT/` and moves processed STEP files into `STEP-INPUT/_processed/`.
   - Re-runs ignore files already in `_processed/`.

2) CLI mode:
   - freecadcmd step2stl.py /path/to/file.step -o /path/to/out
   - freecadcmd step2stl.py /path/to/folder -q medium

Notes:
- Requires FreeCAD Python modules (FreeCAD, Part, Mesh, MeshPart) available (e.g., via FreeCADCmd).
- STL is ASCII for broad compatibility.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Tuple
import shutil
import time
import math
import json


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert STEP to STL using FreeCAD")
    p.add_argument(
        "input",
        type=Path,
        nargs="?",
        help="Input .step/.stp file or directory to scan recursively. If omitted, uses STEP-INPUT/ next to the script and outputs to STL-OUTPUT/.",
    )
    p.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="Output directory (default in drop-folder mode: <script_dir>/STL-OUTPUT). Maintains filenames; mirrors subdirs when input is a folder.",
    )
    p.add_argument(
        "-q",
        "--quality",
        choices=["high", "medium", "low", "custom"],
        default="high",
        help="Mesh quality preset (default: high)",
    )
    # Orientation helpers
    p.add_argument("--source-up", choices=["x", "y", "z"], default=None, help="Source 'up' axis")
    p.add_argument("--target-up", choices=["x", "y", "z"], default=None, help="Target 'up' axis (default z)")
    p.add_argument("--rotate-x", type=float, default=0.0, help="Rotate degrees about X after up-mapping")
    p.add_argument("--rotate-y", type=float, default=0.0, help="Rotate degrees about Y after up-mapping")
    p.add_argument("--rotate-z", type=float, default=0.0, help="Rotate degrees about Z after up-mapping")
    p.add_argument(
        "--linear-deflection",
        type=float,
        default=None,
        help="Custom linear deflection in model units (smaller = finer)",
    )
    p.add_argument(
        "--angular-deflection",
        type=float,
        default=None,
        help="Custom angular deflection in degrees (smaller = finer)",
    )
    p.add_argument(
        "--relative",
        type=lambda s: str(s).lower() in {"1", "true", "yes", "y"},
        default=None,
        help="Use relative linear deflection (True/False). Default varies by preset.",
    )
    return p.parse_args(list(argv))


def resolve_mesh_params(ns: argparse.Namespace) -> Tuple[float, float, bool]:
    # Sensible defaults inspired by FreeCAD best practices
    presets = {
        "high": dict(linear=0.05, angular=10.0, relative=True),
        "medium": dict(linear=0.10, angular=15.0, relative=True),
        "low": dict(linear=0.25, angular=25.0, relative=True),
    }

    if ns.quality == "custom":
        if ns.linear_deflection is None or ns.angular_deflection is None or ns.relative is None:
            raise SystemExit(
                "For --quality custom, provide --linear-deflection, --angular-deflection, and --relative"
            )
        return float(ns.linear_deflection), float(ns.angular_deflection), bool(ns.relative)

    base = presets[ns.quality]
    linear = ns.linear_deflection if ns.linear_deflection is not None else base["linear"]
    angular = ns.angular_deflection if ns.angular_deflection is not None else base["angular"]
    relative = ns.relative if ns.relative is not None else base["relative"]
    return float(linear), float(angular), bool(relative)


def find_step_files(root: Path) -> Iterable[Path]:
    exts = {".step", ".stp"}
    if root.is_file() and root.suffix.lower() in exts:
        yield root
        return
    if root.is_dir():
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in exts:
                continue
            # Ignore files inside any _processed/ path under the given root
            try:
                rel = p.parent.relative_to(root)
                if any(part == "_processed" for part in rel.parts):
                    continue
            except Exception:
                pass
            yield p


def _axis_vec(axis: str):
    import FreeCAD as App  # type: ignore

    axis = axis.lower()
    if axis == "x":
        return App.Vector(1, 0, 0)
    if axis == "y":
        return App.Vector(0, 1, 0)
    return App.Vector(0, 0, 1)


def compose_rotation(ns) -> "object":
    """Build a FreeCAD.Rotation from source/target up and additional XYZ rotations.

    Returns a FreeCAD.Rotation (identity if no rotation requested).
    """
    import FreeCAD as App  # type: ignore

    rot = App.Rotation()  # identity
    # Map source up to target up if provided
    s_up = getattr(ns, "source_up", None)
    t_up = getattr(ns, "target_up", None) or (s_up and "z")
    if s_up and t_up and s_up != t_up:
        v1 = _axis_vec(s_up)
        v2 = _axis_vec(t_up)
        # Compute axis-angle
        dot = float(v1.dot(v2)) / (v1.Length * v2.Length)
        dot = max(-1.0, min(1.0, dot))
        angle_rad = math.acos(dot)
        angle_deg = math.degrees(angle_rad)
        axis = v1.cross(v2)
        if axis.Length < 1e-9:
            # Opposite vectors; choose a perpendicular axis
            axis = App.Vector(1, 0, 0) if abs(v1.x) < 0.9 else App.Vector(0, 1, 0)
        rot = App.Rotation(axis, angle_deg).multiply(rot)

    # Then apply explicit Euler-like rotations X -> Y -> Z
    rx = getattr(ns, "rotate_x", 0.0) or 0.0
    ry = getattr(ns, "rotate_y", 0.0) or 0.0
    rz = getattr(ns, "rotate_z", 0.0) or 0.0
    if rx:
        rot = App.Rotation(App.Vector(1, 0, 0), float(rx)).multiply(rot)
    if ry:
        rot = App.Rotation(App.Vector(0, 1, 0), float(ry)).multiply(rot)
    if rz:
        rot = App.Rotation(App.Vector(0, 0, 1), float(rz)).multiply(rot)
    return rot


def convert_file(
    src: Path,
    dst_dir: Path,
    linear_deflection: float,
    angular_deflection: float,
    relative: bool,
) -> Tuple[bool, str]:
    try:
        # Lazy imports so the script can show a clean error if FreeCAD is missing
        import FreeCAD  # type: ignore
        import Part  # type: ignore
        import Mesh  # type: ignore
        import MeshPart  # type: ignore

        dst_dir.mkdir(parents=True, exist_ok=True)
        out_path = dst_dir / (src.stem + ".stl")

        # First attempt: direct read as a single (possibly compound) shape
        try:
            shape = Part.Shape()
            shape.read(str(src))
            if hasattr(shape, "isNull") and shape.isNull():
                raise RuntimeError("empty shape from STEP")
            mesh = MeshPart.meshFromShape(
                Shape=shape,
                LinearDeflection=float(linear_deflection),
                AngularDeflection=float(angular_deflection),
                Relative=bool(relative),
            )
            Mesh.write(mesh, str(out_path))
            return True, f"OK: {src.name} -> {out_path}"
        except Exception:
            # Second attempt: document-based import (handles some multi-body edge cases)
            try:
                import Import  # type: ignore
            except Exception as ie:
                raise ie

            doc = FreeCAD.newDocument()
            try:
                Import.insert(str(src), doc.Name)
                combined = Mesh.Mesh()
                part_count = 0
                for obj in list(doc.Objects):
                    sh = getattr(obj, "Shape", None)
                    if sh is None:
                        continue
                    try:
                        if hasattr(sh, "isNull") and sh.isNull():
                            continue
                    except Exception:
                        pass
                    m = MeshPart.meshFromShape(
                        Shape=sh,
                        LinearDeflection=float(linear_deflection),
                        AngularDeflection=float(angular_deflection),
                        Relative=bool(relative),
                    )
                    combined.addMesh(m)
                    part_count += 1

                if part_count == 0:
                    return False, f"ERROR: No meshable shapes found in {src}"

                Mesh.write(combined, str(out_path))
                return True, f"OK: {src.name} -> {out_path} ({part_count} parts)"
            finally:
                try:
                    FreeCAD.closeDocument(doc.Name)
                except Exception:
                    pass
    except Exception as e:  # noqa: BLE001
        return False, f"ERROR: {src} -> {e}"


def main(argv: Iterable[str]) -> int:
    ns = parse_args(argv)
    try:
        # Check FreeCAD availability early for nicer error messages
        import FreeCAD  # noqa: F401  # type: ignore
    except Exception:
        sys.stderr.write(
            "FreeCAD Python modules not found. Run with `freecadcmd` or install FreeCAD Python packages.\n"
        )
        return 2

    script_dir = Path(__file__).resolve().parent

    # Drop-folder mode if no input specified
    drop_mode = ns.input is None
    if drop_mode:
        input_dir = script_dir / "STEP-INPUT"
        processed_dir = input_dir / "_processed"
        output_dir = script_dir / "STL-OUTPUT"
        input_dir.mkdir(parents=True, exist_ok=True)
        processed_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        # Support optional defaults via config file next to script
        cfg_path = script_dir / "step2stl.config.json"
        cfg = {}
        if cfg_path.exists():
            try:
                cfg = json.loads(cfg_path.read_text())
            except Exception:
                cfg = {}
        ns = argparse.Namespace(
            input=input_dir,
            out=output_dir if ns.out is None else ns.out,
            quality=cfg.get("quality", getattr(ns, "quality", "medium")),
            linear_deflection=getattr(ns, "linear_deflection", None),
            angular_deflection=getattr(ns, "angular_deflection", None),
            relative=getattr(ns, "relative", None),
            source_up=cfg.get("source_up", getattr(ns, "source_up", None)),
            target_up=cfg.get("target_up", getattr(ns, "target_up", None)),
            rotate_x=float(cfg.get("rotate_x", getattr(ns, "rotate_x", 0.0) or 0.0)),
            rotate_y=float(cfg.get("rotate_y", getattr(ns, "rotate_y", 0.0) or 0.0)),
            rotate_z=float(cfg.get("rotate_z", getattr(ns, "rotate_z", 0.0) or 0.0)),
        )

    # Resolve absolute paths to avoid CWD issues with FreeCADCmd
    ns.input = Path(ns.input).resolve()
    if ns.out is not None:
        ns.out = Path(ns.out).resolve()

    linear, angular, relative = resolve_mesh_params(ns)

    targets = list(find_step_files(ns.input))
    if not targets:
        if drop_mode:
            print(
                "No .step/.stp files found in STEP-INPUT/. Drop files there and re-run."
            )
            return 0
        sys.stderr.write("No .step/.stp files found.\n")
        return 1

    base_out = ns.out if ns.out is not None else (script_dir / "STL-OUTPUT")

    def out_for(p: Path) -> Path:
        # Mirror substructure when input is a directory
        if ns.input.is_dir():
            try:
                rel = p.parent.relative_to(ns.input)
            except ValueError:
                rel = Path("")
            return base_out / rel
        return base_out

    print(f"Found {len(targets)} file(s). Output: {base_out}")

    # Build final rotation to apply
    rot = compose_rotation(ns)
    try:
        import FreeCAD as App  # type: ignore
    except Exception:
        App = None  # type: ignore
    ok = 0
    for src in targets:
        # Read shape, apply rotation eagerly, then mesh (direct path)
        success = False
        msg = ""
        try:
            import Part  # type: ignore
            import MeshPart  # type: ignore
            import Mesh  # type: ignore

            out_dir = out_for(src)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / (src.stem + ".stl")

            shape = Part.Shape()
            shape.read(str(src))
            if hasattr(shape, "isNull") and shape.isNull():
                raise RuntimeError("empty shape from STEP")
            if App is not None and isinstance(rot, App.Rotation.__class__) or hasattr(rot, "Axis"):
                # Apply rotation via Placement
                shp = shape.copy()
                shp.Placement = App.Placement(App.Vector(0, 0, 0), rot)
            else:
                shp = shape
            mesh = MeshPart.meshFromShape(
                Shape=shp,
                LinearDeflection=float(linear),
                AngularDeflection=float(angular),
                Relative=bool(relative),
            )
            Mesh.write(mesh, str(out_path))
            success = True
            msg = f"OK: {src.name} -> {out_path}"
        except Exception:
            # Fallback to convert_file which handles doc-based import and gmsh
            success, msg = convert_file(
                src,
                out_for(src),
                linear_deflection=linear,
                angular_deflection=angular,
                relative=relative,
            )
        print(msg)
        if success:
            ok += 1
            # In drop-folder mode, move processed STEP into _processed/
            if drop_mode:
                processed_dir = ns.input / "_processed"
                processed_dir.mkdir(parents=True, exist_ok=True)
                dst = processed_dir / src.name
                # Avoid overwriting; add suffix if needed
                if dst.exists():
                    stem, suf = src.stem, src.suffix
                    ts = time.strftime("%Y%m%d-%H%M%S")
                    dst = processed_dir / f"{stem}-{ts}{suf}"
                try:
                    shutil.move(str(src), str(dst))
                except Exception as me:
                    print(f"WARN: could not move {src} -> {dst}: {me}")

    print(f"Done. {ok}/{len(targets)} converted.")
    return 0 if ok == len(targets) else 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
else:
    # FreeCAD macro/CLI mode sometimes imports the file instead of executing __main__
    # Try to run main() once in that case.
    try:
        import FreeCAD  # type: ignore  # noqa: F401
        if not getattr(sys, "_step2stl_invoked", False):
            sys._step2stl_invoked = True  # type: ignore[attr-defined]
            try:
                main(sys.argv[1:])
            except SystemExit:
                pass
    except Exception:
        pass
