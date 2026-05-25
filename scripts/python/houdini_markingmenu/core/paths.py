"""Filesystem path helpers for package resources."""

from pathlib import Path


def get_package_root():
    """Return the root directory of the importable Houdini package."""
    return Path(__file__).resolve().parents[1]


def get_menus_root():
    """Return the bundled marking-menu collection directory."""
    return get_package_root() / "menus"
