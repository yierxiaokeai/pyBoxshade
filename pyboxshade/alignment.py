from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from Bio import AlignIO
from Bio.Nexus.Nexus import NexusError

from pyboxshade.errors import AlignmentReadError


@dataclass(frozen=True)
class AlignmentData:
    names: tuple[str, ...]
    sequences: tuple[str, ...]
    text: str
    format: str


def read_alignment(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    text = text.lstrip()
    if not text:
        raise ValueError("The alignment file is empty.")
    first = text.splitlines()[0].upper()
    if first.startswith(">"):
        formats = ("fasta",)
    elif first.startswith(("CLUSTAL", "MUSCLE")):
        formats = ("clustal",)
    elif first.startswith("#NEXUS"):
        formats = ("nexus",)
    elif "STOCKHOLM" in first:
        formats = ("stockholm",)
    elif "PILEUP" in first or "MULTIPLE_ALIGNMENT" in first or "MSF:" in text.upper():
        formats = ("msf",)
    elif len(first.split()) == 2 and all(word.isdigit() for word in first.split()):
        formats = ("phylip-relaxed", "phylip", "phylip-sequential")
    else:
        raise ValueError("Unrecognised alignment format. Use FASTA, Clustal, MSF, "
                         "PHYLIP, Nexus or Stockholm.")
    errors = []
    for fmt in formats:
        try:
            alignment = AlignIO.read(StringIO(text), fmt)
        except (ValueError, NexusError, AssertionError) as error:
            errors.append((fmt, error))
            continue
        sequences = tuple(str(record.seq).upper() for record in alignment)
        if len(sequences) < 2:
            raise ValueError("An alignment must contain at least two sequences.")
        if not sequences[0] or not any(c.isalpha() for seq in sequences for c in seq):
            raise ValueError("The alignment contains no residues.")
        invalid = set("".join(sequences)) - set("ABCDEFGHIJKLMNOPQRSTUVWXYZ-.~")
        if invalid:
            raise ValueError(f"Unsupported residue symbols: {', '.join(sorted(invalid))}")
        return AlignmentData(tuple(record.id for record in alignment), sequences, text, fmt)
    raise AlignmentReadError(errors)
