# Repository Guidelines

This repository contains CLI themes for Codex. Each theme is a single `.tmTheme` XML plist under `themes/`.

## Project Structure

- `README.md` — short project overview.
- `themes/` — all theme files, one file per theme.

Name theme files in lowercase kebab-case and match the display name, for example `themes/tomorrow-night.tmTheme`.

## Adding or Editing a Theme

Use the existing `tomorrow-night.tmTheme` as a template. A valid theme includes:

- Metadata such as `name`, `author`, `semanticClass`, and `colorSpace`.
- A leading `settings` entry that defines the global palette: `background`, `foreground`, `caret`, `selection`, `lineHighlight`, and `invisibles`.
- Additional `settings` entries that map syntax scopes to `foreground`, `background`, or `fontStyle`.

When adding a theme, also add a short link or mention in `README.md`.

## Build, Test, and Development Commands

There is no build system or automated test suite. Validate theme files locally before committing:

```sh
xmllint --noout themes/tomorrow-night.tmTheme
```

For a new theme, replace the filename:

```sh
xmllint --noout themes/<theme-name>.tmTheme
```

Then open the theme in Codex or another TextMate-compatible editor to confirm that syntax highlighting and the global palette render correctly.

## Coding Style & Naming Conventions

- Use tabs for plist indentation, matching the existing files.
- Keep color values as uppercase six-digit hex, such as `#C5C8C6`.
- Set `semanticClass` to `theme.<light|dark>.<slug>`.
- Separate multiple scopes with commas and reuse existing scope names where possible.

## Testing Guidelines

Manual verification is required because no automated tests exist. After editing, re-run `xmllint` and visually check a representative code sample for readability and contrast.

## Commit & Pull Request Guidelines

- Use short imperative commit summaries, such as `Add Tomorrow Night theme`.
- Submit one theme per pull request.
- Describe the theme name, palette source, and scope changes.
- Include a screenshot showing the theme applied.
