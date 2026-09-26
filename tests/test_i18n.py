from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox

from mydialog import prefsDialog
from pyboxshade.export import export_alignment
from pyboxshade.window import ModernWindow


def test_language_switch_preserves_alignment_and_exports(alignment_path, tmp_path, preferences):
    window = ModernWindow()
    try:
        assert window.tabs.tabText(0) == "着色预览"
        assert window.loadFile(str(alignment_path))
        names = list(window.seqnames)
        preview = window.preview.scene().items()[0].pixmap().toImage()
        chinese = tmp_path / "chinese.rtf"
        english = tmp_path / "english.rtf"
        export_alignment(window, chinese)
        window.set_language("en")
        assert window.fileMenu.title() == "&File"
        assert window.tabs.tabText(0) == "Shaded alignment"
        assert "3 sequences" in window.summary.text()
        assert window.seqnames == names
        assert window.preview.scene().items()[0].pixmap().toImage() == preview
        export_alignment(window, english)
        assert chinese.read_bytes() == english.read_bytes()
        window.set_language("zh_CN")
        assert "3 条序列" in window.summary.text()
        assert preferences.value("interfaceLanguage") == "zh_CN"
    finally:
        window.close()


def test_language_persists(preferences):
    window = ModernWindow()
    window.set_language("en")
    window.close()
    reopened = ModernWindow()
    try:
        assert reopened.interface.language == "en"
        assert reopened.language_actions["en"].isChecked()
    finally:
        reopened.close()


def test_preferences_and_warning_localized_on_show(app):
    window = ModernWindow()
    dialog = prefsDialog(0, parent=window)
    original = dialog.SimTab.simstable.item(0, 0).text()
    try:
        dialog.show()
        app.processEvents()
        assert dialog.windowTitle() == "pyBoxshade 设置"
        assert dialog.tabWidget.tabText(0) == "常规"
        assert dialog.GenTab.scbox.text() == "以指定序列为参考"
        assert dialog.SimTab.simstable.horizontalHeaderItem(0).text() == "氨基酸"
        assert dialog.SimTab.simstable.item(0, 0).text() == original
        buttons = dialog.findChild(QDialogButtonBox)
        assert buttons.button(QDialogButtonBox.Ok).text() == "确定"
        warning = QMessageBox(dialog)
        warning.setText("Enter exactly three consensus symbols.")
        warning.show()
        app.processEvents()
        assert warning.text() == "请输入恰好三个共识符号。"
        warning.close()
        window.set_language("en")
        assert dialog.GenTab.scbox.text() == "Consensus to a single sequence"
        assert dialog.SimTab.simstable.horizontalHeaderItem(0).text() == "Amino Acid"
    finally:
        dialog.reject()
        window.close()


def test_user_filename_is_never_translated(tmp_path):
    path = tmp_path / "Protein"
    path.write_text(">Protein\nACGT\n>General\nACGT\n", encoding="utf-8")
    window = ModernWindow()
    try:
        assert window.loadFile(str(path))
        window.set_language("en")
        window.set_language("zh_CN")
        assert window.hint.text() == "Protein"
        assert window.recent_menu.actions()[0].text() == "Protein"
        assert window.seqnames == ["Protein", "General"]
    finally:
        window.close()
