import sys
from importlib.resources import files
from pathlib import Path


def resource_path(name):
    if getattr(sys, "frozen", False):
        return str(Path(sys._MEIPASS) / "pyboxshade" / "assets" / name)
    return str(files("pyboxshade").joinpath("assets", name))
