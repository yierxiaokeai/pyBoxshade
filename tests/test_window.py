from PyQt5.QtWidgets import QMessageBox

from mydialog import prefsDialog
from pyboxshade.window import ModernWindow


def test_live_preview(app, alignment_path, preferences):
    window = ModernWindow()
    try:
        assert not window.export_actions[0].isEnabled()
        assert window.loadFile(str(alignment_path))
        assert window.preview.scene().items()
        assert window.export_actions[0].isEnabled()
        window.threshold.setValue(0.5)
        assert window.timer.isActive()
        window.timer.stop()
        window.apply_quick_settings()
        assert preferences.value("thrfrac", type=float) == 0.5
        window.preview.zoom(1.25)
        window.preview.fit()
        assert window.recent_menu.actions()
    finally:
        window.close()


def test_invalid_file_keeps_loaded_alignment(window, tmp_path, monkeypatch):
    path = tmp_path / "bad.fa"
    path.write_text("invalid", encoding="utf-8")
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: None)
    assert window.loadFile(str(path)) is False
    assert window.no_seqs == 3


def test_preferences_without_alignment():
    dialog = prefsDialog(0)
    dialog.GenTab.filltable()
    dialog.reject()


def test_preferences_validate_symbols(monkeypatch):
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: None)
    dialog = prefsDialog(0)
    dialog.GenTab.consbox.setText("*")
    assert dialog.GenTab.exit() is False
    dialog.reject()
