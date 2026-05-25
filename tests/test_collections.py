import json
from pathlib import Path

import pytest

from houdini_markingmenu.core import collections


def make_item(index, context="SOP", **overrides):
    item = collections.ButtonConfig(
        context=context,
        index=index,
        is_menu=False,
        label=f"Label {index}",
        icon="MISC_python",
        collection="",
        command_type="createnode",
        command="createNode",
        node_type="null",
        active_wire=False,
    ).to_dict()
    item.update(overrides)
    return item


def make_payload(context="SOP"):
    return {"menu": [make_item(index, context=context) for index in range(8)]}


def test_button_config_matches_legacy_json_shape():
    config = collections.ButtonConfig(
        context="SOP",
        index=3,
        is_menu=True,
        label="Common",
        icon="SOP_box",
        collection="SOP_common.json",
        command_type="customfunction",
        command="_mergeSelection",
        node_type="null",
        active_wire=True,
    )

    assert config.defaultcommand == 'cmds.createNode("null", True)'
    assert config.to_dict() == {
        "context": "SOP",
        "active": 1,
        "isMenu": True,
        "label": "Common",
        "icon": "SOP_box",
        "index": 3,
        "menuCollection": "SOP_common.json",
        "nodetype": "null",
        "commandType": "customfunction",
        "activeWire": True,
        "command": "_mergeSelection",
    }


def test_context_from_houdini_category_maps_supported_contexts():
    assert collections.context_from_houdini_category("Sop") == "SOP"
    assert collections.context_from_houdini_category("Lop") == "LOP"


def test_context_from_houdini_category_rejects_unknown_context():
    with pytest.raises(collections.CollectionValidationError):
        collections.context_from_houdini_category("Unknown")


def test_filter_collections_returns_base_collection_first(tmp_path):
    for name in [
        "SOP_wrangles.json",
        "OBJ_baseCollection.json",
        "SOP_common.json",
        "SOP_baseCollection.json",
        "SOP_notes.txt",
    ]:
        (tmp_path / name).write_text("{}", encoding="utf-8")

    assert collections.filter_collections(tmp_path, "SOP") == [
        "SOP_baseCollection.json",
        "SOP_common.json",
        "SOP_wrangles.json",
    ]


def test_normalize_collection_filename_strips_context_and_extension():
    assert (
        collections.normalize_collection_filename("SOP", " SOP_custom menu.json ")
        == "SOP_custom_menu.json"
    )
    assert collections.normalize_collection_filename("VOP", "noise") == "VOP_noise.json"


def test_validate_collection_payload_requires_eight_unique_slots():
    payload = make_payload()
    payload["menu"][7]["index"] = 6

    with pytest.raises(collections.CollectionValidationError):
        collections.validate_collection_payload(payload)


def test_validate_collection_payload_rejects_missing_required_key():
    payload = make_payload()
    del payload["menu"][0]["command"]

    with pytest.raises(collections.CollectionValidationError):
        collections.validate_collection_payload(payload)


def test_load_collection_returns_empty_for_missing_file(tmp_path):
    assert collections.load_collection(tmp_path / "missing.json") == []


def test_save_collection_writes_atomically_loadable_payload(tmp_path):
    target = tmp_path / "SOP_saved.json"
    menu = make_payload()["menu"]

    collections.save_collection(target, menu)

    assert json.loads(target.read_text(encoding="utf-8")) == {"menu": menu}
    assert collections.load_collection(target) == menu
    assert not list(tmp_path.glob("*.tmp.*.json"))


def test_atomic_write_json_preserves_original_when_serialization_fails(tmp_path):
    target = tmp_path / "prefs.json"
    target.write_text('{"ok": true}\n', encoding="utf-8")

    with pytest.raises(TypeError):
        collections.atomic_write_json(target, {"bad": object()})

    assert target.read_text(encoding="utf-8") == '{"ok": true}\n'
    assert not list(tmp_path.glob("*.tmp.*.json"))


def test_bundled_collection_files_are_valid():
    menus_root = Path(__file__).parents[1] / "scripts" / "python" / "houdini_markingmenu" / "menus"
    collection_files = [
        path
        for path in menus_root.rglob("*.json")
        if path.name not in {"icons.json", "menu_prefs.json"}
    ]

    assert collection_files
    for path in collection_files:
        context = path.name.split("_", 1)[0]
        payload = json.loads(path.read_text(encoding="utf-8"))
        collections.validate_collection_payload(payload, expected_context=context)


def test_bundled_menu_preferences_reference_existing_collections():
    menus_root = Path(__file__).parents[1] / "scripts" / "python" / "houdini_markingmenu" / "menus"
    prefs = collections.load_menu_preferences(menus_root / "menu_prefs.json")

    for context, mapping in prefs.items():
        collection_names = set(collections.filter_collections(menus_root / context, context))
        assert mapping["Shift"] in collection_names
        assert mapping["Control"] in collection_names
