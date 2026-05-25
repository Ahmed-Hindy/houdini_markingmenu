"""Pure collection loading, validation, and persistence helpers."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

CONTEXT_MAPPING = {
    "Sop": "SOP",
    "Dop": "DOP",
    "Object": "OBJ",
    "Driver": "ROP",
    "Chop": "CHOP",
    "Vop": "VOP",
    "Shop": "SHOP",
    "Cop2": "COP",
    "Lop": "LOP",
}

CONTEXTS = tuple(sorted(CONTEXT_MAPPING.values()))

MENU_ITEM_KEYS = {
    "context",
    "active",
    "isMenu",
    "label",
    "icon",
    "index",
    "menuCollection",
    "nodetype",
    "commandType",
    "activeWire",
    "command",
}


class CollectionValidationError(ValueError):
    """Raised when a marking-menu collection has an invalid structure."""


@dataclass
class ButtonConfig:
    """Serializable description of one marking-menu button."""

    context: str
    index: int
    is_menu: bool
    label: str
    icon: str
    collection: str
    command_type: str
    command: str
    node_type: str
    active_wire: bool
    active: int = 1

    @property
    def defaultcommand(self):
        """Return the legacy default command string for this button."""
        return f'cmds.createNode("{self.node_type}", {self.active_wire})'

    def to_dict(self):
        """Return this button config as the legacy JSON dictionary shape."""
        return {
            "context": self.context,
            "active": self.active,
            "isMenu": self.is_menu,
            "label": self.label,
            "icon": self.icon,
            "index": self.index,
            "menuCollection": self.collection,
            "nodetype": self.node_type,
            "commandType": self.command_type,
            "activeWire": self.active_wire,
            "command": self.command,
        }


def package_root_from_env(env):
    """Return a package root from an environment mapping, if configured."""
    root = env.get("HOUDINI_MARKINGMENU")
    if not root:
        return None
    return Path(root)


def context_from_houdini_category(category_name):
    """Return the marking-menu context name for a Houdini category name."""
    try:
        return CONTEXT_MAPPING[category_name]
    except KeyError as error:
        raise CollectionValidationError(
            f"Unsupported Houdini node category: {category_name}"
        ) from error


def filter_collections(path, context):
    """Return sorted collection JSON filenames for a context, base first."""
    directory = Path(path)
    filtered = sorted(
        (
            child.name
            for child in directory.iterdir()
            if child.suffix == ".json" and child.name.split("_", 1)[0] == context
        ),
        key=str.lower,
    )
    base_name = f"{context}_baseCollection.json"
    if base_name in filtered:
        filtered.remove(base_name)
        filtered.insert(0, base_name)
    return filtered


def load_json(path):
    """Load JSON data from path."""
    with Path(path).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def atomic_write_json(path, data):
    """Write JSON data atomically beside the target file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f"{target.name}.tmp.",
        suffix=".json",
        dir=str(target.parent),
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, indent=4, sort_keys=True)
            stream.write("\n")
        os.replace(temp_name, str(target))
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def validate_menu_item(item, expected_context=None):
    """Validate one menu item dictionary."""
    if not isinstance(item, Mapping):
        raise CollectionValidationError("Menu item must be a JSON object.")

    missing = sorted(MENU_ITEM_KEYS.difference(item))
    if missing:
        raise CollectionValidationError(
            "Menu item is missing keys: {}".format(", ".join(missing))
        )

    index = item["index"]
    if not isinstance(index, int) or index < 0 or index > 7:
        raise CollectionValidationError("Menu item index must be an integer 0-7.")

    if expected_context is not None and item["context"] != expected_context:
        raise CollectionValidationError(
            "Menu item context {!r} does not match {!r}.".format(
                item["context"], expected_context
            )
        )

    if item["commandType"] not in {"createnode", "customfunction"}:
        raise CollectionValidationError(
            "Unsupported commandType: {!r}.".format(item["commandType"])
        )


def validate_collection_payload(payload, expected_context=None):
    """Validate a complete collection JSON payload."""
    if not isinstance(payload, Mapping):
        raise CollectionValidationError("Collection payload must be a JSON object.")
    menu = payload.get("menu")
    if not isinstance(menu, list):
        raise CollectionValidationError("Collection payload must contain a menu list.")
    if len(menu) != 8:
        raise CollectionValidationError("Collection menu must contain exactly 8 items.")

    seen = set()
    for item in menu:
        validate_menu_item(item, expected_context=expected_context)
        seen.add(item["index"])
    if seen != set(range(8)):
        raise CollectionValidationError("Collection indexes must be exactly 0-7.")
    return menu


def load_menu_preferences(path):
    """Return menu preference data from JSON."""
    return load_json(path)


def save_menu_preferences(path, data):
    """Save menu preference data atomically."""
    if not isinstance(data, Mapping):
        raise CollectionValidationError("Menu preferences must be a JSON object.")
    atomic_write_json(path, data)


def load_collection(path):
    """Return the menu item list from a collection JSON file."""
    collection = Path(path)
    if not collection.is_file():
        return []
    return validate_collection_payload(load_json(collection))


def save_collection(path, data):
    """Save menu item data to a collection JSON file atomically."""
    payload = {"menu": list(data)}
    validate_collection_payload(payload)
    atomic_write_json(path, payload)


def normalize_collection_filename(context, name):
    """Normalize user text into a context-prefixed collection JSON filename."""
    normalized = name.strip(" ").replace(" ", "_")
    prefix = f"{context}_"
    if normalized.startswith(prefix):
        normalized = normalized[len(prefix) :]
    if normalized.endswith(".json"):
        normalized = normalized[: -len(".json")]
    return f"{prefix}{normalized}.json"
