# XRD-SKILL

XRD-SKILL 是一个面向 GPT / Codex 的 XRD 一图流项目：它可以把原始 XRD 二维数据自动绘制成一张堆叠谱线图，并进一步发布为可编辑的飞书 / Lark 画板。

这个项目封装了已经验证通过的完整链路：

1. XRD 原始数据生成 `diagram.svg`、`diagram.png` 和飞书画板 OpenAPI 节点文件 `diagram.json`。
2. 将 `diagram.svg` 或 `diagram.json` 写入飞书文档中的可编辑画板块。

## 项目能做什么

传统 XRD 作图通常需要手动导入数据、叠放曲线、添加物相标记、导出图片，再粘贴到汇报文档里。XRD-SKILL 把这套流程变成可重复执行的 GPT 工作流：

- 从文件夹中读取 XRD 导出的二维数据；
- 自动绘制多条样品谱线的堆叠图；
- 添加 `Fe2SiO4` 和 `Fe2O3` 等物相峰位标记；
- 使用 `@larksuite/whiteboard-cli` 渲染并检查图形；
- 将结果写入飞书画板，生成可编辑节点，而不是一张不可编辑截图。

## 项目结构

```text
XRD-SKILL/
├── skill/xrd-onepage-whiteboard/      # Codex Skill 包
│   ├── SKILL.md                       # Skill 触发说明和工作流
│   ├── agents/openai.yaml             # Codex/OpenAI Skill UI 元数据
│   └── scripts/
│       ├── xrd_data_to_chart.py       # XRD 原始数据 -> SVG/PNG/OpenAPI
│       └── publish_xrd_whiteboard.py  # SVG/OpenAPI -> 飞书画板
├── examples/
│   ├── sample-data/                   # 示例 XRD txt 数据
│   ├── sample-output/                 # 示例生成图和飞书预览
│   ├── reference-xrd.tif              # 原始参考效果图
│   └── reference-xrd-preview.png      # 参考效果图预览
├── docs/
│   ├── USAGE.md                       # 详细使用说明
│   └── CUSTOM_GPT_SETUP.md            # GPT 项目/自定义 GPT 配置说明
├── GPT_INSTRUCTIONS.md                # 给 GPT 项目使用的指令
├── AGENTS.md                          # Agent 维护规则
└── README.md
```

## 环境要求

- Python 3.10 或更高版本；
- Node.js 20 或更高版本；
- 已安装并完成认证的 `lark-cli`；
- 可通过 `npx` 调用的 `@larksuite/whiteboard-cli`。

快速检查：

```powershell
python --version
node --version
lark-cli auth status
npx -y @larksuite/whiteboard-cli@^0.2.11 -v
```

## 快速开始

使用仓库内置示例数据生成 XRD 一图流：

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\xrd_data_to_chart.py" `
  --data-dir ".\examples\sample-data" `
  --output-dir ".\runs\sample" `
  --render --check --openapi
```

生成结果包括：

- `runs/sample/diagram.svg`：可转换为飞书画板节点的 SVG 源文件；
- `runs/sample/diagram.png`：本地渲染预览图；
- `runs/sample/diagram.json`：飞书 OpenAPI 画板节点；
- `runs/sample/metadata.json`：输入数据和输出文件记录。

## 发布到飞书画板

覆盖写入已有飞书画板：

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\publish_xrd_whiteboard.py" `
  --whiteboard-token "<WHITEBOARD_TOKEN>" `
  --openapi-json ".\runs\sample\diagram.json" `
  --preview-output ".\runs\sample\live"
```

追加一个新画板块到飞书文档或 Wiki 页面：

```powershell
python ".\skill\xrd-onepage-whiteboard\scripts\publish_xrd_whiteboard.py" `
  --doc "https://your-domain.feishu.cn/wiki/..." `
  --svg ".\runs\sample\diagram.svg" `
  --title "XRD 一图流画板" `
  --preview-output ".\runs\sample\live"
```

发布脚本会导出飞书端实时预览图，用于确认写入后的布局是否正确。

## 作为 Codex Skill 使用

将 `skill/xrd-onepage-whiteboard` 复制到 Codex 的 skills 目录：

```powershell
Copy-Item ".\skill\xrd-onepage-whiteboard" "$env:USERPROFILE\.codex\skills\xrd-onepage-whiteboard" -Recurse -Force
```

重启 Codex 后，可以直接这样调用：

```text
使用 $xrd-onepage-whiteboard，把 ./examples/sample-data 里的 XRD 数据生成一图流，并发布到这个飞书文档：<文档链接>
```

## 作为 GPT 项目使用

如果要包装成自定义 GPT 或 GPT 项目，建议把以下文件加入项目知识：

- `README.md`
- `GPT_INSTRUCTIONS.md`
- `docs/USAGE.md`
- `docs/CUSTOM_GPT_SETUP.md`
- `skill/xrd-onepage-whiteboard/SKILL.md`

运行环境中保留这两个脚本，供 GPT / Agent 调用：

- `skill/xrd-onepage-whiteboard/scripts/xrd_data_to_chart.py`
- `skill/xrd-onepage-whiteboard/scripts/publish_xrd_whiteboard.py`

## 示例输出

本地生成的 XRD 图：

![生成的 XRD 图](examples/sample-output/diagram.png)

飞书端导出的画板预览：

![飞书画板预览](examples/sample-output/feishu-live-preview.png)

## 常用参数

默认文件匹配规则：

```text
XN*_Theta_2-Theta.txt
```

默认样品标签：

```text
XN1 -> 细泥1
XN2 -> 细泥2
...
```

可通过参数调整物相峰位：

```powershell
--black-peaks "30.2,35.6,43.3,48.6,57.4,62.7"
--red-peaks "20.6,38.8,54.1"
```

如果不需要物相标记：

```powershell
--no-markers
```

## 注意事项

- 默认只读取 `XN*_Theta_2-Theta.txt`，因此不会把 `tuonijingkuang` 参考样误放进图里。
- 如果换了数据集，应先确认文件名规则和峰位标记是否需要调整。
- `publish_xrd_whiteboard.py` 覆盖已有画板时会使用 overwrite 模式，适合恢复被误移动或误编辑的画板。
- 每次发布后都应查看飞书端导出的 `live.png`，因为本地检查不能覆盖所有视觉碰撞问题。

## 许可证

本项目使用 MIT License。详见 [LICENSE](LICENSE)。
