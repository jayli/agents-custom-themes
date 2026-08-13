---
name: nvim-colors-to-tmtheme
description: Convert Neovim/Vim colorschemes from /Users/bachi/jaylli/nvim-colors/colors into Codex-compatible TextMate .tmTheme files. Use when the user asks to convert, port, or generate a Codex CLI theme from an nvim-colors color scheme, or when working with .vim/.lua colorscheme files under that directory.
---

# Nvim Colors to tmTheme

## Overview

Convert one colorscheme from `/Users/bachi/jaylli/nvim-colors/colors` into a single `.tmTheme` file for Codex CLI.

The conversion does not rely on parsing colorscheme source files directly. It starts Neovim in headless mode, loads the requested colorscheme, dumps the resolved highlight groups through `nvim_get_hl`, and maps those groups to TextMate scopes.

## Quick Start

From the repository root of this project, run:

```sh
python3 .codex/skills/nvim-colors-to-tmtheme/scripts/convert.py \
  /Users/bachi/jaylli/nvim-colors/colors/<colorscheme> \
  --display-name "Display Name"
```

Example:

```sh
python3 .codex/skills/nvim-colors-to-tmtheme/scripts/convert.py \
  /Users/bachi/jaylli/nvim-colors/colors/night-owl.vim \
  --display-name "Night Owl"
```

Output defaults to `themes/<colorscheme>.tmTheme`. Use `--output` to override it.

## Workflow

1. Identify the source file under `/Users/bachi/jaylli/nvim-colors/colors`.
2. Derive the colorscheme name from the filename stem, e.g. `night-owl.vim` -> `night-owl`.
3. Run `scripts/convert.py` from the Codex themes project root.
4. Validate the generated XML:

```sh
xmllint --noout themes/<name>.tmTheme
```

5. Open the theme in Codex or another TextMate-compatible editor and visually check contrast and readability.

## What the Script Handles

- Plain Vim colorschemes such as `night-owl.vim` and `codedark.vim`.
- Thin Lua-backed wrappers such as `catppuccin.vim`, `kanagawa.vim`, and `tundra.lua`. These work because Neovim loads the actual runtime plugin from the nvim-colors repository root.
- Highlight-group link chains, including Neovim's default `@lsp.*` and tree-sitter link groups.

## Mapping and Customization

The core mapping from Neovim highlight groups to TextMate scopes is in `references/mapping.md`. To add or reorder a semantic mapping, edit the `SYNTAX_ENTRIES` list in `scripts/convert.py` and rerun the conversion.

## Output Conventions

- Keep one theme per file.
- Use lowercase kebab-case filenames matching the colorscheme slug.
- Keep color values as uppercase six-digit hex.
- Use `semanticClass` as `theme.<light|dark>.<slug>`.
- Preserve tabs for plist indentation.

## Troubleshooting

- If Neovim cannot load a colorscheme, ensure the `--repo` argument points to the nvim-colors repository and its runtime files are available.
- If the dump produces no output, confirm `nvim` is on `PATH` or pass `--nvim /path/to/nvim`.
- If a Lua-backed colorscheme requires external plugins, add those plugin directories to the runtime path before running the converter.
- Always rerun `xmllint` after manual edits.

## References

- [mapping.md](references/mapping.md) - highlight-group to TextMate-scope mapping, fallback order, and conversion rationale.
