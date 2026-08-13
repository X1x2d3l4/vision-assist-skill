# vision-assist skill

给不具备原生识图能力的 AI（如 Codex 中的纯文本模型）添加“看图”能力：识别图片、截图、流程图、模型结构图、代码报错画面，以及 PDF 页面/内嵌图片。

## 目录结构

```
vision-assist/
├── SKILL.md                 # 技能说明与触发规则
└── scripts/
    ├── vision.js            # 图片识别（OpenAI 兼容接口，默认阿里云百炼）
    ├── pdf_to_images.py     # PDF 取图（整页渲染 / 提取内嵌图）
    └── .env.example         # 配置文件模板（复制为 .env 后填写）
```

## 安装（Windows，Codex 与 Claude Code 共用）

1. 把 `vision-assist` 文件夹复制到 Codex 的个人 skills 目录：

```powershell
$dest = Join-Path $env:USERPROFILE ".agents\skills\vision-assist"
Copy-Item -LiteralPath ".\vision-assist" -Destination $dest -Recurse -Force
```

2. 创建配置文件并填入 API Key：

```powershell
Copy-Item "$dest\scripts\.env.example" "$dest\scripts\.env"
notepad "$dest\scripts\.env"
```

`DASHSCOPE_API_KEY` 填阿里云百炼的 Key（获取地址：https://bailian.console.aliyun.com/）。`VISION_MODEL` 默认 `qwen3.5-omni-plus-2026-03-15`，可按需修改；如果用其他 OpenAI 兼容平台，改 `DASHSCOPE_BASE_URL` 即可。

3. （可选）让 Claude Code 通过目录联接读取同一份，实现两边共用：

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\vision-assist" -Target $dest
```

不想共用时，把 `vision-assist` 文件夹直接复制到 `~/.claude\skills\` 即可。

4. 依赖：

- Node.js（运行 vision.js）
- Python 3 + PyMuPDF（PDF 取图用）：`pip install pymupdf`

## 使用

在 Codex 里直接发图片路径或 PDF，说“识别/描述/分析这张图”即可自动触发。手动验证：

```powershell
node "$env:USERPROFILE\.agents\skills\vision-assist\scripts\vision.js" "图片.png" "用中文详细描述这张图片"
python "$env:USERPROFILE\.agents\skills\vision-assist\scripts\pdf_to_images.py" "论文.pdf" --mode embedded
```

## 安全

- 真实 API Key 只放在本机 `scripts/.env`，该文件不要提交到 GitHub（仓库已含 `.gitignore`）。
- 截图或分享终端画面时注意给 Key 打码。
