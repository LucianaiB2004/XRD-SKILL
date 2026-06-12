# XRD-SKILL

XRD-SKILL is a GPT/Codex-ready project for turning raw XRD two-column data into a publication-style one-page XRD chart, then publishing that chart as an editable Feishu/Lark whiteboard.

The project packages the verified workflow from this repository:

1. Raw XRD data to `diagram.svg`, `diagram.png`, and Feishu OpenAPI `diagram.json`.
2. `diagram.svg` or `diagram.json` to an editable Feishu whiteboard block.

## What It Solves

Traditional XRD plotting is usually manual: import data, style stacked curves, add phase markers, export an image, then paste the result into a report. This project turns that into a repeatable GPT workflow:

- read XRD exports from a folder;
- stack and style multiple sample curves;
- add phase markers for `Fe2SiO4` and `Fe2O3`;
- render and check the chart with `@larksuite/whiteboard-cli`;
- write the chart into Feishu as editable whiteboard nodes, not a flat screenshot.

## Repository Layout

```text
XRD-SKILL/
├── skill/xrd-onepage-whiteboard/      # Codex skill package
│   ├── SKILL.md                       # Skill trigger and workflow instructions
│   ├── agents/openai.yaml             # UI metadata for Codex/OpenAI skill loading
│   └── scripts/
│       ├── xrd_data_to_chart.py       # Raw data -> SVG/PNG/OpenAPI
│       └── publish_xrd_whiteboard.py  # SVG/OpenAPI -> Feishu whiteboard
├── examples/
│   ├── sample-data/                   # Example XRD txt data
│   ├── sample-output/                 # Example generated chart and Feishu preview
│   ├── reference-xrd.tif              # Original reference figure
│   └── reference-xrd-preview.png      # Preview of the reference figure
├── docs/
│   ├── USAGE.md
│   └── CUSTOM_GPT_SETUP.md
├── GPT_INSTRUCTIONS.md                # Instructions for a GPT project/custom GPT
├── AGENTS.md                          # Agent operating guidance
└── README.md
```

## Requirements

- Python 3.10 or newer.
- Node.js 20 or newer.
- `lark-cli` from `@larksuite/cli`, authenticated for Feishu/Lark.
- `@larksuite/whiteboard-cli`, invoked through `npx`.

Quick checks:

```powershell
python --version
node --version
lark-cli auth status
npx -y @larksuite/whiteboard-cli@^0.2.11 -v
```

## Quick Start

Generate a chart from the bundled sample data:

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\xrd_data_to_chart.py" `
  --data-dir ".\examples\sample-data" `
  --output-dir ".\runs\sample" `
  --render --check --openapi
```

Publish it to an existing Feishu whiteboard:

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\publish_xrd_whiteboard.py" `
  --whiteboard-token "<WHITEBOARD_TOKEN>" `
  --openapi-json ".\runs\sample\diagram.json" `
  --preview-output ".\runs\sample\live"
```

Append a new whiteboard block to a Feishu doc/wiki page:

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\publish_xrd_whiteboard.py" `
  --doc "https://your-domain.feishu.cn/wiki/..." `
  --svg ".\runs\sample\diagram.svg" `
  --title "XRD 一图流画板" `
  --preview-output ".\runs\sample\live"
```

## Using As A Codex Skill

Copy or symlink `skill/xrd-onepage-whiteboard` into your Codex skills directory:

```powershell
Copy-Item ".\skill\xrd-onepage-whiteboard" "$env:USERPROFILE\.codex\skills\xrd-onepage-whiteboard" -Recurse -Force
```

Restart Codex, then ask:

```text
Use $xrd-onepage-whiteboard to turn the XRD files in ./examples/sample-data into a chart and publish it to this Feishu document: <doc URL>
```

## Example Output

Local rendered chart:

![Generated XRD chart](examples/sample-output/diagram.png)

Feishu live preview:

![Feishu live preview](examples/sample-output/feishu-live-preview.png)

## Notes

- The default file pattern is `XN*_Theta_2-Theta.txt`, matching the current fine-slime sample naming convention.
- The default phase markers are tuned for the supplied data and can be changed with `--black-peaks` and `--red-peaks`.
- `publish_xrd_whiteboard.py` uses overwrite mode when updating an existing whiteboard so accidental manual edits can be restored from generated source.

## License

MIT. See [LICENSE](LICENSE).
