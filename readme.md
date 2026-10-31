# roleplay_talking

一个轻量化的 AI 数字人生成与角色对话框架。输入人物设定，接入自己的 LLM API，就可以让角色开始对话；后续再补上对话记忆和对话修正。

叫它“AI 伴侣计划”也可以，不过这个项目想解决的不只是聊天：它要把人物设定、模型接入、上下文管理和角色修正串成一条能跑通的流程。

> 根目录的 `roleplay_talking` 仍在起步阶段，只有项目说明，没有自己的可运行代码、依赖清单或配置示例。下面写的是根目录项目的目标和计划范围；`opentalking/` 子目录中的实现另见下方模块索引。

## 短期目标

实现一个 Windows `exe` 启动器，用 GUI 引导用户部署压缩包中的 `opentalking`。部署完成后创建桌面快捷方式，用户双击快捷方式即可打开 OpenTalking WebUI（默认 `http://127.0.0.1:5173`）。

启动器不重新实现对话界面。OpenTalking 已经提供 WebUI 和统一启动脚本 `scripts/start_unified.sh`，启动器负责环境检查、依赖准备、服务启停、状态检测和打开浏览器。

## 实现方案（可行性待验证）

以下方案尚未做完整验证，先作为实现方向记录。

### 部署路线

优先封装 Docker 路线。`docker compose up -d` 会拉起 `redis`、`api`、`worker` 和 `web`，默认 Mock 模式不要求 GPU；GPU 环境可以用 `docker compose --profile gpu up` 启用真实合成后端。启动器检测 Docker 和 Compose，引导用户安装或启动 Docker，再执行 compose 命令，等待端口就绪后打开浏览器。这条路线不需要处理 Python 环境、Node 构建和模型权重，封装成本相对低。

### GUI 最小功能

1. **环境自检**：检查 Docker、Compose 是否可用，以及 `5173`、`8000` 端口是否被占用。
2. **一键启动 / 停止**：分别调用 `docker compose up -d` 和 `docker compose down`。
3. **状态显示**：轮询后端 API（`8000`）和 WebUI（`5173`），显示服务是否就绪。
4. **日志面板**：读取 `docker compose logs -f` 的输出，实时显示启动和排错信息。
5. **打开 WebUI**：服务就绪后自动调用 `webbrowser.open("http://127.0.0.1:5173")`，同时保留手动打开按钮。
6. **配置编辑**：在界面中编辑 `.env` 的关键项，例如 LLM、TTS 的 API Key，避免用户直接改文件。

### 技术实现

可以用 PySide6 或 Tauri。团队熟悉 Python 时，PySide6 上手更快；追求更小体积时，可以用 Tauri + WebView2。

下面的 Python 代码只表示启动和轮询的骨架，尚未验证：

```python
import subprocess
import time
import webbrowser
from pathlib import Path

import requests

COMPOSE_DIR = Path(__file__).parent / "opentalking"


def start_stack():
    subprocess.Popen(
        ["docker", "compose", "up", "-d"],
        cwd=COMPOSE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    for _ in range(60):
        try:
            requests.get("http://127.0.0.1:5173", timeout=1)
            webbrowser.open("http://127.0.0.1:5173")
            return
        except requests.ConnectionError:
            time.sleep(2)
```

日志面板读取 `docker compose logs -f` 的标准输出，逐行推送到 GUI。

### 分发形态

```text
OpenTalkingLauncher/
  Launcher.exe          # GUI 启动器
  _internal/            # PyInstaller 依赖（onedir）
  opentalking/          # OpenTalking 运行目录
  resources/
```

使用 PyInstaller `--onedir` 打包，`opentalking/` 原样放在 exe 同级目录，压缩整个目录后分发。用户解压并双击 `Launcher.exe`，首次运行可以引导复制 `.env.example` 为 `.env`。桌面快捷方式可以在首次运行时创建，也可以改用 Inno Setup 生成安装包。

### 需要提前确认

1. Docker 不建议静默安装。首次检测失败时给出安装指引，用户装好并启动 Docker 后重新运行启动器即可。
2. Docker 镜像不包含大模型权重。真实口型合成仍要配置本地模型后端或 OmniRT 远程运行时。默认先用 Mock 模式跑通链路，再引导配置 GPU 模型。

## OpenTalking 模块索引

`opentalking/` 子目录包含已落地的 OpenTalking 实现、API 和中文文档。下面按能力整理入口，具体字段与校验规则以运行后的 OpenAPI（`/openapi.json`）为准。

| 模块 | 作用与主要接口 | 文档/代码入口 |
| --- | --- | --- |
| 数据导入与资产库 | 导入人物包、知识库文档、记忆/微信聊天、数字人形象、复刻音色和场景背景 | [Persona Package](opentalking/docs/zh/usage/persona-package.md) · [微信聊天导入](opentalking/docs/zh/examples/Wechat_import.md) · [知识库改造说明](opentalking/docs/zh/developer-guide/agent-knowledge-lightrag.md) · [Avatar API](opentalking/docs/zh/docs/api/avatars.md) · [音色与 TTS](opentalking/docs/zh/docs/api/tts-and-voices.md) |
| 文本生成（LLM） | `POST /sessions/{id}/speak` 把文本送入会话链路；Worker 侧通过 `create_chat_task` 调用 OpenAI-compatible LLM 生成回复，当前没有独立的 `/sessions/{id}/chat` REST 路由 | [LLM 与 STT](opentalking/docs/zh/speech_models/llm-stt.md) · [LLM adapter](opentalking/opentalking/providers/llm/openai_compatible/adapter.py) · [session runner](opentalking/opentalking/pipeline/session/runner.py) |
| 语音生成（TTS） | `POST /tts/preview` 独立试听；`POST /sessions/{id}/speak` 的回复由 TTS 合成并播报；`POST /voices/clone` 复刻音色 | [TTS 与音色 API](opentalking/docs/zh/docs/api/tts-and-voices.md) · [音色与 TTS 使用](opentalking/docs/zh/usage/webui/voice-and-tts.md) |
| 语音转文字（STT） | `POST /sessions/{id}/transcribe` 返回识别文本；`POST /sessions/{id}/speak_audio` 在识别后进入会话；WebSocket 支持流式音频输入 | [会话 API](opentalking/docs/zh/docs/api/sessions.md) · [STT 文档](opentalking/docs/zh/speech_models/stt.md) |
| 视频生成 | `POST /video-creation/jobs` 创建视频任务，支持上传音频、文本合成、复刻音色、参考视频和双人对话等来源；结果可从 `/exports/videos/{id}/download` 下载 | [视频创作](opentalking/docs/zh/usage/webui/video-creation.md) · [视频创作 API/RTMPS](opentalking/docs/zh/docs/api/video-creation-rtmps-execution.md) · [视频克隆](opentalking/docs/zh/usage/webui/video-clone.md) |
| 实时对话与 WebRTC | `POST /sessions`、`POST /sessions/{id}/webrtc/offer`，以及音频输入 WebSocket；SSE `/sessions/{id}/events` 推送 `transcript`、`llm`、`subtitle.chunk`、`tts`、`frame` 等事件 | [会话 API](opentalking/docs/zh/docs/api/sessions.md) · [事件与流式接口](opentalking/docs/zh/docs/api/events.md) |
| API 接口总览 | REST、SSE 与 WebSocket；默认 Base URL 为 `http://localhost:8000`，Swagger UI 为 `<base>/docs`，原始规范为 `<base>/openapi.json` | [API 索引](opentalking/docs/zh/docs/api/index.md) · [架构说明](opentalking/docs/zh/docs/architecture.md) · [OpenTalking 中文文档](opentalking/docs/zh/index.md) |

> 列出的“生成文本”按 LLM 对话回复整理，“生成文字”按语音转文字（STT）整理；如果“生成文字”指的是前端字幕，字幕由 SSE 的 `transcript`、`llm` 和 `subtitle.chunk` 事件输出。OpenTalking 的文本生成在会话运行时内部完成，当前没有单独的 chat REST 端点。

### 导入数据可接受类型

| 导入项 | 接口 | 可接受类型与限制 |
| --- | --- | --- |
| 人物包（Persona） | `POST /personas/import` | `.otpersona` 或 `.zip`，不超过 200MB；压缩包根目录需有 `persona.json`，可带 `prompts/`、`knowledge/` 等目录。 |
| 知识库文档 | `POST /agent/knowledge-bases/{kb_id}/documents`、`POST /agent/knowledge-documents` | `.txt`、`.md`、`.markdown`、`.pdf`、`.pptx`，单文件不超过 20MB。 |
| 微信聊天记录 | `POST /memory/wechat-import` | WeFlow 导出的 `.json`、`.csv`、`.txt`、`.html`、`.htm`，或包含这些文件的 `.zip`；不接受在线 API URL。 |
| 记忆条目 | `POST /memory/libraries/{library_id}/import` | JSON 请求体；`turns` 数组中每项包含 `role`（`user` 或 `assistant`）和 `content`。 |
| 数字人形象 | `POST /avatars/custom` | 图片与视频二选一：接口文档列出的图片类型为 JPEG、PNG、WebP，不超过 10MB；视频为 MP4、WebM、MOV、AVI，不超过 200MB。视频会取首帧作为形象源图。 |
| 复刻音色 | `POST /voices/clone` | FFmpeg 能解码的音频（如 WAV、MP3、M4A、WebM），大小 256B–12MB；服务端会转为 24kHz 单声道 WAV。 |
| 视频创作音频 | `POST /video-creation/jobs`（`audio_source=upload`） | WAV、MP3、M4A、WebM 等 FFmpeg 可解码音频，默认不超过 50MB。 |
| 场景背景 | `POST /scene-assets/backgrounds` | PNG、JPEG、WebP，或 MP4、WebM、MOV；默认不超过 200MB。 |

### API 入口

- 本地 API 文档索引：[opentalking/docs/zh/docs/api/index.md](opentalking/docs/zh/docs/api/index.md)
- 运行服务后打开 Swagger UI：`http://localhost:8000/docs`
- OpenAPI 原始规范：`http://localhost:8000/openapi.json`
- 端点实现目录：[opentalking/apps/api/routes](opentalking/apps/api/routes)

## 项目目标

- 降低部署门槛：准备好人物设定和 LLM API，就能开始使用，不需要先搭一套复杂服务。
- 提供一条清楚的接入流程：第一次接触项目的人能知道先做什么、后做什么。
- 保持模块可替换：角色设定、模型调用、对话记忆和修正逻辑尽量解耦，方便按需扩展。
- 参考 OpenAI 的 OpenTalking，但把重点放在简化部署和清晰的使用指引上。

## 计划功能

- **人物设定导入**：用文本描述角色的身份、语气、背景和对话约束。
- **自备 LLM API**：由使用者提供自己的服务地址、模型和密钥，不依赖项目内置的模型服务。
- **多轮角色对话**：在连续对话中维持角色口吻和上下文连贯。
- **对话记忆**：保存必要的对话信息，供后续交流使用。
- **对话修正**：允许使用者纠正角色的回复或设定，并让修正结果影响后续对话。
- **本地配置**：密钥通过环境变量或本地配置提供，不写入仓库。

## 当前进度

- [x] 创建项目仓库和基础说明
- [ ] 实现最小可运行对话流程
- [ ] 接入 LLM API
- [ ] 加入对话记忆
- [ ] 加入对话修正
- [ ] 补充部署和使用文档

目前没有可执行程序，因此 README 暂不提供安装命令和运行命令。等最小版本落地后，会在这里补齐环境要求、配置方式和启动步骤。

## 目标使用流程

1. 编写人物设定，明确角色身份、说话方式和行为边界。
2. 配置自己的 LLM API 地址、模型名称和访问密钥。
3. 启动对话服务或本地程序。
4. 与角色进行多轮对话。
5. 根据实际效果调整记忆内容和修正规则。

以上是计划中的使用流程。具体命令、配置文件格式和接口参数会随实现同步补充。

## 设计思路

- **角色层**：把人物设定作为独立配置，避免写死在代码里。
- **模型层**：封装 LLM 调用，便于更换服务商或模型。
- **会话层**：集中管理当前对话状态，保证多轮交流的上下文一致。
- **记忆层**：保存对话中需要长期保留的信息，并按需取回。
- **修正层**：记录使用者对角色表现的调整，减少重复纠错。

## 下一步

先完成一个最小可运行版本：能够加载人物设定、调用 LLM API 并完成多轮对话。这个流程稳定后，再加入记忆和修正能力，最后补齐部署文档与示例配置。

## 安全注意事项

- 不要把 API 密钥、访问令牌或账号信息提交到仓库。
- 建议通过环境变量或未纳入版本控制的本地文件保存敏感配置。
- 输出日志时注意脱敏，避免把密钥和完整请求内容写入日志。

## 开发人员

nothing793  Reoxy258

## Task

- [ ] 将整理后的 `opentalking` 压缩包上传到 <https://github.com/nothing793/roleplay_talking>。
