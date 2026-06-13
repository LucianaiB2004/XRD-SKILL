# Project Summary

XRD-SKILL packages the full chain from raw XRD data to editable Feishu whiteboard:

- `xrd_data_to_chart.py` generates the chart artifacts.
- `publish_xrd_whiteboard.py` publishes or restores Feishu whiteboards.
- `scripts/preflight.py` checks Python, Node.js, whiteboard-cli, and optional Feishu CLI auth.
- `scripts/install_codex_skill.py` installs the packaged skill into the local Codex skills directory.
- The repository root can be installed as the `xrd-onepage-whiteboard` Codex skill.
- `GPT_INSTRUCTIONS.md` can be used as a Custom GPT or GPT project instruction file.

The bundled sample is based on seven XRD exports named `XN1` through `XN7`. The generated chart reproduces a stacked XRD one-page view with phase markers for `Fe2SiO4` and `Fe2O3`.
