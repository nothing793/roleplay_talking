# 数字人形象目录

这是 OpenTalking 的 Avatar bundle 根目录，默认由 `OPENTALKING_AVATARS_DIR=./examples/avatars` 指向。

仓库不再附带内置示例数字人。首次使用请在 WebUI 的“形象库”上传图片或视频，系统会在这里生成 `custom-*` 目录；也可以按 `docs/zh/docs/avatar-format.md` 手工构建 bundle。

- `custom-*`：通过 WebUI 上传或视频创作生成的用户资产。
- 其他目录：自行放入的 Avatar bundle，每个目录需要包含 `manifest.json`。

不要把包含个人肖像、声音或未授权素材的资产提交到公开仓库。
