"""Analysis of the Python PEP process from a pinned snapshot of python/peps."""

from collections import Counter

from pep_analysis import headers
from pep_analysis.config import PINNED_COMMIT
from pep_analysis.fetch import ensure_peps_repo


def main() -> None:
    """Run the whole analysis pipeline."""
    ensure_peps_repo()
    print(f"Pinned commit: {PINNED_COMMIT}")

    rows = headers.run()
    print(f"PEP files read: {len(rows)}")

    # Raw status values, before any cleaning, to see how messy the data is.
    statuses = Counter(row.get("Status", "<missing>") for row in rows)
    for status, count in statuses.most_common():
        print(f"  {status}: {count}")
