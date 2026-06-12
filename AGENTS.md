# Agent Guidance

This repository is a GPT/Codex project for XRD one-page chart generation and Feishu whiteboard publishing.

## Operating Rules

- Keep changes surgical. Do not refactor plotting behavior unless the requested output requires it.
- Use the bundled scripts instead of ad hoc plotting code.
- Validate by running real commands against `examples/sample-data` when changing scripts.
- Keep generated scratch output under `runs/`, which is ignored by git.
- Keep curated examples under `examples/`.

## Validation Commands

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\xrd_data_to_chart.py" `
  --data-dir ".\examples\sample-data" `
  --output-dir ".\runs\sample" `
  --render --check --openapi
```

Publishing requires authenticated Feishu CLI and a target document or whiteboard token:

```powershell
lark-cli auth status
npx -y @larksuite/whiteboard-cli@^0.2.11 -v
```

## Files To Preserve

- `skill/xrd-onepage-whiteboard/SKILL.md`
- `skill/xrd-onepage-whiteboard/scripts/xrd_data_to_chart.py`
- `skill/xrd-onepage-whiteboard/scripts/publish_xrd_whiteboard.py`
- `GPT_INSTRUCTIONS.md`
- `docs/USAGE.md`
