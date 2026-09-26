import os
import sys

os.environ["QT_QPA_PLATFORM"] = "windows" if sys.platform == "win32" else "offscreen"

import pytest
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from BS_app import set_defaults
from pyboxshade.qt_runtime import configure_qt
from pyboxshade.settings import new_settings


@pytest.fixture(scope="session")
def app():
    configure_qt()
    instance = QApplication.instance() or QApplication([])
    yield instance


@pytest.fixture(autouse=True)
def preferences(app, tmp_path):
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    QSettings.setPath(QSettings.IniFormat, QSettings.SystemScope, str(tmp_path))
    settings = new_settings()
    settings.setFallbacksEnabled(False)
    set_defaults()
    yield settings


@pytest.fixture
def alignment_path(tmp_path):
    path = tmp_path / "对齐.fasta"
    path.write_text(">alpha\nACDEFGHIKL-MNPQRSTVWYZ\n>beta\nACDEYGHIKL-MNPQRSTVWYZ\n"
                    ">gamma\nACDEFGHIKL-MNPQRSTVWYZ\n", encoding="utf-8")
    return path


@pytest.fixture
def window(alignment_path):
    from BS_app import MainWindow
    window = MainWindow()
    assert window.loadFile(str(alignment_path))
    yield window
    window.close()
