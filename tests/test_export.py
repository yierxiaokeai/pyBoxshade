import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
from pypdf import PdfReader
from PyQt5.QtGui import QImage

from OutDevs import RTFdev
from pyboxshade.export import export_alignment


@pytest.mark.parametrize("fmt", ["png", "svg", "pdf", "rtf", "ps", "txt"])
def test_exports(window, preferences, tmp_path, fmt):
    preferences.setValue("consflag", True)
    preferences.setValue("rulerflag", True)
    preferences.setValue("LHsnumsflag", True)
    preferences.setValue("RHsnumsflag", True)
    preferences.setValue("scflag", True)
    window.process_seqs()
    path = tmp_path / f"输出.{fmt}"
    export_alignment(window, path)
    assert path.stat().st_size > 100
    if fmt == "svg":
        root = ET.parse(path).getroot()
        assert root.tag.endswith("svg")
        texts = [node.text or "" for node in root.iter() if node.tag.endswith("text")]
        assert "alpha" in "".join(texts)
    elif fmt == "pdf":
        reader = PdfReader(path)
        assert len(reader.pages) == 1
        assert "alpha" in "".join(reader.pages[0].extract_text().split())
    elif fmt == "png":
        image = QImage(str(path))
        assert not image.isNull()
        assert image.width() > 100
    elif fmt == "rtf":
        assert path.read_text(encoding="utf-8").startswith("{\\rtf1")
    elif fmt == "ps":
        assert path.read_text(encoding="utf-8").endswith("%%EOF\n")
    else:
        assert "alpha" in path.read_text(encoding="utf-8")


def test_pdf_pagination(window, preferences, tmp_path):
    path = tmp_path / "long.fa"
    path.write_text(">alpha\n" + "ACGT"*300 + "\n>beta\n" + "ACGT"*300 + "\n", encoding="utf-8")
    window.loadFile(str(path))
    preferences.setValue("outlen", 20)
    output = tmp_path / "long.pdf"
    export_alignment(window, output)
    pages = PdfReader(output).pages
    assert len(pages) >= 3
    assert all("alpha" in "".join(page.extract_text().split()) for page in pages)


def test_rtf_escaping():
    assert RTFdev.escape("a{b}\\c") == "a\\{b\\}\\\\c"
    assert RTFdev.escape("中") == "\\u20013?"


def test_failed_export_preserves_existing_file(window, tmp_path):
    output = tmp_path / "image.svg"
    output.write_text("existing file", encoding="utf-8")
    window.seqnames[0] = "A"*2000
    with pytest.raises(ValueError, match="wide"):
        export_alignment(window, output)
    assert output.read_text(encoding="utf-8") == "existing file"


def test_cli(alignment_path, tmp_path):
    output = tmp_path / "cli.svg"
    result = subprocess.run([sys.executable, "-m", "pyboxshade", str(alignment_path),
                             "--export", str(output)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    ET.parse(output)
    result = subprocess.run([sys.executable, "-m", "pyboxshade", str(alignment_path),
                             "--export", str(output), "--reference", "99"],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 2
    assert "outside" in result.stderr


def test_cli_failed_destination(alignment_path, tmp_path):
    result = subprocess.run([sys.executable, "-m", "pyboxshade", str(alignment_path),
                             "--export", str(tmp_path / "missing" / "output.rtf")],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 2
