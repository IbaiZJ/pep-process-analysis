"""Obtain the studied repository and make sure the pinned commit is available."""

import subprocess

from pep_analysis.config import DATA_DIR, PEPS_REPO_DIR, PEPS_URL, PINNED_COMMIT
from pep_analysis.git import git, has_commit


def ensure_peps_repo() -> None:
    """Clone python/peps into data/peps if needed and check that the pinned commit exists.

    The clone is full (not shallow) because the analysis needs the whole history.
    --no-checkout is used because files are always read with `git show <commit>:<path>`,
    never from the working tree, so no working tree is needed.
    """
    if not (PEPS_REPO_DIR / ".git").exists():
        DATA_DIR.mkdir(exist_ok=True)
        print(f"Cloning {PEPS_URL} into {PEPS_REPO_DIR} ...")
        subprocess.run(
            ["git", "clone", "--no-checkout", PEPS_URL, str(PEPS_REPO_DIR)],
            check=True,
        )

    if not has_commit(PINNED_COMMIT):
        # An older clone may not contain the pinned commit yet.
        git("fetch", "origin")

    if not has_commit(PINNED_COMMIT):
        msg = f"Pinned commit {PINNED_COMMIT} not found in {PEPS_URL}"
        raise SystemExit(msg)
