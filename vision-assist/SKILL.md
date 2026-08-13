---
name: vision-assist
description: 识别和分析图片、截图、流程图、模型结构图、代码报错画面、PDF 页面或 PDF 内嵌图片等视觉内容，当底层模型不具备原生识图能力时使用。触发场景：用户分享本地图片路径或图片 URL、要求“识别/描述/分析/OCR”某张图片或 PDF 中的图、遇到代码报错截图、论文流程图、视觉模型结构图，或需要从图片中提取文字。
---

# 图片识别（vision-assist）

底层模型不能直接“看”图片。遇到图片时**不要用 Read 工具读取图片文件**（读不出像素内容），改用脚本 `scripts/vision.js`：

```powershell
node "<本skill目录>/scripts/vision.js" "<图片绝对路径>" "用中文详细描述这张图片的内容"
```

## 使用规则

- 本地图片：直接传绝对路径。
- 网络图片：加 `--url` 参数：`node vision.js --url "<图片URL>" "问题"`。
- 根据用户任务改写提示词，例如：
  - 代码报错截图：提取错误类型、错误信息、堆栈、可能原因和修复建议。
  - 论文流程图：描述标题、节点、连线、分支条件和整体流程。
  - 模型结构图：描述模块名称、输入输出、连接方式和数据流向。
  - 纯文字提取（OCR）：要求“逐字提取图中全部文字”。
  - 用户需要结构化结果时，在提示词中要求“仅输出 JSON”。
- 脚本会把识别结果打印到 stdout，直接读取并转述给用户；不要虚构图片中不存在的内容。
- 图片在 PDF 中时：先用 Python/PyMuPDF 或系统工具把 PDF 页面渲染成 PNG，再对 PNG 调用本脚本。
- 多个图片时逐张调用，拿到全部结果后再统一回复。

## PDF 识别

用户给的图在 PDF 里时，先用脚本取图，再识别：

```powershell
python "<本skill目录>/scripts/pdf_to_images.py" "<PDF路径>" [--mode page|embedded] [--pages 1,3-5] [--dpi 200]
```

- `--mode page`（默认）：整页渲染成 PNG，适合流程图、版面复杂的页面；页面文字密集时建议 `--dpi 300`。
- `--mode embedded`：提取页内嵌图片，适合论文插图，按 xref 去重。
- 脚本会打印 JSON 文件清单；对清单中每个 PNG 依次调用 `vision.js`，最后统一汇总结果给用户。
- 输出目录默认是 PDF 同目录下的 `<文件名>_vision/`，可用 `--out` 指定。

## 配置

配置文件为本目录下的 `scripts/.env`：

- `DASHSCOPE_API_KEY`：阿里云百炼 API Key（必填，用户自己填写）。
- `VISION_MODEL`：视觉模型名，默认 `qwen3.5-omni-plus-2026-03-15`（当前 `.env` 中已配置）。
- `DASHSCOPE_BASE_URL`：OpenAI 兼容接口地址，默认 `https://dashscope.aliyuncs.com/compatible-mode/v1`；如果模型来自其他平台，改成对应地址即可。
- PDF 取图需要 Python 与 PyMuPDF（`pip install pymupdf`；本机已安装）。

## 失败处理

调用失败（401/403/429/网络错误）时，把脚本输出的原始报错告诉用户，并提示检查：
1. `.env` 中 API Key 是否已填写且未过期；
2. `VISION_MODEL` 是否在该平台可用；
3. 免费额度或速率限制是否超限。
