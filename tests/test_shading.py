import numpy as np

from BS_app import grp, readsims, sim
from OutDevs import Paintdev


def test_similarity_covers_alphabet(preferences):
    readsims()
    assert sim("A", "A")
    assert sim("Z", "Z")
    assert grp("Z", "Z")
    assert sim("A", "G")
    assert not sim("-", "A")


def test_consensus_and_gap_column(window, preferences):
    preferences.setValue("consflag", True)
    preferences.setValue("countGaps", False)
    preferences.setValue("symbcons", " .*")
    window.process_seqs()
    assert window.cons[4] == "F"
    assert list(window.cols[:, 4]) == [1, 2, 1]
    assert np.all(window.cols[:, 0] == 3)
    assert np.all(window.cols[:, 10] == 0)
    assert window.conschar[10] == " "
    assert np.all(window.cols[:, -1] == 3)


def test_dna_similarity(preferences):
    preferences.setValue("pepseqsflag", False)
    readsims()
    assert sim("A", "G")
    assert grp("C", "T")
    assert not grp("A", "T")


def test_exact_block_numbering(window, preferences, tmp_path):
    path = tmp_path / "exact.fasta"
    path.write_text(">a\n" + "A"*20 + "\n>b\n" + "A"*20 + "\n", encoding="utf-8")
    window.loadFile(str(path))
    preferences.setValue("outlen", 10)
    preferences.setValue("LHsnumsflag", True)
    preferences.setValue("RHsnumsflag", True)
    window.startnums[:] = -3
    device = Paintdev(window)
    try:
        assert window.prep_out(device)
        assert device.paint.font().pixelSize() == device.FSize
        assert [s.strip() for s in device.LHprenums[0]] == ["-3", "8"]
        assert [s.strip() for s in device.RHprenums[0]] == ["7", "17"]
        assert device.canvas.height() < 160
    finally:
        device.exit()


def test_reference_reset_when_loading_smaller_alignment(window, preferences, tmp_path):
    window.consensnum = 3
    preferences.setValue("scflag", True)
    path = tmp_path / "small.fa"
    path.write_text(">a\nAC\n>b\nAT\n", encoding="utf-8")
    assert window.loadFile(str(path))
    assert window.consensnum == 1
