# Custom GPT / GPT Project Setup

Use this repository as the knowledge and code base for a GPT project that automates XRD chart generation and Feishu whiteboard publishing.

## Suggested GPT Name

XRD 一图流画板助手

## Suggested Description

从 XRD 原始数据自动生成堆叠谱线图，并发布为可编辑的飞书画板。

## Knowledge Files

Add these files to the GPT/project knowledge:

- `README.md`
- `GPT_INSTRUCTIONS.md`
- `docs/USAGE.md`
- `skill/xrd-onepage-whiteboard/SKILL.md`

Keep the scripts in the project workspace so the agent can execute them:

- `skill/xrd-onepage-whiteboard/scripts/xrd_data_to_chart.py`
- `skill/xrd-onepage-whiteboard/scripts/publish_xrd_whiteboard.py`

## Starter Prompts

```text
把这个文件夹里的 XRD 数据生成一图流，并发布到我的飞书文档：<doc URL>
```

```text
从 ./examples/sample-data 生成 XRD 图，先只输出 PNG 和 SVG，不发布飞书。
```

```text
用已有 diagram.json 覆盖修复这个飞书画板：<whiteboard token>
```

## Runtime Requirements

The GPT runner or local agent environment must have:

- Python 3.10+
- Node.js 20+
- `lark-cli` authenticated as the target Feishu/Lark user
- network access to install or run `@larksuite/whiteboard-cli` through `npx`
