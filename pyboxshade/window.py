from pathlib import Path

from PyQt5.QtCore import QSize, Qt, QTimer
from pyboxshade.settings import new_settings as QSettings
from PyQt5.QtGui import QIcon, QPainter, QFont
from PyQt5.QtWidgets import (
    QAction, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
    QGraphicsScene, QGraphicsView, QGroupBox, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget, QMenu, QActionGroup,
)

from BS_app import MainWindow
import BS_config as BS
from OutDevs import Paintdev
from pyboxshade import __version__
from pyboxshade.export import export_alignment
from pyboxshade.resources import resource_path
from pyboxshade.i18n import InterfaceLanguage


class AlignmentView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(self.ScrollHandDrag)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setBackgroundBrush(Qt.lightGray)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            self.zoom(1.15 if event.angleDelta().y() > 0 else 1/1.15)
            event.accept()
        else:
            super().wheelEvent(event)

    def zoom(self, factor):
        if 0.05 <= self.transform().m11()*factor <= 8:
            self.scale(factor, factor)

    def fit(self):
        if not self.scene().items():
            return
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)


class ModernWindow(MainWindow):
    def __init__(self):
        super().__init__()
        interface_font = QFont("Segoe UI")
        interface_font.setPixelSize(14)
        self.setFont(interface_font)
        self.menuBar().setFont(interface_font)
        self.statusBar().setFont(interface_font)
        for menu in (self.fileMenu, self.actionsMenu, self.helpMenu):
            menu.setFont(interface_font)
        self.setMinimumSize(920, 600)
        self.resize(max(1100, self.width()), max(720, self.height()))
        self.setWindowTitle("pyBoxshade · Alignment workspace")
        self.setWindowIcon(QIcon(resource_path("image2.png")))
        self.preview = AlignmentView()
        self.takeCentralWidget()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.preview, "Shaded alignment")
        self.tabs.addTab(self.textEdit, "Source alignment")
        self.textEdit.setPlaceholderText("Open an alignment or drag a file into this window.")
        self.textEdit.setLineWrapMode(self.textEdit.NoWrap)

        self.summary = QLabel("Open an alignment to begin")
        self.summary.setObjectName("summary")
        self.hint = QLabel("FASTA · Clustal · PHYLIP · MSF · Nexus · Stockholm")
        self.hint.setProperty("i18n_skip", True)
        self.hint.setWordWrap(True)
        open_button = QPushButton("Open alignment…")
        open_button.clicked.connect(self.open)
        sidebar = QVBoxLayout()
        sidebar.addWidget(QLabel("ALIGNMENT WORKSPACE"))
        sidebar.addWidget(self.summary)
        sidebar.addWidget(self.hint)
        sidebar.addWidget(open_button)
        sidebar.addWidget(self.quick_settings())
        sidebar.addStretch()
        sidebar.addWidget(QLabel("Ctrl + wheel to zoom\nDrag the preview to pan"))
        side = QWidget()
        side.setFixedWidth(300)
        side.setLayout(sidebar)
        content = QHBoxLayout()
        content.setContentsMargins(16, 16, 16, 16)
        content.addWidget(side)
        content.addWidget(self.tabs, 1)
        central = QWidget()
        central.setLayout(content)
        self.setCentralWidget(central)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.apply_quick_settings)
        for widget in (self.threshold, self.line_width):
            widget.valueChanged.connect(lambda *_: self.timer.start())
        self.sequence_type.currentIndexChanged.connect(lambda *_: self.timer.start())
        self.consensus.toggled.connect(lambda *_: self.timer.start())
        self.ruler.toggled.connect(lambda *_: self.timer.start())
        self.create_modern_actions()
        self.refresh_controls()
        self.update_export_actions()
        self.setStyleSheet("""
            QMainWindow, QDialog { background: #f5f7fb; }
            QLabel#summary { font-size: 17px; font-weight: 600; color: #16324f; padding: 8px 0; }
            QToolBar { background: white; border: none; spacing: 8px; padding: 8px; }
            QToolButton, QPushButton { padding: 7px 10px; border-radius: 5px; }
            QPushButton { background: #2458a6; color: white; border: none; }
            QPushButton:hover { background: #1a447f; }
            QGroupBox { border: 1px solid #d4dce8; border-radius: 7px; margin-top: 18px; padding: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
            QTabWidget::pane { border: 1px solid #d4dce8; background: white; }
            QTabBar::tab { padding: 9px 18px; }
            QStatusBar { background: white; }
        """)
        self.interface = InterfaceLanguage(self)
        self.language_menu = self.menuBar().addMenu("Language")
        self.language_group = QActionGroup(self)
        self.language_group.setExclusive(True)
        self.language_actions = {}
        for language, label in (("zh_CN", "简体中文"), ("en", "English")):
            action = self.language_menu.addAction(label)
            action.setCheckable(True)
            self.language_group.addAction(action)
            action.triggered.connect(lambda checked=False, code=language: self.set_language(code))
            self.language_actions[language] = action
        self.set_language(QSettings().value("interfaceLanguage", "zh_CN", type=str))

    def set_language(self, language):
        if language not in self.language_actions:
            language = "zh_CN"
        self.interface.set_language(language)
        self.language_actions[language].setChecked(True)
        if self.no_seqs >= 2:
            self.summary.setText(self.interface.text("{count} sequences\n{length:,} positions",
                                                     count=self.no_seqs, length=self.maxseqlen))
            self.show_ready_status()
        else:
            self.statusBar().showMessage(self.interface.text("Ready"))

    def show_ready_status(self):
        self.statusBar().showMessage(self.interface.text(
            "{count} sequences · {length:,} positions · Ready to export",
            count=self.no_seqs, length=self.maxseqlen))

    def closeEvent(self, event):
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        app.removeTranslator(self.interface.translator)
        app.removeEventFilter(self.interface)
        super().closeEvent(event)

    def quick_settings(self):
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0, 1)
        self.threshold.setSingleStep(0.05)
        self.threshold.setMinimumWidth(90)
        self.line_width = QSpinBox()
        self.line_width.setRange(10, 250)
        self.line_width.setMinimumWidth(90)
        self.sequence_type = QComboBox()
        self.sequence_type.addItems(["Protein", "DNA / RNA"])
        self.sequence_type.setMinimumWidth(90)
        self.consensus = QCheckBox("Consensus line")
        self.ruler = QCheckBox("Position ruler")
        form = QFormLayout()
        form.addRow("Sequence type", self.sequence_type)
        form.addRow("Threshold", self.threshold)
        form.addRow("Residues / line", self.line_width)
        form.addRow(self.consensus)
        form.addRow(self.ruler)
        advanced = QPushButton("All settings…")
        advanced.clicked.connect(self.do_prefs)
        form.addRow(advanced)
        box = QGroupBox("Shading & layout")
        box.setLayout(form)
        return box

    def create_modern_actions(self):
        self.recent_menu = QMenu("Recent files", self)
        self.fileMenu.insertMenu(self.exitAct, self.recent_menu)
        self.update_recent_files()
        self.export_actions = []
        exports = self.menuBar().addMenu("&Export")
        for fmt, label in [("pdf", "PDF document…"), ("svg", "SVG vector image…"),
                           ("png", "PNG image…"), ("rtf", "RTF document…"),
                           ("ps", "PostScript…"), ("txt", "Text comparison…")]:
            action = QAction(label, self)
            action.triggered.connect(lambda checked=False, format=fmt: self.export_dialog(format))
            exports.addAction(action)
            self.export_actions.append(action)
        toolbar = self.addToolBar("Preview")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.addAction("Fit", self.preview.fit)
        toolbar.addAction("100%", self.preview.resetTransform)
        toolbar.addAction("Zoom +", lambda: self.preview.zoom(1.25))
        toolbar.addAction("Zoom −", lambda: self.preview.zoom(0.8))
        toolbar.addSeparator()
        toolbar.addAction(self.export_actions[0])
        toolbar.addAction(self.export_actions[1])
        self.PaintAct.setText("Refresh preview")

    def refresh_controls(self):
        settings = QSettings("Boxshade", "Boxshade")
        values = [(self.threshold, "thrfrac", float), (self.line_width, "outlen", int)]
        for widget, key, dtype in values:
            widget.blockSignals(True)
            widget.setValue(settings.value(key, type=dtype))
            widget.blockSignals(False)
        for widget, key in [(self.consensus, "consflag"), (self.ruler, "rulerflag")]:
            widget.blockSignals(True)
            widget.setChecked(settings.value(key, type=bool))
            widget.blockSignals(False)
        self.sequence_type.blockSignals(True)
        self.sequence_type.setCurrentIndex(0 if settings.value("pepseqsflag", type=bool) else 1)
        self.sequence_type.blockSignals(False)

    def apply_quick_settings(self):
        settings = QSettings("Boxshade", "Boxshade")
        for key, value in [("thrfrac", self.threshold.value()), ("outlen", self.line_width.value()),
                           ("pepseqsflag", self.sequence_type.currentIndex() == 0),
                           ("consflag", self.consensus.isChecked()), ("rulerflag", self.ruler.isChecked())]:
            settings.setValue(key, value)
        self.process_seqs()
        self.render_preview()

    def do_prefs(self):
        if hasattr(self, "timer"):
            self.timer.stop()
            self.apply_quick_settings()
        super().do_prefs()
        self.refresh_controls()
        self.render_preview()

    def loadFile(self, filename):
        if not super().loadFile(filename):
            return False
        if hasattr(self, "preview"):
            settings = QSettings("Boxshade", "Boxshade")
            recent = settings.value("recentFiles", [], type=list)
            path = str(Path(filename).resolve())
            settings.setValue("recentFiles", [path] + [item for item in recent if item != path][:9])
            BS.lastdir = str(Path(filename).resolve().parent)
            self.summary.setText(self.interface.text("{count} sequences\n{length:,} positions",
                                                     count=self.no_seqs, length=self.maxseqlen))
            self.hint.setText(Path(filename).name)
            self.setWindowTitle(f"{Path(filename).name} · pyBoxshade")
            self.update_recent_files()
            self.update_export_actions()
            self.render_preview(fit=True)
        return True

    def update_recent_files(self):
        self.recent_menu.clear()
        for path in QSettings("Boxshade", "Boxshade").value("recentFiles", [], type=list):
            action = self.recent_menu.addAction(Path(path).name)
            action.setProperty("i18n_skip", True)
            action.setToolTip(path)
            action.triggered.connect(lambda checked=False, filename=path: self.loadFile(filename))
        self.recent_menu.setEnabled(bool(self.recent_menu.actions()))

    def update_export_actions(self):
        for action in self.export_actions + [self.RTFAct, self.PSAct, self.AscAct, self.PaintAct]:
            action.setEnabled(self.no_seqs >= 2)

    def render_preview(self, fit=False):
        if self.no_seqs < 2:
            return
        device = Paintdev(self)
        try:
            if not self.prep_out(device):
                raise ValueError("Unable to allocate preview image.")
            self.do_out(device)
        except (ValueError, OSError, RuntimeError) as error:
            self.preview.scene().clear()
            self.preview.scene().addText(self.interface.text("Preview unavailable: {error}", error=self.interface.error_text(error)))
            self.preview.setToolTip(str(error))
            self.statusBar().showMessage(self.interface.error_text(error))
            return
        finally:
            from PyQt5.QtWidgets import QApplication
            if hasattr(device, "paint") and device.paint.isActive():
                device.paint.end()
            if QApplication.overrideCursor() is not None:
                QApplication.restoreOverrideCursor()
        self.preview.scene().clear()
        self.preview.setToolTip("")
        self.preview.scene().addPixmap(device.canvas)
        self.preview.setSceneRect(self.preview.scene().itemsBoundingRect())
        if fit:
            self.preview.fit()
        self.show_ready_status()

    def image_out(self):
        self.render_preview(fit=True)
        self.tabs.setCurrentIndex(0)

    def export_dialog(self, fmt):
        if self.timer.isActive():
            self.timer.stop()
            self.apply_quick_settings()
        default = str(Path(self.curFile).with_suffix(f".{fmt}"))
        path, _ = QFileDialog.getSaveFileName(self, self.interface.text("Export {format}", format=fmt.upper()),
                                             default, f"{fmt.upper()} (*.{fmt})")
        if not path:
            return
        if not Path(path).suffix:
            path += f".{fmt}"
        try:
            export_alignment(self, path, fmt)
        except (ValueError, OSError, RuntimeError) as error:
            self.interface.show_error("Export failed", error)
            return
        self.statusBar().showMessage(self.interface.text("Saved {path}", path=path), 8000)

    def RTF_out(self):
        self.export_dialog("rtf")

    def PS_out(self):
        self.export_dialog("ps")

    def ASCII_out(self):
        self.export_dialog("txt")

    def about(self):
        QMessageBox.about(self, self.interface.text("About pyBoxshade"), f"pyBoxshade {__version__}\n" +
                          self.interface.text("Sequence alignment shading, live preview and vector export.") + "\n" +
                          self.interface.text("Based on Michael Baron’s pyBoxshade. Licensed under GPL-3.0."))
