# Usage

This guide describes the two supported workflows.

## 1. Raw XRD Data To Chart

Input files should be text files with two numeric columns:

```text
SampleName
10.0  1
10.1  2
...
```

Run:

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\xrd_data_to_chart.py" `
  --data-dir ".\examples\sample-data" `
  --output-dir ".\runs\sample" `
  --render --check --openapi
```

Outputs:

- `diagram.svg`: editable SVG source for the whiteboard converter.
- `diagram.png`: local rendered preview.
- `diagram.json`: Feishu OpenAPI whiteboard node JSON.
- `metadata.json`: list of input series and generated artifact paths.

Useful options:

```powershell
--pattern "*_Theta_2-Theta.txt"
--label-prefix "细泥"
--black-peaks "30.2,35.6,43.3,48.6,57.4,62.7"
--red-peaks "20.6,38.8,54.1"
--no-markers
```

## 2. Chart To Feishu Whiteboard

Publish to an existing whiteboard token:

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\publish_xrd_whiteboard.py" `
  --whiteboard-token "<WHITEBOARD_TOKEN>" `
  --openapi-json ".\runs\sample\diagram.json" `
  --preview-output ".\runs\sample\live"
```

Append a new whiteboard block to a document:

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\publish_xrd_whiteboard.py" `
  --doc "https://your-domain.feishu.cn/wiki/..." `
  --svg ".\runs\sample\diagram.svg" `
  --title "XRD 一图流画板" `
  --preview-output ".\runs\sample\live"
```

The script returns JSON containing the whiteboard token, block ID when a new block is created, and preview image path.

## Troubleshooting

- If `npx` cannot be found from Python on Windows, ensure Node.js is installed and `npx.cmd` is on PATH.
- If Feishu returns a permission error, run `lark-cli auth status` and refresh authorization scopes.
- If `whiteboard-cli --check` reports text overflow, adjust labels, chart width, or phase markers before publishing.
