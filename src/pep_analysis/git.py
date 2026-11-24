"""Thin wrapper around the git command line for the studied repository."""

import subprocess

from pep_analysis.config import PEPS_REPO_DIR


def git(*args: str) -> str:
    """Run a git command inside the cloned PEP repository and return its output."""
    result = subprocess.run(
        ["git", "-C", str(PEPS_REPO_DIR), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        # Some old PEPs in the history were saved as Latin-1, not UTF-8. Undecodable
        # bytes are replaced instead of crashing; header fields are ASCII anyway.
        errors="replace",
    )
    return result.stdout


def has_commit(commit: str) -> bool:
    """Return True if the commit exists in the local clone."""
    result = subprocess.run(
        ["git", "-C", str(PEPS_REPO_DIR), "cat-file", "-e", f"{commit}^{{commit}}"],
        check=False,
        capture_output=True,
    )
    return result.returncode == 0
