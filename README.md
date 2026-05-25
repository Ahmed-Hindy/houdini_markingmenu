# houdini_markingmenu

Marking menu tools for the Houdini network editor. The package provides quick
access to node creation, node placement, tool scripts, shelf tools, and editable
JSON menu collections.

![Image of the Menu and Editor](/scripts/python/houdini_markingmenu/docs/mm_screenshot.jpg?raw=true)

Demo video: https://vimeo.com/251253577

## Compatibility

- Houdini 18.5+ py3 should be able to load the neutral `scripts/python` package
  code when the package file adds that folder to `PYTHONPATH`.
- The Python source is kept compatible with Python 3.7 through 3.13 syntax.
- supports `Qt5` and `Qt6` flavors of Houdini.


## Installation

1. Copy `houdini_markingmenu.json` into `$HOUDINI_USER_PREF_DIR/packages`.
2. Edit `HOUDINI_MARKINGMENU` in the copied package file so it points to this
   repository root.

Example:

```json
{
    "HOUDINI_MARKINGMENU": "G:/Projects/Dev/Github/houdini_markingmenu"
}
```


## Development

This repository uses `uv` for local tooling.

```powershell
uv sync --extra dev
uv run pytest
uv run ruff check .
```
