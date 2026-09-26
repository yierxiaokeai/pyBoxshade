import argparse
import os
import sys
from pathlib import Path

from pyboxshade import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(description="Shade a multiple sequence alignment")
    parser.add_argument("alignment", nargs="?", type=Path)
    parser.add_argument("--version", action="version", version=f"pyBoxshade {__version__}")
    parser.add_argument("--export", type=Path, help="Export to PNG, SVG, PDF, RTF, PS or TXT without opening a window")
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--line-width", type=int, default=None)
    parser.add_argument("--dna", action="store_true")
    parser.add_argument("--reference", type=int, help="Reference sequence, numbered from 1 (required for TXT)")
    parser.add_argument("--language", choices=("zh_CN", "en"), help="Interface language (saved for subsequent launches)")
    args = parser.parse_args(argv)
    if args.export and not args.alignment:
        parser.error("--export requires an alignment")
    if args.threshold is not None and not 0 <= args.threshold <= 1:
        parser.error("--threshold must be between 0 and 1")
    if args.line_width is not None and not 10 <= args.line_width <= 250:
        parser.error("--line-width must be between 10 and 250")
    if args.export:
        os.environ.setdefault("QT_QPA_PLATFORM", "windows" if sys.platform == "win32" else "offscreen")
    from PyQt5.QtCore import QSettings, Qt
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from BS_app import MainWindow, set_defaults
    from pyboxshade.qt_runtime import configure_qt
    from pyboxshade.settings import new_settings

    configure_qt()
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication([sys.argv[0]])
    app.setApplicationName("pyBoxshade")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Boxshade")
    if args.export:
        # Each unattended export uses in-memory settings with a private INI file.
        from tempfile import TemporaryDirectory
        with TemporaryDirectory(prefix="pyboxshade-") as settings_dir:
            QSettings.setDefaultFormat(QSettings.IniFormat)
            QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, settings_dir)
            QSettings.setPath(QSettings.IniFormat, QSettings.SystemScope, settings_dir)
            return run_export(args, MainWindow, set_defaults)
    set_defaults()
    from pyboxshade.window import ModernWindow
    window = ModernWindow()
    if args.language:
        window.set_language(args.language)
    settings = new_settings()
    apply_options(args, settings)
    window.refresh_controls()
    if args.alignment:
        window.loadFile(str(args.alignment))
        if args.reference is not None:
            if not 1 <= args.reference <= window.no_seqs:
                QMessageBox.warning(window, window.interface.text("Invalid reference"),
                                    window.interface.text("Reference sequence is outside the alignment."))
                settings.setValue("scflag", False)
            else:
                window.consensnum = args.reference
            window.process_seqs()
            window.render_preview(fit=True)
    window.show()
    return app.exec()


def apply_options(args, settings):
    if args.threshold is not None:
        settings.setValue("thrfrac", args.threshold)
    if args.line_width is not None:
        settings.setValue("outlen", args.line_width)
    if args.dna:
        settings.setValue("pepseqsflag", False)
    if args.reference is not None:
        settings.setValue("scflag", True)


def run_export(args, window_class, defaults):
    from pyboxshade.settings import new_settings
    from pyboxshade.alignment import read_alignment
    from pyboxshade.export import export_alignment
    try:
        data = read_alignment(args.alignment)
        if args.reference is not None and not 1 <= args.reference <= len(data.sequences):
            raise ValueError("Reference sequence is outside the alignment.")
        defaults()
        settings = new_settings()
        apply_options(args, settings)
        window = window_class()
        window.loadFile(str(args.alignment))
        if args.reference is not None:
            window.consensnum = args.reference
            window.process_seqs()
        export_alignment(window, args.export)
        print(f"Saved {args.export}")
        return 0
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        from pyboxshade.errors import describe_error
        report = describe_error(error, args.language or "en")
        print(f"pyBoxshade: {report.message}", file=sys.stderr)
        if report.details != report.message:
            print(f"技术详情：\n{report.details}", file=sys.stderr)
        return 2
