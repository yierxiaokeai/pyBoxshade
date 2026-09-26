import errno
import os
import subprocess
import sys

import pytest
from Bio.Nexus.Nexus import NexusError
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from pyboxshade.alignment import read_alignment
from pyboxshade.errors import AlignmentReadError, describe_error
from pyboxshade.window import ModernWindow


@pytest.mark.parametrize("text, fragment", [
    (">alpha\nACGT\n>beta\nACG\n", "比对长度不一致"),
    ("CLUSTAL W\n\nalpha ACGT 4\nbeta  ACGT nope\n", "位置编号"),
    ("# STOCKHOLM 1.0\nalpha ACGT\nbeta ACG\n//\n", "比对长度不一致"),
    ("2 5\nalpha ACGTAC\nbeta ACGTA\n", "无法读取比对"),
    ("PileUp\n\n MSF: 4 Type: N Check: 0 ..\n\n Name: alpha Len: 4 Check: 0 Weight: 1.00\n", "结束标记"),
    ("#NEXUS\n[unclosed comment\n", "方括号"),
])
def test_real_parser_failures_are_readable(tmp_path, text, fragment):
    path = tmp_path / "损坏比对.txt"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(AlignmentReadError) as result:
        read_alignment(path)
    report = describe_error(result.value)
    assert fragment in report.message
    assert report.details == str(result.value)
    assert result.value.attempts
    assert "Unable to read" not in report.message


@pytest.mark.parametrize("exception", [NexusError("Invalid matrix"), AssertionError("Bad consensus")])
def test_third_party_parser_exceptions_keep_diagnostics(tmp_path, monkeypatch, exception):
    path = tmp_path / "input.nex"
    path.write_text("#NEXUS\n", encoding="utf-8")
    def fail(*args):
        raise exception
    monkeypatch.setattr("pyboxshade.alignment.AlignIO.read", fail)
    with pytest.raises(AlignmentReadError) as result:
        read_alignment(path)
    assert result.value.attempts[0][1] is exception
    report = describe_error(result.value)
    assert "详细信息" in report.message
    assert str(exception) in report.details


@pytest.mark.parametrize("number, fragment", [
    (errno.ENOENT, "不存在"), (errno.EACCES, "权限"), (errno.ENOSPC, "空间不足"),
    (errno.EISDIR, "文件夹"), (errno.EROFS, "只读"), (errno.EBUSY, "占用"),
])
def test_os_failures_keep_paths_and_original_diagnostics(number, fragment):
    error = OSError(number, "system-specific error", "D:/中文/{literal}<input>.fasta")
    report = describe_error(error)
    assert fragment in report.message
    assert error.filename in report.message
    assert report.details == str(error)
    assert describe_error(error, "en").message == str(error)


def test_bad_encoding_is_localized(tmp_path):
    path = tmp_path / "非UTF8.fasta"
    path.write_bytes(b">alpha\nACG\xff\n>beta\nACGT\n")
    with pytest.raises(UnicodeDecodeError) as result:
        read_alignment(path)
    report = describe_error(result.value)
    assert "UTF-8" in report.message
    assert "字节位置" in report.message
    assert "can't decode" in report.details


def test_gui_read_failure_preserves_loaded_data_and_details(alignment_path, tmp_path, monkeypatch):
    window = ModernWindow()
    dialogs = []
    monkeypatch.setattr(QMessageBox, "exec", lambda dialog: dialogs.append(dialog) or QMessageBox.Ok)
    try:
        assert window.loadFile(str(alignment_path))
        original = window.seqs.copy()
        missing = tmp_path / "不存在.fasta"
        assert window.loadFile(str(missing)) is False
        assert (window.seqs == original).all()
        dialog = dialogs[-1]
        assert dialog.windowTitle() == "无法打开比对文件"
        assert "不存在" in dialog.text()
        assert str(missing) in dialog.text()
        assert dialog.textFormat() == Qt.PlainText
        assert "[Errno" in dialog.detailedText()
    finally:
        window.close()


def test_gui_export_failure_preserves_existing_file(alignment_path, tmp_path, monkeypatch):
    window = ModernWindow()
    dialogs = []
    output = tmp_path / "已有输出.svg"
    output.write_text("preserve existing content", encoding="utf-8")
    monkeypatch.setattr(QMessageBox, "exec", lambda dialog: dialogs.append(dialog) or QMessageBox.Ok)
    monkeypatch.setattr("pyboxshade.window.QFileDialog.getSaveFileName", lambda *args: (str(output), ""))
    try:
        assert window.loadFile(str(alignment_path))
        window.seqnames[0] = "A" * 2000
        window.export_dialog("svg")
        assert "输出过宽" in dialogs[-1].text()
        assert "Output is too wide" in dialogs[-1].detailedText()
        assert output.read_text(encoding="utf-8") == "preserve existing content"
    finally:
        window.close()


@pytest.mark.parametrize("failure", ["unequal", "missing", "destination", "encoding"])
def test_chinese_cli_errors(tmp_path, failure, alignment_path):
    path = alignment_path
    output = tmp_path / "output.svg"
    if failure == "unequal":
        path = tmp_path / "unequal.fa"
        path.write_text(">a\nACGT\n>b\nACG\n", encoding="utf-8")
        fragment = "长度不一致"
    elif failure == "missing":
        path = tmp_path / "不存在.fa"
        fragment = "不存在"
    elif failure == "destination":
        output = tmp_path / "不存在目录" / "output.svg"
        fragment = "打开输出文件"
    else:
        path = tmp_path / "encoding.fa"
        path.write_bytes(b">a\nAC\xff\n>b\nACG\n")
        fragment = "UTF-8"
    if output.parent.exists():
        output.write_text("original", encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "pyboxshade", str(path), "--export", str(output),
                             "--language", "zh_CN"], capture_output=True, text=True, encoding="utf-8",
                            env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=30)
    assert result.returncode == 2
    assert fragment in result.stderr
    assert "技术详情" in result.stderr
    if output.exists():
        assert output.read_text(encoding="utf-8") == "original"


def test_unknown_error_has_chinese_summary_and_full_details():
    error = RuntimeError("New vendor failure: <node>{literal} Ω")
    report = describe_error(error)
    assert "详细信息" in report.message
    assert report.details == str(error)
