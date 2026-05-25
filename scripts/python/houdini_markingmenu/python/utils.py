from math import sqrt

from houdini_markingmenu.core import collections
from houdini_markingmenu.core.paths import get_package_root


class ButtonConfig(collections.ButtonConfig):
    """Create a button object using the legacy constructor signature."""

    def __init__(
            self,
            context,
            index,
            isMenu,
            label,
            icon,
            collection,
            commandType,
            command,
            nodetype,
            activeWire):

        super(ButtonConfig, self).__init__(
            context=context,
            index=index,
            is_menu=isMenu,
            label=label,
            icon=icon,
            collection=collection,
            command_type=commandType,
            command=command,
            node_type=nodetype,
            active_wire=activeWire,
        )
        self.config = self.to_dict()


def packageRoot():
    """Return the root path for bundled menu resources."""
    return str(get_package_root())


def filterCollections(path, context):
    """Return a list of collection strings that match context."""
    return collections.filter_collections(path, context)


def loadMenuPreferences(path):
    """Return dictionary of menu preference json file."""
    return collections.load_menu_preferences(path)


def saveMenuPreferences(path, data):
    """Save menu preference data to json file atomically."""
    collections.save_menu_preferences(path, data)


def loadCollection(collection):
    """Return dictionary list from json file collection."""
    return collections.load_collection(collection)


def saveCollection(collection, data):
    """Save dictionary list data to json file collection."""
    collections.save_collection(collection, data)


def normalizeCollectionFilename(context, name):
    """Normalize user text into a collection JSON filename."""
    return collections.normalize_collection_filename(context, name)


def getContext(editor):
    """Return houdini context string."""
    hou_context = editor.pwd().childTypeCategory().name()
    return collections.context_from_houdini_category(hou_context)


def buildCompleter(jsonfile):
    """Create QCompleter from jsonfile."""
    from houdini_markingmenu.qt import QtWidgets
    import hou

    strlist = []
    jsondict = collections.load_json(jsonfile)

    for x in jsondict.keys():
        for item in jsondict[x]:
            strlist.append(item)

    comp = QtWidgets.QCompleter(strlist)
    comp.popup().setStyleSheet(hou.qt.styleSheet())
    comp.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
    return comp


def pointRectDist(pos, rect):
    """Calculate the distance from a point to a rectangle.

    Keyword arguments:
    pos -- position (type QtCore.QPoint)
    rect -- rectangle (type QtCore.QRect)
    """
    x = pos.x()
    y = pos.y()
    rx = rect.topLeft().x()
    ry = rect.topLeft().y()
    width = rect.width()
    height = rect.height()
    cx = max(min(x, rx+width), rx)
    cy = max(min(y, ry+height), ry)
    return sqrt((x - cx)*(x - cx) + (y - cy)*(y - cy))


def qpDist(pt0, pt1):
    """Calculate the distance between 2 vectors.

    pt0, pt1 -- type QtCore.QPoint
    """
    return sqrt((pt0.x() - pt1.x()) ** 2 + (pt0.y() - pt1.y()) ** 2)
