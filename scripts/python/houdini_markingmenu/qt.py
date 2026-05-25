"""Qt compatibility imports for Houdini and local development.

The preferred path is Qt.py because it is bundled with recent Houdini builds
and smooths over PySide/PyQt binding differences. Direct PySide imports are
kept as fallbacks for older Houdini installs and lightweight test environments.
"""

try:
    from Qt import QtCore, QtGui, QtTest, QtWidgets
except ImportError:
    try:
        from PySide6 import QtCore, QtGui, QtTest, QtWidgets
    except ImportError:
        from PySide2 import QtCore, QtGui, QtTest, QtWidgets
