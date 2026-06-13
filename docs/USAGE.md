# 使用说明

本文档说明 XRD-SKILL 的两条核心链路：

1. 从原始 XRD 二维数据生成 XRD 一图流；
2. 将生成的 XRD 图发布为飞书 / Lark 可编辑画板。

## 0. 环境检查

只检查本地作图所需环境：

```powershell
python ".\scripts\preflight.py" --skip-lark
```

检查完整飞书发布环境：

```powershell
python ".\scripts\preflight.py"
```

完整发布环境需要：

- Python 3.10+；
- Node.js 20+；
- 可通过 `npx` 调用 `@larksuite/whiteboard-cli`；
- 已安装并登录的 `lark-cli`。

## 1. 安装为 Codex Skill

```powershell
python ".\scripts\install_codex_skill.py" --force
```

脚本会把当前项目根目录中的 `SKILL.md`、`agents/` 和 `scripts/` 安装到本机 Codex skills 目录：

- 如果设置了 `CODEX_HOME`，安装到 `%CODEX_HOME%\skills\xrd-onepage-whiteboard`；
- 否则安装到 `%USERPROFILE%\.codex\skills\xrd-onepage-whiteboard`。

安装后重启 Codex，即可直接触发：

```text
使用 $xrd-onepage-whiteboard，把 ./examples/sample-data 生成 XRD 一图流。
```

## 2. 原始 XRD 数据生成图

输入文件应为两列数值文本，第一列为 `2θ`，第二列为强度：

```text
SampleName
10.0  1
10.1  2
...
```

使用仓库内置示例数据运行：

```powershell
python ".\scripts\xrd_data_to_chart.py" `
  --data-dir ".\examples\sample-data" `
  --output-dir ".\runs\sample" `
  --render --check --openapi
```

输出文件：

- `diagram.svg`：可被白板转换器读取的 SVG 源文件；
- `diagram.png`：本地渲染预览图；
- `diagram.json`：飞书 OpenAPI 画板节点 JSON；
- `metadata.json`：输入序列和生成文件记录。

常用参数：

```powershell
--pattern "*_Theta_2-Theta.txt"
--label-prefix "细泥"
--black-peaks "30.2,35.6,43.3,48.6,57.4,62.7"
--red-peaks "20.6,38.8,54.1"
--no-markers
```

## 3. XRD 图发布到飞书画板

发布到已有画板 token，会覆盖该画板的当前内容，适合修复被误移动或误编辑的生成图：

```powershell
python ".\scripts\publish_xrd_whiteboard.py" `
  --whiteboard-token "<WHITEBOARD_TOKEN>" `
  --openapi-json ".\runs\sample\diagram.json" `
  --preview-output ".\runs\sample\live"
```

追加一个新画板块到飞书文档或 Wiki 页面：

```powershell
python ".\scripts\publish_xrd_whiteboard.py" `
  --doc "https://your-domain.feishu.cn/wiki/..." `
  --openapi-json ".\runs\sample\diagram.json" `
  --title "XRD 一图流画板" `
  --preview-output ".\runs\sample\live"
```

脚本会返回包含 `whiteboard_token`、新建块 `block_id` 和预览图路径的 JSON。

## 4. 验证标准

一次完整验证应确认：

- `preflight.py --skip-lark` 通过；
- `install_codex_skill.py --force` 能成功复制 skill；
- `xrd_data_to_chart.py --render --check --openapi` 能生成 SVG、PNG、JSON；
- 如果发布到飞书，`publish_xrd_whiteboard.py` 返回 `"ok": true`；
- 发布后查看导出的 `live.png`，确认飞书端画板布局正常。

## 5. 常见问题

- 如果 Python 找不到 `npx`，请确认 Node.js 已安装，并且 `npx.cmd` 在 PATH 中。
- 如果 `whiteboard-cli --check` 报告文字溢出，先调整标签、画布宽度或峰位标记，再发布。
- 如果飞书返回权限错误，先运行 `lark-cli auth status`，必要时重新登录或补充授权范围。
- 如果只想验证本地 XRD 图生成，不需要登录飞书，运行 `python ".\scripts\preflight.py" --skip-lark`。
