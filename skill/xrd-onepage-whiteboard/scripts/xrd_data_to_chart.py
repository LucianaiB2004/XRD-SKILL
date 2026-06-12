#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from html import escape
from pathlib import Path


COLORS = [
    "#555555",
    "#f23f3f",
    "#2276df",
    "#35ad68",
    "#a86fe0",
    "#d39a00",
    "#16c7c5",
    "#d76ac2",
    "#2aa6a1",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an editable Feishu-compatible XRD SVG from two-column XRD data."
    )
    parser.add_argument("--data-dir", required=True, help="Directory containing XRD data files.")
    parser.add_argument(
        "--pattern",
        default="XN*_Theta_2-Theta.txt",
        help="Glob pattern for series files. Use '*_Theta_2-Theta.txt' to include all txt exports.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Defaults to ./diagrams/YYYY-MM-DDTHHMMSS.",
    )
    parser.add_argument("--width", type=int, default=1620)
    parser.add_argument("--height", type=int, default=1180)
    parser.add_argument("--x-min", type=float, default=None)
    parser.add_argument("--x-max", type=float, default=None)
    parser.add_argument("--label-prefix", default="细泥", help="Label prefix for XN series.")
    parser.add_argument(
        "--black-peaks",
        default="30.2,35.6,43.3,48.6,57.4,62.7",
        help="Comma-separated Fe2SiO4 marker positions.",
    )
    parser.add_argument(
        "--red-peaks",
        default="20.6,38.8,54.1",
        help="Comma-separated Fe2O3 marker positions.",
    )
    parser.add_argument("--render", action="store_true", help="Render diagram.png with whiteboard-cli.")
    parser.add_argument("--check", action="store_true", help="Run whiteboard-cli --check.")
    parser.add_argument("--openapi", action="store_true", help="Export diagram.json OpenAPI nodes.")
    parser.add_argument("--no-markers", action="store_true", help="Do not draw phase markers.")
    return parser.parse_args()


def parse_float_list(raw: str) -> list[float]:
    if not raw.strip():
        return []
    return [float(item.strip()) for item in raw.split(",") if item.strip()]


def series_key(path: Path) -> tuple[int, str]:
    match = re.search(r"XN(\d+)", path.name, re.IGNORECASE)
    if match:
        return int(match.group(1)), path.name
    return 10_000, path.name


def read_series(path: Path, label_prefix: str) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    header = lines[0].strip() if lines else path.stem
    xs: list[float] = []
    ys: list[float] = []
    for line in lines[1:]:
        parts = line.replace(",", " ").split()
        if len(parts) < 2:
            continue
        try:
            xs.append(float(parts[0]))
            ys.append(float(parts[1]))
        except ValueError:
            continue
    if not xs:
        raise ValueError(f"No numeric two-column data found in {path}")

    match = re.search(r"XN(\d+)", path.name, re.IGNORECASE)
    if match:
        label = f"{label_prefix}{int(match.group(1))}"
        sample = f"XN{int(match.group(1))}"
    else:
        label = header or path.stem
        sample = header or path.stem
    return {"path": path, "sample": sample, "label": label, "xs": xs, "ys": ys}


def downsample(xs: list[float], ys: list[float], target_points: int = 1100) -> tuple[list[float], list[float]]:
    stride = max(1, len(xs) // target_points)
    out_x = xs[::stride]
    out_y = ys[::stride]
    if out_x[-1] != xs[-1]:
        out_x.append(xs[-1])
        out_y.append(ys[-1])
    return out_x, out_y


def attr_string(values: dict[str, object]) -> str:
    return " ".join(f'{key.replace("_", "-")}="{escape(str(value))}"' for key, value in values.items())


def text(x: float, y: float, body: str, **attrs: object) -> str:
    values = {"x": round(x, 2), "y": round(y, 2)}
    values.update(attrs)
    return f"<text {attr_string(values)}>{escape(body)}</text>"


def line(x1: float, y1: float, x2: float, y2: float, **attrs: object) -> str:
    values = {"x1": round(x1, 2), "y1": round(y1, 2), "x2": round(x2, 2), "y2": round(y2, 2)}
    values.update(attrs)
    return f"<line {attr_string(values)}/>"


def rect(x: float, y: float, width: float, height: float, **attrs: object) -> str:
    values = {"x": round(x, 2), "y": round(y, 2), "width": round(width, 2), "height": round(height, 2)}
    values.update(attrs)
    return f"<rect {attr_string(values)}/>"


def red_marker(cx: float, y: float, size: float = 18.0) -> list[str]:
    half = size / 2
    return [
        rect(cx - half, y, size, size, fill="#FF0000", transform=f"rotate(45 {cx:.2f} {y + half:.2f})"),
        rect(cx - 4, y + size * 0.88, 8, size * 0.9, fill="#FF0000", rx=4),
    ]


def y_at_x(xs: list[float], ys: list[float], target: float, y_px) -> float:
    if target <= xs[0]:
        return y_px(ys[0])
    if target >= xs[-1]:
        return y_px(ys[-1])
    for index in range(1, len(xs)):
        if xs[index] >= target:
            x0, x1 = xs[index - 1], xs[index]
            y0, y1 = ys[index - 1], ys[index]
            ratio = 0.0 if x1 == x0 else (target - x0) / (x1 - x0)
            return y_px(y0 + (y1 - y0) * ratio)
    return y_px(ys[-1])


def render_svg(series: list[dict[str, object]], args: argparse.Namespace) -> str:
    width, height = args.width, args.height
    plot_l, plot_r = 80, width - 110
    plot_t, plot_b = 70, height - 140
    x_min = args.x_min if args.x_min is not None else min(min(item["xs"]) for item in series)  # type: ignore[arg-type]
    x_max = args.x_max if args.x_max is not None else max(max(item["xs"]) for item in series)  # type: ignore[arg-type]

    def x_px(value: float) -> float:
        return plot_l + (value - x_min) / (x_max - x_min) * (plot_r - plot_l)

    count = len(series)
    top_baseline = plot_t + 115
    bottom_baseline = plot_b - 60
    gap = (bottom_baseline - top_baseline) / max(1, count - 1)
    baselines = [bottom_baseline - index * gap for index in range(count)]
    amplitude = min(90.0, gap * 0.62)
    black_peaks = parse_float_list(args.black_peaks)
    red_peaks = parse_float_list(args.red_peaks)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        rect(0, 0, width, height, fill="#FFFFFF"),
        rect(plot_l, plot_t, plot_r - plot_l, plot_b - plot_t, fill="#FFFFFF", stroke="#0A0A0A", stroke_width=4),
        text(105, 115, "▼-Fe2SiO4", fill="#0A0A0A", font_size=43, font_weight=700),
        *red_marker(392, 83, 20),
        text(412, 115, "-Fe2O3", fill="#FF0000", font_size=43, font_weight=700),
    ]

    first_tick = int((x_min + 9) // 10 * 10)
    for tick in range(first_tick, int(x_max) + 1, 10):
        x = x_px(tick)
        parts.append(line(x, plot_b, x, plot_b - 30, stroke="#0A0A0A", stroke_width=4))
        parts.append(text(x - 22, plot_b + 62, str(tick), fill="#0A0A0A", font_size=43))
    for tick in range(first_tick + 5, int(x_max), 10):
        x = x_px(tick)
        parts.append(line(x, plot_b, x, plot_b - 18, stroke="#0A0A0A", stroke_width=4))

    parts.append(text(width * 0.43, plot_b + 102, "2θ (deg.)", fill="#0A0A0A", font_size=54))
    parts.append(text(42, height * 0.58, "Intensity", fill="#0A0A0A", font_size=54, transform=f"rotate(-90 42 {height * 0.58:.2f})"))

    cached = []
    for index, item in enumerate(series):
        xs: list[float] = item["xs"]  # type: ignore[assignment]
        ys: list[float] = item["ys"]  # type: ignore[assignment]
        baseline = baselines[index]
        max_y = max(max(ys), 1.0)

        def y_px(value: float, baseline: float = baseline, max_y: float = max_y) -> float:
            return baseline - (value / max_y) * amplitude

        cached.append((item, baseline, y_px))
        dx, dy = downsample(xs, ys)
        points = " ".join(f"{x_px(x):.1f},{y_px(y):.1f}" for x, y in zip(dx, dy))
        color = COLORS[index % len(COLORS)]
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>')
        label_y = baseline - 38
        label_x = plot_r - 122
        parts.append(line(label_x - 92, label_y, label_x - 10, label_y, stroke=color, stroke_width=4, stroke_linecap="round"))
        parts.append(text(label_x, label_y + 12, str(item["label"]), fill="#0A0A0A", font_size=38))

    if not args.no_markers:
        for cache_index, (item, baseline, y_px) in enumerate(cached):
            xs = item["xs"]  # type: ignore[assignment]
            ys = item["ys"]  # type: ignore[assignment]
            is_top_series = cache_index == len(cached) - 1
            red_min_y = plot_t + 95 if is_top_series else plot_t + 34
            black_min_y = plot_t + 105 if is_top_series else plot_t + 35
            for peak in red_peaks:
                if x_min <= peak <= x_max:
                    y = max(red_min_y, y_at_x(xs, ys, peak, y_px) - 22)
                    parts.extend(red_marker(x_px(peak), y, 18))
            for peak in black_peaks:
                if x_min <= peak <= x_max:
                    y = max(black_min_y, y_at_x(xs, ys, peak, y_px) - 22)
                    parts.append(text(x_px(peak) - 14, y, "▼", fill="#0A0A0A", font_size=36, font_weight=700))

    parts.append("</svg>")
    return "\n".join(parts)


def run_command(command: list[str]) -> None:
    print("+ " + " ".join(command))
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout, file=sys.stderr)
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)
    print("[ok]")


def exe(name: str) -> str:
    return shutil.which(name) or name


def main() -> int:
    args = parse_args()
    data_dir = Path(args.data_dir).resolve()
    if not data_dir.is_dir():
        print(f"Data directory not found: {data_dir}", file=sys.stderr)
        return 2

    paths = sorted(data_dir.glob(args.pattern), key=series_key)
    if not paths:
        print(f"No files matched {args.pattern!r} in {data_dir}", file=sys.stderr)
        return 2

    series = [read_series(path, args.label_prefix) for path in paths]
    output_dir = Path(args.output_dir) if args.output_dir else Path("diagrams") / datetime.now().strftime("%Y-%m-%dT%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    svg_path = output_dir / "diagram.svg"
    svg_path.write_text(render_svg(series, args), encoding="utf-8")

    metadata = {
        "series": [{"sample": item["sample"], "label": item["label"], "path": str(item["path"])} for item in series],
        "svg": str(svg_path),
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.render:
        run_command([exe("npx"), "-y", "@larksuite/whiteboard-cli@^0.2.11", "-i", str(svg_path), "-o", str(output_dir / "diagram.png"), "-f", "svg"])
    if args.check:
        run_command([exe("npx"), "-y", "@larksuite/whiteboard-cli@^0.2.11", "-i", str(svg_path), "-f", "svg", "--check"])
    if args.openapi:
        run_command([exe("npx"), "-y", "@larksuite/whiteboard-cli@^0.2.11", "-i", str(svg_path), "--to", "openapi", "--format", "json", "-o", str(output_dir / "diagram.json")])

    print(json.dumps({"ok": True, "output_dir": str(output_dir), **metadata}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
