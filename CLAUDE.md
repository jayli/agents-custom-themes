# CLAUDE.md

This file provides guidance to the AI agent when working with code in this repository.

## Project layout

Theme files live in `codex/themes/`, not `themes/` (the README and AGENTS.md paths are outdated). New themes must be added under `codex/themes/<slug>.tmTheme`.

## Converting themes

To generate a theme from a Neovim colorscheme in `/Users/bachi/jaylli/nvim-colors/colors`, run:

```sh
python3 .codex/skills/nvim-colors-to-tmtheme/scripts/convert.py \
  /Users/bachi/jaylli/nvim-colors/colors/<name>.vim \
  --display-name "Display Name"
```

The script writes to `themes/<slug>.tmTheme` by default; move or adjust `--output` to place the result under `codex/themes/`.

## Validating themes

There is no automated test suite. Before committing, validate XML with:

```sh
xmllint --noout codex/themes/<name>.tmTheme
```

Then visually verify the theme in a TextMate-compatible editor.

## Theme conventions

- Store one theme per file in `codex/themes/`.
- Use lowercase kebab-case filenames matching the display name slug.
- Indent plist XML with tabs, not spaces.
- Keep hex colors uppercase and six digits, e.g. `#C5C8C6`.
- Set `semanticClass` to `theme.<light|dark>.<slug>`.
- Separate multiple scopes with commas.
- Reuse existing scope names where possible.

## Commits

Use short imperative summaries. Common prefixes are `feat(themes):`, `style(theme):`, or `fix(themes):` when changing theme colors or adding themes.
