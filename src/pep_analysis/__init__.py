"""Analysis of the Python PEP process from a pinned snapshot of python/peps."""

from collections import Counter

from pep_analysis import clean, headers
from pep_analysis.config import PINNED_COMMIT
from pep_analysis.fetch import ensure_peps_repo


def main() -> None:
    """Run the whole analysis pipeline."""
    ensure_peps_repo()
    print(f"Pinned commit: {PINNED_COMMIT}")

    raw_rows = headers.run()
    peps, log = clean.run(raw_rows)

    print("\nCleaning log:")
    for rule, records, note in log.entries:
        print(f"  {records:>5}  {rule}" + (f"  [{note}]" if note else ""))

    print("\nOutcomes:")
    for outcome, count in Counter(row["outcome"] for row in peps).most_common():
        print(f"  {count:>5}  {outcome}")
