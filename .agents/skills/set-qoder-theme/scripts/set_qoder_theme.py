#!/usr/bin/env python3
"""Sync a Qoder CLI custom theme JSON into the global Qoder config."""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def default_config_root() -> Path:
    return Path(os.environ.get("QODER_CONFIG_ROOT") or Path.home() / ".qoder").expanduser()


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("theme_file", type=Path, help="Path to the Qoder theme JSON file")
    parser.add_argument(
        "--config-root",
        type=Path,
        default=None,
        help="Qoder config root (default: $QODER_CONFIG_ROOT or ~/.qoder)",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    theme_file = args.theme_file.expanduser().resolve()
    if not theme_file.is_file():
        print(f"error: theme file not found: {theme_file}", file=sys.stderr)
        return 1

    theme = load_json(theme_file)
    if not isinstance(theme, dict):
        print("error: theme file must contain a JSON object", file=sys.stderr)
        return 1
    name = theme.get("name")
    if not isinstance(name, str) or not name.strip():
        print('error: theme must have a non-empty "name"', file=sys.stderr)
        return 1

    config_root = (args.config_root or default_config_root()).expanduser().resolve()
    settings_path = config_root / "settings.json"
    themes_dir = config_root / "themes"

    # 1. Sync the file into the global theme directory (following symlinks).
    destination = (themes_dir / theme_file.name).resolve()
    if destination != theme_file:
        themes_dir.resolve().mkdir(parents=True, exist_ok=True)
        shutil.copy2(theme_file, destination)
        file_status = "copied"
    else:
        file_status = "already in place"

    # 2. Update the effective config in settings.json.
    if not settings_path.is_file():
        print(
            f"error: {settings_path} not found; run qoder once or create it first",
            file=sys.stderr,
        )
        return 1

    settings = load_json(settings_path)
    if not isinstance(settings, dict):
        print("error: settings.json must contain a JSON object", file=sys.stderr)
        return 1

    ui = settings.setdefault("ui", {})
    custom_themes = ui.get("customThemes")
    if custom_themes is None:
        custom_themes = {}
        ui["customThemes"] = custom_themes
    if not isinstance(custom_themes, dict):
        print('error: ui.customThemes must be a JSON object', file=sys.stderr)
        return 1

    old_theme = custom_themes.get(name)
    custom_themes[name] = theme
    ui["theme"] = name

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = settings_path.with_name(f"settings.json.bak-set-qoder-theme-{stamp}")
    shutil.copy2(settings_path, backup)

    temporary = settings_path.with_name(f"{settings_path.name}.tmp")
    temporary.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, settings_path)

    print(f"theme: {name}")
    print(f"global theme file: {file_status}")
    print(f'ui.theme -> "{name}"')
    print(f'ui.customThemes["{name}"]: {"updated" if old_theme != theme else "unchanged"}')
    print(f"backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
