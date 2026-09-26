from pathlib import Path
from importlib.util import find_spec

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks.qt import pyqt5_library_info

project = Path(SPECPATH)
qt_root = Path(find_spec('PyQt5').origin).parent / 'Qt5'
reported_prefix = Path(pyqt5_library_info.location['PrefixPath'])
for key, value in tuple(pyqt5_library_info.location.items()):
    path = Path(value)
    if path == reported_prefix or reported_prefix in path.parents:
        pyqt5_library_info.location[key] = str(qt_root / path.relative_to(reported_prefix))
pyqt5_library_info.qt_inside_package = True
pyqt5_library_info.qt_lib_dir = qt_root / 'bin'

a = Analysis(
    [str(project / 'BS_app.py')],
    pathex=[str(project)],
    datas=collect_data_files('pyboxshade'),
    hiddenimports=['Bio.Nexus', 'PyQt5.QtSvg', 'pyboxshade.window'],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='pyBoxshade', console=False)
coll = COLLECT(exe, a.binaries, a.datas, name='pyBoxshade')
