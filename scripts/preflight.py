#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass


WHITEBOARD_PACKAGE = "@larksuite/whiteboard-cli@^0.2.11"
MIN_PYTHON = (3, 10)
MIN_NODE_MAJOR = 20


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    command: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check runtime dependencies for XRD-SKILL.")
    parser.add_argument("--skip-lark", action="store_true", help="Skip lark-cli checks for local chart generation only.")
    parser.add_argument(
        "--skip-whiteboard",
        action="store_true",
        help="Skip @larksuite/whiteboard-cli checks. Only use this for syntax-only validation.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def command_text(command: list[str]) -> str:
    return " ".join(command)


def run(command: list[str], timeout: int = 90) -> tuple[int, str, str]:
    executable = shutil.which(command[0])
    if executable is None:
        return 127, "", f"{command[0]} not found on PATH"
    completed = subprocess.run(
        [executable, *command[1:]],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def check_python() -> CheckResult:
    version = sys.version_info
    detail = f"{version.major}.{version.minor}.{version.micro}"
    if (version.major, version.minor) < MIN_PYTHON:
        return CheckResult("Python", "fail", f"{detail}; require Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+")
    return CheckResult("Python", "pass", detail)


def check_node() -> CheckResult:
    command = ["node", "--version"]
    code, stdout, stderr = run(command)
    detail = stdout or stderr
    if code != 0:
        return CheckResult("Node.js", "fail", detail, command_text(command))
    match = re.search(r"v?(\d+)", detail)
    major = int(match.group(1)) if match else 0
    if major < MIN_NODE_MAJOR:
        return CheckResult("Node.js", "fail", f"{detail}; require Node.js {MIN_NODE_MAJOR}+", command_text(command))
    return CheckResult("Node.js", "pass", detail, command_text(command))


def check_whiteboard_cli() -> CheckResult:
    command = ["npx", "-y", WHITEBOARD_PACKAGE, "-v"]
    code, stdout, stderr = run(command, timeout=180)
    detail = stdout or stderr
    if code != 0:
        return CheckResult("whiteboard-cli", "fail", detail, command_text(command))
    return CheckResult("whiteboard-cli", "pass", detail, command_text(command))


def check_lark_cli_available() -> CheckResult:
    command = ["lark-cli", "--version"]
    code, stdout, stderr = run(command)
    detail = stdout or stderr
    if code != 0:
        return CheckResult("lark-cli", "fail", detail, command_text(command))
    return CheckResult("lark-cli", "pass", detail, command_text(command))


def check_lark_auth() -> CheckResult:
    command = ["lark-cli", "auth", "status"]
    code, stdout, stderr = run(command)
    detail = stdout or stderr
    if code != 0:
        return CheckResult("lark-cli auth", "fail", detail, command_text(command))
    return CheckResult("lark-cli auth", "pass", detail, command_text(command))


def print_human(results: list[CheckResult]) -> None:
    for item in results:
        marker = "[ok]" if item.status == "pass" else "[fail]"
        suffix = f" ({item.command})" if item.command else ""
        print(f"{marker} {item.name}: {item.detail}{suffix}")


def main() -> int:
    args = parse_args()
    results = [check_python()]
    if not args.skip_whiteboard:
        results.append(check_node())
        results.append(check_whiteboard_cli())
    if not args.skip_lark:
        results.append(check_lark_cli_available())
        results.append(check_lark_auth())

    if args.json:
        print(json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2))
    else:
        print_human(results)

    return 1 if any(item.status == "fail" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
