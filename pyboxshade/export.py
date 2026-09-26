from pathlib import Path

from PyQt5.QtCore import QIODevice, QSaveFile, QSize, QSizeF, QRectF, QMarginsF
from pyboxshade.settings import new_settings as QSettings
from PyQt5.QtGui import QFont, QPageLayout, QPageSize, QPainter, QPdfWriter
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtWidgets import QApplication

import BS_config as BS
from OutDevs import ASCIIdev, Paintdev, PSdev, RTFdev
from pyboxshade.errors import qt_file_error


def dimensions(device, window):
    blocks = (window.consenslen + device.outlen - 1) // device.outlen
    lines = blocks * (device.no_seqs + device.interlines) - device.interlines
    chars = min(device.outlen, window.consenslen)
    if device.snameflag:
        chars += len(device.seqnames[0]) + 1
    if device.LHsnumsflag:
        chars += len(device.LHprenums[0][0]) + 1
    if device.RHsnumsflag:
        chars += len(device.RHprenums[0][0]) + 1
    return int(2*device.left_mar + chars*device.dev_xsize + 1), int(2*device.top_mar + lines*device.dev_ysize + 1)


class VectorDevice(Paintdev):
    def __init__(self, window, path, fmt):
        super().__init__(window)
        self.path = str(path)
        self.fmt = fmt

    def graphics_init(self):
        width, height = dimensions(self, self.MW)
        if width > 14400:
            raise ValueError("Output is too wide. Reduce font size, line width or sequence name length.")
        if self.fmt == "svg" and height > 32767:
            raise ValueError("SVG is too tall. Use paginated PDF or increase residues per line.")
        self.file = QSaveFile(self.path)
        if not self.file.open(QIODevice.WriteOnly):
            raise qt_file_error(self.file, "open")
        if self.fmt == "svg":
            self.target = QSvgGenerator()
            self.target.setOutputDevice(self.file)
            self.target.setSize(QSize(width, height))
            self.target.setViewBox(QRectF(0, 0, width, height))
            self.target.setResolution(72)
            self.target.setTitle(Path(self.MW.curFile).name)
            self.target.setDescription("Sequence alignment shaded by pyBoxshade")
            self.lines_per_page = 10**12
        else:
            self.target = QPdfWriter(self.file)
            self.target.setResolution(72)
            self.target.setTitle(Path(self.MW.curFile).name)
            self.target.setCreator("pyBoxshade 2.0")
            page = QPageSize(QSizeF(max(width, 595), 842), QPageSize.Point)
            self.target.setPageSize(page)
            self.target.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Point)
            self.lines_per_page = int((self.target.height() - 2*self.top_mar) // self.dev_ysize)
        self.paint = QPainter(self.target)
        if not self.paint.isActive():
            self.file.cancelWriting()
            raise OSError("Unable to initialise vector rendering.")
        font = QFont(BS.monofont)
        font.setPointSize(self.FSize)
        font.setBold(True)
        self.paint.setFont(font)
        self.paint.setRenderHint(QPainter.TextAntialiasing)
        self.xpos, self.ypos = self.left_mar, self.top_mar
        self.act_col = 4
        return True

    def newpage(self):
        if self.fmt == "pdf":
            if not self.target.newPage():
                raise OSError("Unable to create a PDF page.")
            self.xpos, self.ypos = self.left_mar, self.top_mar

    def exit(self):
        self.paint.end()
        self.target = None
        if not self.file.commit():
            raise qt_file_error(self.file, "commit")


def export_alignment(window, path, fmt=None):
    path = Path(path)
    fmt = (fmt or path.suffix.lstrip(".")).lower()
    if window.no_seqs < 2:
        raise ValueError("Open an alignment before exporting.")
    if fmt not in {"svg", "pdf", "png", "rtf", "ps", "txt"}:
        raise ValueError("Choose a .svg, .pdf, .png, .rtf, .ps or .txt output file.")
    if fmt == "txt" and not QSettings("Boxshade", "Boxshade").value("scflag", type=bool):
        raise ValueError("Text export needs a reference sequence. Select one in Settings.")
    if fmt in {"svg", "pdf"}:
        device = VectorDevice(window, path, fmt)
    elif fmt == "png":
        device = Paintdev(window)
    else:
        device = {"rtf": RTFdev, "ps": PSdev, "txt": ASCIIdev}[fmt](Path(window.curFile).name)
        device.output_path = str(path)
    try:
        if not window.prep_out(device):
            raise OSError("Unable to prepare output.")
        window.do_out(device)
        if fmt == "png":
            output = QSaveFile(str(path))
            if not output.open(QIODevice.WriteOnly):
                raise qt_file_error(output, "open")
            if not device.canvas.save(output, "PNG"):
                output.cancelWriting()
                raise OSError("Unable to encode PNG.")
            if not output.commit():
                raise qt_file_error(output, "commit")
    except Exception:
        if hasattr(device, "paint") and device.paint.isActive():
            device.paint.end()
        if isinstance(device.file, QSaveFile) and device.file.isOpen():
            device.file.cancelWriting()
        raise
    finally:
        if QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()
    return path
