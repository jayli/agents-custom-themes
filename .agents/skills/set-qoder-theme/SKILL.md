---
name: set-qoder-theme
description: 把用户指定的 Qoder CLI 自定义皮肤 JSON 文件安装或更新到全局配置：同步到 ~/.qoder/themes，并写入 ~/.qoder/settings.json 的 ui.customThemes 与 ui.theme。仅用于 Qoder CLI 的 JSON 皮肤，不用于 Codex 的 .tmTheme 皮肤。
---

# 设置 Qoder 自定义皮肤

把用户指定的 Qoder CLI 皮肤文件应用到全局配置。

Qoder 皮肤的实际生效位置是 `~/.qoder/settings.json`：`ui.theme` 是当前皮肤名，`ui.customThemes` 保存各皮肤的定义；`~/.qoder/themes/` 是皮肤的全局存放目录，本机通常是指向仓库 `qoder/themes/` 的符号链接。

## 必需的输入

必须由用户指定要被设置的皮肤文件（例如 `qoder/themes/codedark.json`）。如果用户没有给出文件路径，先停下来询问，不要改动任何配置。

## 操作步骤

1. 确认指定的文件存在、是合法 JSON，且包含非空的 `name` 字段。
2. 执行：

   ```bash
   python3 .agents/skills/set-qoder-theme/scripts/set_qoder_theme.py <皮肤文件路径>
   ```

3. 脚本会：
   - 把文件同步到全局皮肤目录 `~/.qoder/themes/`；若文件本来就通过符号链接位于该目录内，则跳过复制；
   - 修改前自动备份 `~/.qoder/settings.json`；
   - 用文件内容覆盖 `ui.customThemes["<name>"]`，并把 `ui.theme` 设为 `<name>`，其他配置保持不动。

## 约束

- 只改动用户指定的皮肤文件和 Qoder 全局配置，不顺手修改无关设置。
- 保留 `ui.customThemes` 中其他皮肤的定义。
- 改完后校验 JSON 合法性，并告诉用户改了什么；用户在 Qoder 里运行 `/theme` 或重启后即可看到效果。

## 排他范围

- 只处理 Qoder CLI 的 JSON 皮肤。Codex 的 `.tmTheme` 皮肤走 `nvim-colors-to-tmtheme` 技能。
