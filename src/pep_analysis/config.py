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
