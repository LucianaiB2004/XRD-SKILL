---
name: xrd-onepage-whiteboard
description: "Generate XRD one-page charts from raw two-column XRD data and publish them as editable Feishu/Lark whiteboards. Use when the user asks for XRD 一图流, XRD data-to-chart automation, XRD chart reconstruction, or converting an XRD figure/SVG/OpenAPI JSON into a Feishu whiteboard. Supports two workflows: raw XRD data to SVG/PNG/OpenAPI chart, and SVG/OpenAPI chart to Feishu whiteboard block."
---

# XRD Onepage Whiteboard

Build an editable XRD one-page Feishu whiteboard from raw XRD exports. The skill is script-led so future runs do not need to rewrite the same plotting and `lark-cli` glue.

## Capabilities

1. **Raw data -> XRD chart**
   - Use `scripts/xrd_data_to_chart.py`.
   - Input: a folder of two-column XRD files, typically `*_Theta_2-Theta.txt`.
   - Output: `diagram.svg`, optional `diagram.png`, optional `diagram.json`, plus `metadata.json`.

2. **XRD chart -> Feishu whiteboard**
   - Use `scripts/publish_xrd_whiteboard.py`.
   - Input: `diagram.svg` or `diagram.json`.
   - Target: an existing `--whiteboard-token`, or a `--doc` URL/token where the script appends a new heading and blank whiteboard block.
   - Output: updated editable whiteboard and optional live preview PNG.

## Prerequisites

Before publishing to Feishu, verify:

```powershell
lark-cli auth status
npx -y @larksuite/whiteboard-cli@^0.2.11 -v
```

Use `--as user` by default for user-owned docs/wiki pages. If `lark-cli` asks for more scope, follow the lark-shared authorization workflow.

## Workflow 1: Data To XRD Chart

Run from the project/workspace root so relative output paths are stable:

```powershell
python ".\scripts\xrd_data_to_chart.py" `
  --data-dir ".\examples\sample-data" `
  --output-dir ".\runs\xrd-run" `
  --render --check --openapi
```

Defaults are tuned for the current XRD one-page style:

- `--pattern "XN*_Theta_2-Theta.txt"` includes the seven `XN1`-`XN7` fine-slime samples and skips the `tuonijingkuang` reference file.
- `--label-prefix "细泥"` labels `XN1` as `细泥1`, etc.
- `--black-peaks` marks Fe2SiO4 default positions.
- `--red-peaks` marks Fe2O3 default positions.

For a different dataset, change only the pattern and peak lists:

```powershell
python ".\scripts\xrd_data_to_chart.py" `
  --data-dir ".\data" `
  --pattern "*_Theta_2-Theta.txt" `
  --black-peaks "30.2,35.6,43.3,48.6,57.4,62.7" `
  --red-peaks "20.6,38.8,54.1" `
  --render --check --openapi
```

Always view `diagram.png` after generation. `whiteboard-cli --check` catches many layout errors, but not every visual collision.

## Workflow 2: Publish Chart To Feishu Whiteboard

Overwrite an existing whiteboard:

```powershell
python ".\scripts\publish_xrd_whiteboard.py" `
  --whiteboard-token "<WHITEBOARD_TOKEN>" `
  --openapi-json ".\runs\xrd-run\diagram.json" `
  --preview-output ".\runs\xrd-run\live"
```

Append a new whiteboard block to a doc/wiki page:

```powershell
python ".\scripts\publish_xrd_whiteboard.py" `
  --doc "https://example.feishu.cn/wiki/..." `
  --svg ".\runs\xrd-run\diagram.svg" `
  --title "XRD 一图流画板" `
  --preview-output ".\runs\xrd-run\live"
```

The publish script uses `--overwrite` for existing whiteboards. This is intentional: it restores a known-good generated state and prevents duplicated overlapping nodes.

## Verification Checklist

After each end-to-end run:

- Confirm `diagram.png` looks correct locally.
- Confirm `whiteboard-cli --check` exits successfully.
- Confirm `publish_xrd_whiteboard.py` returns `"ok": true`.
- Open or view the exported `live.png` preview from Feishu.
- Return the Feishu doc/whiteboard link and the preview image path to the user.
