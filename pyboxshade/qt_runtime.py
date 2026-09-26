from pathlib import Path

import PyQt5
from PyQt5.QtCore import QCoreApplication


def configure_qt():
    # PyQt5's compiled prefix can lose non-ASCII characters on Windows.
    root = Path(PyQt5.__file__).resolve().parent
    candidates = (root / "Qt5" / "plugins", root / "Qt" / "plugins")
    for plugins in candidates:
        if plugins.is_dir():
            QCoreApplication.setLibraryPaths([str(plugins)])
            return
    raise RuntimeError("Qt platform plugins are missing. Reinstall PyQt5 or restore the complete application folder.")
