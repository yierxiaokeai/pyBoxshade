from io import StringIO

import pytest
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from pyboxshade.alignment import read_alignment


@pytest.mark.parametrize("fmt", ["fasta", "clustal", "phylip", "phylip-relaxed",
                                 "phylip-sequential", "stockholm", "nexus"])
def test_supported_formats(tmp_path, fmt):
    alignment = MultipleSeqAlignment([
        SeqRecord(Seq("AC-GTA"), id="alpha", annotations={"molecule_type": "DNA"}),
        SeqRecord(Seq("ACCGTA"), id="beta", annotations={"molecule_type": "DNA"}),
    ])
    handle = StringIO()
    AlignIO.write(alignment, handle, fmt)
    path = tmp_path / "input.txt"
    path.write_text("\ufeff\n" + handle.getvalue(), encoding="utf-8")
    data = read_alignment(path)
    assert data.names == ("alpha", "beta")
    assert data.sequences == ("AC-GTA", "ACCGTA")


def test_msf(tmp_path):
    path = tmp_path / "input.msf"
    path.write_text("PileUp\n\n   MSF: 6  Type: N  Check: 0 ..\n\n"
                    " Name: alpha Len: 6 Check: 0 Weight: 1.00\n"
                    " Name: beta Len: 6 Check: 0 Weight: 1.00\n\n//\n\n"
                    "alpha AC.GTA\nbeta  ACCGTA\n", encoding="utf-8")
    assert read_alignment(path).sequences == ("AC-GTA", "ACCGTA")


@pytest.mark.parametrize("text", ["", ">a\nAC\n", ">a\nAC\n>b\nA\n",
                                  ">a\n--\n>b\n--\n", "invalid", ">a\nA*\n>b\nA*\n"])
def test_invalid_alignment(tmp_path, text):
    path = tmp_path / "bad.fasta"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        read_alignment(path)
