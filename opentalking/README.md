# OpenTalking 运行包

这是从 OpenTalking 源码整理出的可运行压缩包，保留 WebUI、API、Worker、启动脚本、配置示例和文档。随包示例数字人已经移除，使用前需要通过 WebUI 上传自己的数字人形象。Git 元数据、官网宣传页、重复 README 和 GitHub 模板已经移除。

## 目录说明

| 路径 | 内容 |
| --- | --- |
| `apps/web` | React WebUI |
| `apps/api`、`opentalking` | API、Worker 与运行时代码 |
| `scripts/start_unified.sh` | 源码模式的统一启动脚本 |
| `docker-compose.yml` | Docker 全栈编排，默认 Mock 模式 |
| `examples/avatars` | 用户导入的 Avatar bundle 根目录；仓库不再附带示例形象 |
| `docs` | 项目文档 |
| `.env.example` | 环境变量模板 |

## Docker 启动

```bash
cp .env.example .env
docker compose up -d
```

启动后访问 `http://127.0.0.1:5173`，API 文档位于 `http://127.0.0.1:8000/docs`。停止服务：

```bash
docker compose down
```

默认配置使用 Mock 合成，不需要 GPU 和模型权重。需要真实合成时，请补全 `.env` 中的 LLM、TTS 和模型后端配置，再按需启用 GPU profile。

## 源码启动

需要 Python 3.10+、Node.js、FFmpeg，以及可用的 LLM 配置。

```bash
uv sync --extra dev --python 3.11
source .venv/bin/activate
cp .env.example .env
bash scripts/start_unified.sh --mock
```

默认 WebUI 地址为 `http://127.0.0.1:5173`。第一次打开后，先在“形象库”上传图片或视频，再开始会话。停止服务：

```bash
bash scripts/quickstart/stop_all.sh
```

模型权重不包含在压缩包内。真实口型合成需要另外准备本地模型，或配置 OmniRT 等远程运行时。
