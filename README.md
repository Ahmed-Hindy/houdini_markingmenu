# houdini_markingmenu

Marking menu tools for the Houdini network editor. The package provides quick
access to node creation, node placement, tool scripts, shelf tools, and editable
JSON menu collections.

![Image of the Menu and Editor](/scripts/python/houdini_markingmenu/docs/mm_screenshot.jpg?raw=true)

Demo video: https://vimeo.com/251253577

## Compatibility

- Houdini 18.5+ should be able to load the neutral `scripts/python` package
  code when the package file adds that folder to `PYTHONPATH`.
- The top-level network-editor hook remains in versioned `pythonX.Ylibs`
  folders because Houdini discovers `nodegraphhooks.py` from the active Python
  version folder. Those files are thin shims into the neutral package code.
- Houdini 21 uses Python 3.11, Qt 6, and PySide6. UI modules import through the
  bundled `houdini_markingmenu.qt` compatibility shim, which prefers Qt.py and
  falls back to PySide6 or PySide2.
- The Python source is kept compatible with Python 3.7 through 3.13 syntax.

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

The package file prepends `$HOUDINI_MARKINGMENU/scripts/python` to `PYTHONPATH`
and adds `$HOUDINI_MARKINGMENU` to Houdini's path with `hpath`, allowing Houdini
to find the matching `pythonX.Ylibs/nodegraphhooks.py` shim.

## Development

This repository uses `uv` for local tooling.

```powershell
uv sync --extra dev
uv run pytest
uv run ruff check .
```
