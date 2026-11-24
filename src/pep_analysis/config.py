"""Fixed settings for the analysis: paths and the pinned snapshot of python/peps."""

from pathlib import Path

# src/pep_analysis/config.py -> parents[2] is the repository root. uv installs the
# project in editable mode, so __file__ always points into the repository.
REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = REPO_ROOT / "data"
PEPS_REPO_DIR = DATA_DIR / "peps"
RESULTS_DIR = REPO_ROOT / "results"

PEPS_URL = "https://github.com/python/peps.git"

# Every result is computed from this commit and nothing newer.
PINNED_COMMIT = "af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58"

# Governance periods used to compare the process before and after it changed. Each period
# starts on the given date (inclusive). Sources are listed in docs/links.md.
# - 2018-07-13: on 2018-07-12 the BDFL announces on python-committers ("Transfer of
#   power") that he removes himself from the decision process. His last decision, PEP 572,
#   was committed a few hours earlier on the same UTC day (commit 8846efd6), so the
#   transition starts the next day to keep it in the BDFL period.
# - 2019-02-20: PEP 1 names the elected Steering Council (PEP 13) as the final authority
#   on PEPs (python/peps commit 83687f6e), after the first election (PEP 8100).
PERIODS = [
    ("1 BDFL", "2000-01-01"),
    ("2 Transition", "2018-07-13"),
    ("3 Steering Council", "2019-02-20"),
]
