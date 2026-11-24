"""Thin wrapper around the git command line for the studied repository."""

import os
import subprocess

from pep_analysis.config import PEPS_REPO_DIR

# Run git without the user's or the system's configuration: settings such as
# log.showSignature or diff.renames in someone's ~/.gitconfig would change the output and
# therefore the numbers. Only the options passed explicitly in the code apply.
GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "LC_ALL": "C",
}


def git(*args: str) -> str:
    """Run a git command inside the cloned PEP repository and return its output."""
    result = subprocess.run(
        ["git", "-C", str(PEPS_REPO_DIR), *args],
        check=True,
        capture_output=True,
        env=GIT_ENV,
    )
    return decode(result.stdout)


def decode(data: bytes) -> str:
    """Decode git output as UTF-8.

    Some old PEPs in the history were saved as Latin-1, not UTF-8. Undecodable bytes are
    replaced instead of crashing; header fields are ASCII anyway.
    """
    return data.decode("utf-8", errors="replace")


def read_blobs(specs: list[str]) -> dict[str, str]:
    """Read many files at once with `git cat-file --batch`.

    Each spec is "<commit>:<path>". One git process for all files instead of one
    `git show` per file, which is much faster on slow file systems such as /mnt/c in WSL.
    """
    result = subprocess.run(
        ["git", "-C", str(PEPS_REPO_DIR), "cat-file", "--batch"],
        input="\n".join(specs).encode() + b"\n",
        check=True,
        capture_output=True,
        env=GIT_ENV,
    )
    out = result.stdout
    blobs = {}
    position = 0
    for spec in specs:
        # Each answer is "<sha> <type> <size>\n<content>\n".
        header_end = out.index(b"\n", position)
        header = out[position:header_end].split()
        if header[-1] == b"missing":
            msg = f"{spec} not found in the repository"
            raise ValueError(msg)
        size = int(header[2])
        start = header_end + 1
        blobs[spec] = decode(out[start : start + size])
        position = start + size + 1
    return blobs


def has_commit(commit: str) -> bool:
    """Return True if the commit exists in the local clone."""
    result = subprocess.run(
        ["git", "-C", str(PEPS_REPO_DIR), "cat-file", "-e", f"{commit}^{{commit}}"],
        check=False,
        capture_output=True,
        env=GIT_ENV,
    )
    return result.returncode == 0
