"""Extract the header block of every PEP file at the pinned commit."""

import csv
import re
from pathlib import Path

from pep_analysis.config import PINNED_COMMIT, RESULTS_DIR
from pep_analysis.git import git, read_blobs

# Proposal files live directly in peps/ and are named pep-NNNN.rst (older ones .txt).
PEP_FILE = re.compile(r"^peps/pep-(\d{4})\.(rst|txt)$")


def list_pep_files() -> list[str]:
    """Return the paths of all PEP files at the pinned commit, sorted by number."""
    names = git("ls-tree", "--name-only", PINNED_COMMIT, "peps/").splitlines()
    return sorted(name for name in names if PEP_FILE.match(name))


def parse_headers(text: str) -> dict[str, str]:
    """Parse the RFC 2822-style header block at the top of a PEP.

    The block ends at the first blank line. A line starting with whitespace continues
    the previous field (for example a long Post-History list).
    """
    headers: dict[str, str] = {}
    current: str | None = None
    for line in text.splitlines():
        if not line.strip():
            break
        if line[0] in " \t" and current is not None:
            headers[current] += " " + line.strip()
            continue
        key, sep, value = line.partition(":")
        if not sep:
            break
        current = key.strip()
        headers[current] = value.strip()
    return headers


def extract_headers() -> list[dict[str, str]]:
    """Read every PEP file at the pinned commit and return one row of headers per file.

    Files are read from git objects at the pinned commit, never from the working tree.
    """
    paths = list_pep_files()
    blobs = read_blobs([f"{PINNED_COMMIT}:{path}" for path in paths])
    return [{"file": path, **parse_headers(blobs[f"{PINNED_COMMIT}:{path}"])} for path in paths]


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    """Write rows to CSV. Columns: file and PEP first, then every other header A-Z."""
    keys = {key for row in rows for key in row} - {"file", "PEP"}
    fieldnames = ["file", "PEP", *sorted(keys)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run() -> list[dict[str, str]]:
    """Extract headers and save them to results/pep_headers_raw.csv."""
    rows = extract_headers()
    write_csv(rows, RESULTS_DIR / "pep_headers_raw.csv")
    return rows
