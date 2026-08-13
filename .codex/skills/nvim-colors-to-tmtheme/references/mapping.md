# Highlight Group to TextMate Scope Mapping

This file documents the mapping used by `scripts/convert.py`. The script resolves Neovim highlight groups from a headless dump, then chooses the first group in each ordered list that supplies a foreground or background color.

## Global Palette

| tmTheme key | Neovim fallback order |
| --- | --- |
| `background` | `Normal` bg |
| `foreground` | `Normal` fg |
| `caret` | `Normal` fg |
| `selection` | `Visual` bg, `PmenuSel` bg, `Search` bg |
| `lineHighlight` | `CursorLine` bg, `CursorLineNr` bg, `ColorColumn` bg |
| `invisibles` | `NonText` fg, `SpecialKey` fg, `Whitespace` fg, `Comment` fg, `LineNr` fg, skipping the background color |

## Syntax Scopes

| tmTheme scope | Neovim fallback order |
| --- | --- |
| `comment` | `Comment`, `jsComment`, `javaScriptLineComment`, `shComment` |
| `keyword.operator...` | `Operator`, `Special`, `Delimiter`, `NvimOperator` |
| `variable...` | `Identifier`, `Tag`, `Special`, `Label`, `jsObjectProp` |
| `constant.numeric...` | `Constant`, `Number`, `Boolean`, `Float`, `Character` |
| `entity.name.class...` | `Type`, `Structure`, `Typedef`, `StorageClass` |
| `string...` | `String`, `Character`, `SpecialChar`, `Regexp` |
| `entity.name.function...` | `Function`, `Identifier`, `jsFunction`, `jsFuncName`, `jsFuncCall`, `Support` |
| `keyword, storage...` | `Keyword`, `StorageClass`, `Statement`, `Conditional`, `Repeat`, `Label` |
| `invalid` | `Error`, `ErrorMsg`, `DiagnosticError`, `DiagnosticFloatingError` |
| `meta.separator` | `Delimiter`, `Conceal`, `SpecialKey`, `Whitespace`, `NonText` |
| `invalid.deprecated` | `DiagnosticDeprecated`, `Error`, `WarningMsg` |
| markup/diff heading | `Title`, `htmlH1`, `htmlBold`, `DiffChange`, `DiffText` |
| JSON/YAML keys | `Identifier`, `PreProc`, `Statement`, `Tag` |
| shell/CLI | `Special`, `String`, `Function`, `Identifier` |
| diagnostics | `Error`, `DiagnosticError`, `WarningMsg`, `DiagnosticWarn` |

## Diff Backgrounds

`markup.inserted` uses `DiffAdd` bg and `markup.deleted` uses `DiffDelete` bg when available. A color is skipped when the resolved group does not provide that field.

## Why Headless Neovim

Static parsing of `.vim` files misses runtime definitions, `hi link` chains, Lua plugin configuration, and tree-sitter default links. Headless Neovim resolves all of those before the converter runs, so the same script works for plain Vim and Lua-backed colorschemes.
