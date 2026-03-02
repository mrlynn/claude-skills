#!/usr/bin/env python3

"""
Build distribution ZIPs for all skills.

Usage:
  python build_dist.py            # build all distributions
  python build_dist.py --scope professional
  python build_dist.py --scope mongodb
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Iterable, List
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
MDB_ROOT = ROOT / "mongodb-skills"
PROF_DIST_DIR = ROOT / "dist"
MDB_DIST_DIR = MDB_ROOT / "dist"


EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "dist",
}

EXCLUDED_FILES = {
    ".DS_Store",
}


def debug(msg: str) -> None:
    """Simple stdout logger."""
    print(msg)


def ensure_clean_dir(path: Path) -> None:
    """Remove an existing directory and recreate it empty."""
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def iter_files(base: Path) -> Iterable[Path]:
    """
    Yield all files under base, applying basic excludes.
    """
    for root, dirs, files in os_walk(base):
        # Exclude unwanted directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

        for name in files:
            if name in EXCLUDED_FILES or name.startswith("."):
                continue
            yield Path(root) / name


def os_walk(path: Path):
    """
    Wrapper around os.walk that works with Path.
    """
    import os

    return os.walk(path, topdown=True)


def zip_directory(source_dir: Path, zip_path: Path) -> None:
    """
    Zip the entire source_dir into zip_path, keeping relative paths from source_dir.
    """
    debug(f"  - Creating {zip_path.relative_to(ROOT)}")
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for file_path in iter_files(source_dir):
            arcname = file_path.relative_to(source_dir)
            zf.write(file_path, arcname.as_posix())


def zip_multi_directories(
    base_dirs: List[Path], names: List[str], zip_path: Path
) -> None:
    """
    Zip multiple directories into a single archive, each under its own top-level folder.
    """
    if len(base_dirs) != len(names):
        raise ValueError("base_dirs and names must be the same length")

    debug(f"  - Creating {zip_path.relative_to(ROOT)}")
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for base_dir, name in zip(base_dirs, names):
            for file_path in iter_files(base_dir):
                rel = file_path.relative_to(base_dir)
                arcname = Path(name) / rel
                zf.write(file_path, arcname.as_posix())


def discover_professional_skills() -> List[Path]:
    """
    Discover professional skills at the repo root: directories with a SKILL.md file.
    Excludes the mongodb-skills collection and common meta directories.
    """
    skills: List[Path] = []
    for entry in ROOT.iterdir():
        if not entry.is_dir():
            continue
        if entry.name in {
            "mongodb-skills",
            "dist",
            ".git",
            ".github",
            ".idea",
            ".vscode",
            "__pycache__",
        }:
            continue
        if (entry / "SKILL.md").is_file():
            skills.append(entry)
    return sorted(skills, key=lambda p: p.name)


def discover_mongodb_skills() -> List[Path]:
    """
    Discover MongoDB skills under mongodb-skills: directories with a SKILL.md file.
    """
    skills: List[Path] = []
    if not MDB_ROOT.is_dir():
        return skills

    for entry in MDB_ROOT.iterdir():
        if not entry.is_dir():
            continue
        if (entry / "SKILL.md").is_file():
            skills.append(entry)
    return sorted(skills, key=lambda p: p.name)


def build_professional_dist() -> None:
    debug("Building professional skills distribution...")
    ensure_clean_dir(PROF_DIST_DIR)

    skills = discover_professional_skills()
    if not skills:
        debug("  ! No professional skills found (no SKILL.md at repo root).")
        return

    # Individual skill ZIPs
    for skill_dir in skills:
        zip_path = PROF_DIST_DIR / f"{skill_dir.name}.zip"
        zip_directory(skill_dir, zip_path)

    # Collection ZIP: professional-skills-all.zip
    zip_multi_directories(
        base_dirs=skills,
        names=[p.name for p in skills],
        zip_path=PROF_DIST_DIR / "professional-skills-all.zip",
    )

    # Collection ZIP: mongodb-skills-all.zip (if MongoDB skills exist)
    mdb_skills = discover_mongodb_skills()
    if mdb_skills:
        zip_multi_directories(
            base_dirs=mdb_skills,
            names=[p.name for p in mdb_skills],
            zip_path=PROF_DIST_DIR / "mongodb-skills-all.zip",
        )


def build_mongodb_dist() -> None:
    if not MDB_ROOT.is_dir():
        debug("Skipping MongoDB skills: mongodb-skills/ directory not found.")
        return

    debug("Building MongoDB skills distribution...")
    ensure_clean_dir(MDB_DIST_DIR)

    skills = discover_mongodb_skills()
    if not skills:
        debug("  ! No MongoDB skills found under mongodb-skills/.")
        return

    # Individual MongoDB skill ZIPs under mongodb-skills/dist
    for skill_dir in skills:
        zip_path = MDB_DIST_DIR / f"{skill_dir.name}.zip"
        zip_directory(skill_dir, zip_path)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build skill distribution ZIPs.")
    parser.add_argument(
        "--scope",
        choices=["all", "professional", "mongodb"],
        default="all",
        help="Which distributions to build (default: all).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if args.scope in ("all", "professional"):
        build_professional_dist()

    if args.scope in ("all", "mongodb"):
        build_mongodb_dist()

    debug("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

