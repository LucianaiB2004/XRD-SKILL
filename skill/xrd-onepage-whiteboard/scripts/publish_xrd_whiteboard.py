#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish an XRD SVG/OpenAPI chart to a Feishu whiteboard.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--svg", help="Path to diagram.svg. It will be converted to OpenAPI JSON.")
    source.add_argument("--openapi-json", help="Path to existing diagram.json from whiteboard-cli.")

    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--doc", help="Feishu/Lark doc or wiki URL/token. A whiteboard block will be appended.")
    target.add_argument("--whiteboard-token", help="Existing whiteboard token to overwrite.")

    parser.add_argument("--title", default="XRD 一图流画板", help="Heading to append before a new whiteboard block.")
    parser.add_argument("--as", dest="identity", default="user", choices=["user", "bot"])
    parser.add_argument("--idempotent-token", default=None)
    parser.add_argument("--preview-output", default=None, help="Relative output stem/path for live preview image.")
    parser.add_argument("--no-preview", action="store_true")
    return parser.parse_args()


def run_json(command: list[str]) -> dict:
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="replace")
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)
    if completed.returncode != 0:
        print(completed.stdout, file=sys.stderr)
        raise SystemExit(completed.returncode)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        print(completed.stdout)
        raise


def run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout, file=sys.stderr)
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode)


def exe(name: str) -> str:
    return shutil.which(name) or name


def relative_cli_path(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return resolved.relative_to(cwd).as_posix()
    except ValueError:
        raise SystemExit(f"Path must be under the current working directory for lark-cli file arguments: {resolved}")


def convert_svg_to_json(svg_path: Path) -> Path:
    output = svg_path.with_suffix(".json")
    run([exe("npx"), "-y", "@larksuite/whiteboard-cli@^0.2.11", "-i", str(svg_path), "--to", "openapi", "--format", "json", "-o", str(output)])
    return output


def append_whiteboard(doc: str, title: str, identity: str) -> tuple[str, str | None]:
    content = f"<h2>{title}</h2><whiteboard type=\"blank\"></whiteboard>"
    result = run_json(
        [
            exe("lark-cli"),
            "docs",
            "+update",
            "--api-version",
            "v2",
            "--as",
            identity,
            "--doc",
            doc,
            "--command",
            "append",
            "--content",
            content,
            "--format",
            "json",
        ]
    )
    blocks = result.get("data", {}).get("document", {}).get("new_blocks", [])
    for block in blocks:
        if block.get("block_type") == "whiteboard" and block.get("block_token"):
            return block["block_token"], block.get("block_id")
    raise SystemExit("docs +update succeeded but did not return a whiteboard block_token")


def main() -> int:
    args = parse_args()
    json_path = Path(args.openapi_json).resolve() if args.openapi_json else convert_svg_to_json(Path(args.svg).resolve())
    if not json_path.is_file():
        print(f"OpenAPI JSON not found: {json_path}", file=sys.stderr)
        return 2

    block_id = None
    whiteboard_token = args.whiteboard_token
    if args.doc:
        whiteboard_token, block_id = append_whiteboard(args.doc, args.title, args.identity)

    token = args.idempotent_token or f"{int(time.time())}xrdflow"
    source_arg = "@" + relative_cli_path(json_path)
    update = run_json(
        [
            exe("lark-cli"),
            "whiteboard",
            "+update",
            "--whiteboard-token",
            whiteboard_token,
            "--source",
            source_arg,
            "--input_format",
            "raw",
            "--idempotent-token",
            token,
            "--overwrite",
            "--as",
            args.identity,
        ]
    )

    preview_path = None
    if not args.no_preview:
        if args.preview_output:
            preview_stem = Path(args.preview_output)
        else:
            preview_stem = json_path.with_name("live")
        output_arg = relative_cli_path(preview_stem)
        preview = run_json(
            [
                exe("lark-cli"),
                "whiteboard",
                "+query",
                "--whiteboard-token",
                whiteboard_token,
                "--output_as",
                "image",
                "--output",
                output_arg,
                "--overwrite",
                "--as",
                args.identity,
            ]
        )
        preview_path = preview.get("data", {}).get("preview_image_path")

    print(
        json.dumps(
            {
                "ok": True,
                "whiteboard_token": whiteboard_token,
                "block_id": block_id,
                "json": str(json_path),
                "preview": preview_path,
                "created_node_ids": update.get("data", {}).get("created_node_ids"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
