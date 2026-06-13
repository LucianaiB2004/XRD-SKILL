#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SKILL_NAME = "xrd-onepage-whiteboard"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install XRD-SKILL into the local Codex skills directory.")
    parser.add_argument(
        "--dest",
        default=None,
        help="Destination skills root. Defaults to %%CODEX_HOME%%\\skills or %%USERPROFILE%%\\.codex\\skills.",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing installed skill.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_dest_root() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "skills"
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        return Path(user_profile).expanduser() / ".codex" / "skills"
    return Path.home() / ".codex" / "skills"


def ensure_safe_remove(dest_root: Path, dest: Path) -> None:
    root = dest_root.resolve()
    target = dest.resolve()
    if target.name != SKILL_NAME or target.parent != root:
        raise SystemExit(f"Refusing to remove unexpected path: {target}")


def main() -> int:
    args = parse_args()
    source = repo_root() / "skill" / SKILL_NAME
    if not source.is_dir():
        print(f"Skill source not found: {source}", file=sys.stderr)
        return 2

    dest_root = Path(args.dest).expanduser() if args.dest else default_dest_root()
    dest = dest_root / SKILL_NAME
    dest_root.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        if not args.force:
            print(f"Skill already exists: {dest}", file=sys.stderr)
            print("Rerun with --force to replace it.", file=sys.stderr)
            return 1
        ensure_safe_remove(dest_root, dest)
        shutil.rmtree(dest)

    shutil.copytree(source, dest)
    print(f"Installed {SKILL_NAME} to {dest}")
    print("Restart Codex to refresh the available skills list.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
