#!/usr/bin/env python3
"""Convert an nvim-colors colorscheme to a Codex/TextMate .tmTheme file.

The conversion uses Neovim in headless mode so it works for both plain
Vim colorschemes and Lua-backed ones that require runtime plugin code.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from xml.sax.saxutils import escape


DEFAULT_NVIM_REPO = "/Users/bachi/jaylli/nvim-colors"
DEFAULT_OUTPUT_DIR = "themes"


# Ordered group names provide a fallback chain. Each entry maps a TextMate
# scope to the Neovim highlight groups that should provide its color.
SYNTAX_ENTRIES = [
    {
        "name": "Comment",
        "scopes": "comment",
        "groups": ["Comment", "jsComment", "javaScriptLineComment", "shComment"],
    },
    {
        "name": "operator",
        "scopes": "keyword.operator.class, keyword.operator, constant.other, source.php.embedded.line",
        "groups": ["Operator", "Special", "Delimiter", "NvimOperator"],
    },
    {
        "name": "variable-string-link-regex-tag",
        "scopes": "variable, support.other.variable, string.other.link, string.regexp, entity.name.tag, entity.other.attribute-name",
        "groups": ["Identifier", "Tag", "Special", "Label", "jsObjectProp"],
    },
    {
        "name": "number-constant-function-argument",
        "scopes": "constant.numeric, constant.language, support.constant, constant.character, variable.parameter, punctuation.section.embedded",
        "groups": ["Constant", "Number", "Boolean", "Float", "Character"],
    },
    {
        "name": "class-support",
        "scopes": "entity.name.class, entity.name.type.class, support.type, support.class",
        "groups": ["Type", "Structure", "Typedef", "StorageClass"],
    },
    {
        "name": "string-symbol-heading",
        "scopes": "string, constant.other.symbol, entity.other.inherited-class, markup.heading",
        "groups": ["String", "Character", "SpecialChar", "Regexp"],
    },
    {
        "name": "function",
        "scopes": "entity.name.function, meta.function-call, support.function, keyword.other.special-method, meta.block-level",
        "groups": ["Function", "Identifier", "jsFunction", "jsFuncName", "jsFuncCall", "Support"],
    },
    {
        "name": "keyword-storage",
        "scopes": "keyword, storage, storage.type",
        "groups": ["Keyword", "StorageClass", "Statement", "Conditional", "Repeat", "Label"],
    },
    {
        "name": "Invalid",
        "scopes": "invalid",
        "groups": ["Error", "ErrorMsg", "DiagnosticError", "DiagnosticFloatingError"],
    },
    {
        "name": "Separator",
        "scopes": "meta.separator",
        "groups": ["Delimiter", "Conceal", "SpecialKey", "Whitespace", "NonText"],
    },
    {
        "name": "Deprecated",
        "scopes": "invalid.deprecated",
        "groups": ["DiagnosticDeprecated", "Error", "WarningMsg"],
    },
    {
        "name": "markup-heading-bold-changed-diff",
        "scopes": "markup.heading, markup.bold, markup.changed, markup.inserted.diff, markup.deleted.diff",
        "groups": ["Title", "htmlH1", "htmlBold", "DiffChange", "DiffText"],
    },
    {
        "name": "json-yaml-keys",
        "scopes": "support.type.property-name.json, string.unquoted.plain.out.yaml, entity.name.tag.yaml",
        "groups": ["Identifier", "PreProc", "Statement", "Tag"],
    },
    {
        "name": "shell-and-cli",
        "scopes": "support.function.builtin.shell, variable.other.normal.shell, string.interpolated.shell",
        "groups": ["Special", "String", "Function", "Identifier"],
    },
    {
        "name": "diagnostics",
        "scopes": "invalid.illegal, markup.deleted, message.error, markup.warning",
        "groups": ["Error", "DiagnosticError", "WarningMsg", "DiagnosticWarn"],
    },
]


def resolve_highlight(highlights: dict, group: str) -> dict:
    """Resolve a Neovim highlight group, following `link` chains."""
    seen: set[str] = set()
    current = group
    while current in highlights:
        if current in seen:
            break
        seen.add(current)
        entry = highlights[current]
        if "link" in entry:
            current = entry["link"]
            continue
        return entry
    return {}


def to_hex(value) -> str | None:
    """Convert a Neovim color value to uppercase six-digit hex."""
    if value is None:
        return None
    if isinstance(value, int):
        return f"#{value:06X}"
    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() == "none":
            return None
        if text.startswith("#"):
            if re.fullmatch(r"#[0-9a-fA-F]{6}", text):
                return text.upper()
            if re.fullmatch(r"#[0-9a-fA-F]{3}", text):
                r, g, b = text[1], text[2], text[3]
                return f"#{r * 2}{g * 2}{b * 2}".upper()
            return None
    return None


def first_color(highlights: dict, groups: list[str], field: str) -> str | None:
    for group in groups:
        resolved = resolve_highlight(highlights, group)
        color = to_hex(resolved.get(field))
        if color:
            return color
    return None


def font_style_for(highlights: dict, groups: list[str]) -> str | None:
    for group in groups:
        resolved = resolve_highlight(highlights, group)
        if "fg" not in resolved:
            continue
        styles: list[str] = []
        if resolved.get("bold"):
            styles.append("bold")
        if resolved.get("italic"):
            styles.append("italic")
        if resolved.get("underline"):
            styles.append("underline")
        if styles:
            return " ".join(styles)
        return None
    return None


def dump_highlights(nvim: str, repo: str, colorscheme: str) -> dict:
    """Run Neovim headlessly and return its complete highlight dump."""
    lua = (
        "lua local hl=vim.api.nvim_get_hl(0,{}); "
        "io.stdout:write(vim.json.encode({colors_name=vim.g.colors_name, highlights=hl}))"
    )
    cmd = [
        nvim,
        "--headless",
        "-u",
        "NONE",
        "--cmd",
        f"set rtp^={repo}",
        "-c",
        f"colorscheme {colorscheme}",
        "-c",
        lua,
        "-c",
        "qa!",
    ]
    try:
        proc = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=repo,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Neovim could not load the colorscheme. "
            f"stderr:\n{exc.stderr.strip()}\nstdout:\n{exc.stdout.strip()}"
        ) from exc

    output = proc.stdout.strip()
    if not output:
        raise RuntimeError("Neovim produced no highlight dump.")
    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse Neovim JSON output: {output[:500]}") from exc
    if "highlights" not in data:
        raise RuntimeError("Neovim JSON output did not contain `highlights`.")
    return data


def luminance(hex_color: str) -> float:
    r = int(hex_color[1:3], 16) / 255
    g = int(hex_color[3:5], 16) / 255
    b = int(hex_color[5:7], 16) / 255
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "converted-theme"


def build_tmtheme(
    data: dict,
    *,
    source_name: str,
    display_name: str | None,
    author: str,
) -> str:
    highlights = data.get("highlights", {})
    colorscheme = data.get("colors_name") or source_name
    slug = slugify(source_name)

    foreground = first_color(highlights, ["Normal"], "fg") or "#D4D4D4"
    background = first_color(highlights, ["Normal"], "bg") or "#1E1E1E"
    caret = foreground
    selection = first_color(highlights, ["Visual", "PmenuSel", "Search"], "bg") or "#264F78"
    line_highlight = first_color(highlights, ["CursorLine", "CursorLineNr", "ColorColumn"], "bg") or background
    invisibles = foreground
    for group in ("NonText", "SpecialKey", "Whitespace", "Comment", "LineNr"):
        candidate = first_color(highlights, [group], "fg")
        if candidate and candidate.lower() != background.lower():
            invisibles = candidate
            break

    palette = {
        "background": background,
        "caret": caret,
        "foreground": foreground,
        "invisibles": invisibles,
        "lineHighlight": line_highlight,
        "selection": selection,
    }

    mode = "light" if luminance(background) > 0.5 else "dark"
    name = display_name or source_name.replace("_", "-").replace("-", " ").title()
    comment = f"{name} converted from {colorscheme}"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        '<plist version="1.0">',
        "\t<dict>",
        "\t\t<key>comment</key>",
        f"\t\t<string>{escape(comment)}</string>",
        "\t\t<key>name</key>",
        f"\t\t<string>{escape(name)}</string>",
        "\t\t<key>author</key>",
        f"\t\t<string>{escape(author)}</string>",
        "\t\t<key>semanticClass</key>",
        f"\t\t<string>theme.{mode}.{slug}</string>",
        "\t\t<key>colorSpace</key>",
        "\t\t<string>sRGB</string>",
        "\t\t<key>settings</key>",
        "\t\t<array>",
        "\t\t\t<dict>",
        "\t\t\t\t<key>settings</key>",
        "\t\t\t\t<dict>",
    ]
    for key in ("background", "caret", "foreground", "invisibles", "lineHighlight", "selection"):
        lines.extend(
            [
                f"\t\t\t\t\t<key>{key}</key>",
                f"\t\t\t\t\t<string>{escape(palette[key])}</string>",
            ]
        )
    lines.extend(
        [
            "\t\t\t\t</dict>",
            "\t\t\t</dict>",
        ]
    )

    for entry in SYNTAX_ENTRIES:
        color = first_color(highlights, entry["groups"], "fg")
        if not color:
            continue
        lines.extend(
            [
                "\t\t\t<dict>",
                "\t\t\t\t<key>name</key>",
                f"\t\t\t\t<string>{escape(entry['name'])}</string>",
                "\t\t\t\t<key>scope</key>",
                f"\t\t\t\t<string>{escape(entry['scopes'])}</string>",
                "\t\t\t\t<key>settings</key>",
                "\t\t\t\t<dict>",
            ]
        )
        style = font_style_for(highlights, entry["groups"])
        if style:
            lines.extend(
                [
                    "\t\t\t\t\t<key>fontStyle</key>",
                    f"\t\t\t\t\t<string>{escape(style)}</string>",
                ]
            )
        lines.extend(
            [
                "\t\t\t\t\t<key>foreground</key>",
                f"\t\t\t\t\t<string>{escape(color)}</string>",
                "\t\t\t\t</dict>",
                "\t\t\t</dict>",
            ]
        )

    diff_add_bg = first_color(highlights, ["DiffAdd", "Added"], "bg")
    diff_delete_bg = first_color(highlights, ["DiffDelete", "Removed"], "bg")
    if diff_add_bg:
        lines.extend(_diff_entry("Diff Inserted", "markup.inserted", "background", diff_add_bg))
    if diff_delete_bg:
        lines.extend(_diff_entry("Diff Deleted", "markup.deleted", "background", diff_delete_bg))

    lines.extend(
        [
            "\t\t</array>",
            "\t\t<key>uuid</key>",
            f"\t\t<string>{uuid.uuid4().hex.upper()}</string>",
            "\t</dict>",
            "</plist>",
            "",
        ]
    )
    return "\n".join(lines)


def _diff_entry(name: str, scope: str, key: str, value: str) -> list[str]:
    return [
        "\t\t\t<dict>",
        "\t\t\t\t<key>name</key>",
        f"\t\t\t\t<string>{escape(name)}</string>",
        "\t\t\t\t<key>scope</key>",
        f"\t\t\t\t<string>{escape(scope)}</string>",
        "\t\t\t\t<key>settings</key>",
        "\t\t\t\t<dict>",
        f"\t\t\t\t\t<key>{key}</key>",
        f"\t\t\t\t\t<string>{escape(value)}</string>",
        "\t\t\t\t</dict>",
        "\t\t\t</dict>",
    ]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert an nvim-colors colorscheme into a .tmTheme file."
    )
    parser.add_argument("source", help="Path to a colorscheme file under nvim-colors/colors.")
    parser.add_argument(
        "-o",
        "--output",
        help="Output .tmTheme path. Defaults to themes/<colorscheme>.tmTheme.",
    )
    parser.add_argument(
        "--repo",
        default=DEFAULT_NVIM_REPO,
        help=f"Path to the nvim-colors repository. Defaults to {DEFAULT_NVIM_REPO}.",
    )
    parser.add_argument(
        "--nvim",
        default="nvim",
        help="Path to the nvim executable.",
    )
    parser.add_argument(
        "--display-name",
        help="Human-facing theme name. Defaults to a title-cased source filename.",
    )
    parser.add_argument(
        "--author",
        default="nvim-colors",
        help="Author string for the generated tmTheme.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    source = Path(args.source).expanduser().resolve()
    if not source.is_file():
        print(f"Source file not found: {source}", file=sys.stderr)
        return 1

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        print(f"nvim-colors repository not found: {repo}", file=sys.stderr)
        return 1

    colorscheme = source.stem
    data = dump_highlights(args.nvim, str(repo), colorscheme)
    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else Path(DEFAULT_OUTPUT_DIR) / f"{slugify(colorscheme)}.tmTheme"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    content = build_tmtheme(
        data,
        source_name=colorscheme,
        display_name=args.display_name,
        author=args.author,
    )
    output.write_text(content)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
