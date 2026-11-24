"""Participation: who writes PEPs, how concentrated authorship is, how many newcomers
appear, and how often decisions are delegated. Only counts and shares are output, never
a list of names (see the assignment, section 8).
"""

from collections import Counter, defaultdict

from pep_analysis.analysis_common import CLOSED, Row, Table, pct, period_of
from pep_analysis.config import PERIODS

# Authors with at least this many PEPs are called "frequent authors".
FREQUENT = 10
BUCKETS = [(1, 1), (2, 4), (5, 9), (FREQUENT, 10**6)]


def author_stats(authors: list[Row]) -> tuple[dict[str, int], dict[str, int]]:
    """Return (number of PEPs per author, year of each author's first PEP)."""
    peps_per_author: Counter = Counter()
    first_year: dict[str, int] = {}
    for row in authors:
        key = str(row["author_key"])
        peps_per_author[key] += 1
        year = int(row["created_year"])
        first_year[key] = min(year, first_year.get(key, year))
    return dict(peps_per_author), first_year


def bucket_table(peps_per_author: dict[str, int]) -> Table:
    """How many authors wrote 1, 2-4, 5-9 or 10+ PEPs, and their share of authorships."""
    total_authors = len(peps_per_author)
    total_authorships = sum(peps_per_author.values())
    table = []
    for low, high in BUCKETS:
        counts = [n for n in peps_per_author.values() if low <= n <= high]
        label = f"{low}" if low == high else (f"{low}+" if high >= 10**6 else f"{low}-{high}")
        table.append(
            {
                "peps_per_author": label,
                "authors": len(counts),
                "authors_%": pct(len(counts), total_authors),
                "authorships": sum(counts),
                "authorships_%": pct(sum(counts), total_authorships),
            }
        )
    return table


def by_group(
    peps: list[Row], authors: list[Row], group_name: str, group_of, keys: list[str]
) -> Table:
    """Participation per group of PEPs (a period or a year of creation)."""
    peps_per_author, first_year = author_stats(authors)
    frequent = {a for a, n in peps_per_author.items() if n >= FREQUENT}
    authors_of: dict[int, set[str]] = defaultdict(set)
    for row in authors:
        authors_of[int(row["pep"])].add(str(row["author_key"]))

    groups: dict[str, list[Row]] = {key: [] for key in keys}
    for row in peps:
        groups.setdefault(group_of(row), []).append(row)

    table = []
    for key, rows in groups.items():
        people: set[str] = set()
        newcomers: set[str] = set()
        with_newcomer = 0
        with_frequent = 0
        for row in rows:
            names = authors_of[int(row["pep"])]
            people |= names
            new = {a for a in names if first_year[a] == int(row["created_year"])}
            newcomers |= new
            with_newcomer += bool(new)
            with_frequent += bool(names & frequent)
        table.append(
            {
                group_name: key,
                "peps": len(rows),
                "distinct_authors": len(people),
                "new_authors": len(newcomers),
                "peps_with_new_author_%": pct(with_newcomer, len(rows)),
                "peps_with_frequent_author_%": pct(with_frequent, len(rows)),
                "mean_authors_per_pep": (
                    f"{sum(int(r['n_authors']) for r in rows) / len(rows):.2f}" if rows else ""
                ),
            }
        )
    return table


def delegation_table(peps: list[Row]) -> Table:
    """Standards Track decisions per period: how many name a delegate, how many people."""
    keys = [name for name, _ in PERIODS]
    groups: dict[str, list[Row]] = {key: [] for key in keys}
    for row in peps:
        if (
            row["type"] == "Standards Track"
            and row["outcome"] in CLOSED
            and row["decision_date"]
            and not row["decision_in_bulk_commit"]
        ):
            groups[period_of(str(row["decision_date"]))].append(row)
    table = []
    for key, rows in groups.items():
        delegated = [r for r in rows if r["delegate"]]
        table.append(
            {
                "decision_period": key,
                "decisions": len(rows),
                "with_delegate": len(delegated),
                "with_delegate_%": pct(len(delegated), len(rows)),
                "distinct_delegates": len({r["delegate"] for r in delegated}),
            }
        )
    return table


def summary_lines(
    peps_per_author: dict[str, int], peps: list[Row], authors: list[Row]
) -> list[str]:
    """Headline numbers for authorship concentration."""
    frequent = {a for a, n in peps_per_author.items() if n >= FREQUENT}
    peps_with_people = {int(r["pep"]) for r in authors}
    peps_with_frequent = {int(r["pep"]) for r in authors if r["author_key"] in frequent}
    ranked = sorted(peps_per_author.values(), reverse=True)
    top_n = max(1, round(len(ranked) / 10))
    return [
        f"- Distinct authors: {len(peps_per_author)}",
        f"- PEPs with at least one person as author: {len(peps_with_people)} of {len(peps)}",
        f"- Frequent authors (>= {FREQUENT} PEPs): {len(frequent)} "
        f"({pct(len(frequent), len(peps_per_author))} % of authors), co-authors of "
        f"{len(peps_with_frequent)} PEPs ({pct(len(peps_with_frequent), len(peps_with_people))} %)",
        f"- The top 10 % of authors ({top_n} people) hold {sum(ranked[:top_n])} of "
        f"{sum(ranked)} authorships ({pct(sum(ranked[:top_n]), sum(ranked))} %)",
    ]
