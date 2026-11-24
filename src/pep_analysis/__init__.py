"""Analysis of the Python PEP process from a pinned snapshot of python/peps."""

from collections import Counter

from pep_analysis import analysis, clean, headers, history
from pep_analysis.config import PINNED_COMMIT
from pep_analysis.fetch import ensure_peps_repo


def main() -> None:
    """Run the whole analysis pipeline."""
    ensure_peps_repo()
    print(f"Pinned commit: {PINNED_COMMIT}")

    raw_rows = headers.run()
    peps, authors, log = clean.clean(raw_rows)
    history.run(peps, log)
    clean.write_outputs(peps, authors, log)
    analysis.run(peps, authors, log.entries)

    print("\nCleaning log:")
    for rule, records, note in log.entries:
        print(f"  {records:>5}  {rule}" + (f"  [{note}]" if note else ""))

    print("\nOutcomes:")
    for outcome, count in Counter(row["outcome"] for row in peps).most_common():
        print(f"  {count:>5}  {outcome}")
    print("\nAll tables: results/summary.md")
