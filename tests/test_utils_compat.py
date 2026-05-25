import json
from pathlib import Path

import pytest

from houdini_markingmenu.python import utils

REPO_ROOT = Path(__file__).parents[1]


def test_legacy_utils_imports_without_houdini_or_qt():
    assert Path(utils.packageRoot()).name == "houdini_markingmenu"


def test_legacy_button_config_keeps_config_attribute():
    config = utils.ButtonConfig(
        "SOP",
        0,
        False,
        "Null",
        "SOP_null",
        "",
        "createnode",
        "createNode",
        "null",
        False,
    )

    assert config.config["context"] == "SOP"
    assert config.config["index"] == 0
    assert config.config["nodetype"] == "null"


def test_legacy_context_wrapper_uses_editor_category():
    class Category:
        def name(self):
            return "Sop"

    class Node:
        def childTypeCategory(self):
            return Category()

    class Editor:
        def pwd(self):
            return Node()

    assert utils.getContext(Editor()) == "SOP"


@pytest.mark.parametrize("version", ["3.7", "3.9", "3.10", "3.11", "3.12", "3.13"])
def test_nodegraph_hook_shims_live_in_versioned_python_libs(version):
    hook_path = REPO_ROOT / f"python{version}libs" / "nodegraphhooks.py"

    assert hook_path.is_file()
    assert "houdini_markingmenu.nodegraphhooks" in hook_path.read_text(encoding="utf-8")


def test_nodegraph_hook_is_not_top_level_scripts_python_module():
    assert not (REPO_ROOT / "scripts" / "python" / "nodegraphhooks.py").exists()
    assert (REPO_ROOT / "scripts" / "python" / "houdini_markingmenu" / "nodegraphhooks.py").is_file()


def test_houdini_package_loads_pythonpath_and_hpath():
    package_data = json.loads((REPO_ROOT / "houdini_markingmenu.json").read_text(encoding="utf-8"))

    assert package_data["hpath"] == "$HOUDINI_MARKINGMENU"
    assert {
        "var": "PYTHONPATH",
        "value": "$HOUDINI_MARKINGMENU/scripts/python",
        "method": "prepend",
    } in package_data["env"]
