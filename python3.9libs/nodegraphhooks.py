"""Houdini network editor hook shim for Python 3.9 builds."""

from houdini_markingmenu.nodegraphhooks import buildHandler, createEventHandler

__all__ = ["buildHandler", "createEventHandler"]
