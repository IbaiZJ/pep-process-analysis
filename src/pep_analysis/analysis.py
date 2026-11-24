"""Measure how the PEP process behaves: outcomes, time to decision and participation,
overall and by governance period. Every number in the report comes from the tables
written here.

Outputs (in results/): one CSV per table, the charts (*.png) and summary.md with all
tables in Markdown, ready to be cited in docs/report.md.
"""

import csv
import statistics
from collections import Counter
from pathlib import Path

from pep_analysis import charts, participation
from pep_analysis.analysis_common import (
    CLOSED,
    OUTCOME_ORDER,
    Row,
    Table,
    measurable,
    pct,
    period_of,
)
from pep_analysis.config import PERIODS, PINNED_COMMIT, RESULTS_DIR


def outcome_table(
    peps: list[Row], group_name: str, group_of, keys: list[str] | None = None
) -> Table:
    """Count outcomes per group and the share of "no" among closed PEPs.

    keys lists groups that must appear even when empty (a period with no decisions is a
    result, not a missing row).

    rejection_rate and withdrawal_rate use only closed PEPs (accepted, rejected,
    withdrawn) as denominator; including open PEPs would make them look lower.
    """
    groups: dict[str, Counter] = {key: Counter() for key in keys or []}
    for row in peps:
        groups.setdefault(group_of(row), Counter())[row["outcome"]] += 1
    table = []
    for key in sorted(groups):
        counts = groups[key]
        closed = sum(counts[o] for o in CLOSED)
        table.append(
            {
                group_name: key,
                "total": sum(counts.values()),
                **{o: counts[o] for o in OUTCOME_ORDER},
                "closed": closed,
                "acceptance_rate_%": pct(counts["accepted"], closed),
                "rejection_rate_%": pct(counts["rejected"], closed),
                "withdrawal_rate_%": pct(counts["withdrawn"], closed),
            }
        )
    return table


def time_table(peps: list[Row], group_name: str, group_of) -> Table:
    """Median and quartiles of days from Created to decision, per group and outcome."""
    values: dict[tuple[str, str], list[int]] = {}
    for row in peps:
        if not measurable(row):
            continue
        key = group_of(row)
        values.setdefault((key, row["outcome"]), []).append(int(row["days_to_decision"]))
    table = []
    for (key, outcome), days in sorted(values.items()):
        quartiles = (
            statistics.quantiles(days, n=4, method="inclusive") if len(days) > 1 else days * 3
        )
        table.append(
            {
                group_name: key,
                "outcome": outcome,
                "n": len(days),
                "median_days": statistics.median(days),
                "p25_days": round(quartiles[0]),
                "p75_days": round(quartiles[2]),
            }
        )
    return table


def open_table(peps: list[Row]) -> Table:
    """Share of PEPs still open, by the period in which they were created.

    Recent PEPs have had less time to be decided (right-censoring): this table shows how
    much that affects the comparison between periods.
    """
    groups: dict[str, Counter] = {}
    for row in peps:
        groups.setdefault(period_of(str(row["created"])), Counter())[row["outcome"]] += 1
    return [
        {
            "created_period": key,
            "total": sum(c.values()),
            "open": c["open"],
            "open_%": pct(c["open"], sum(c.values())),
        }
        for key, c in sorted(groups.items())
    ]


def write_csv(table: Table, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)


def markdown(table: Table) -> str:
    """Render a table as GitHub Markdown; numeric-looking columns are right-aligned."""
    columns = list(table[0])
    numeric = [
        all(str(row[c]).replace(".", "", 1).isdigit() or row[c] == "" for row in table)
        for c in columns
    ]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---:" if n else "---" for n in numeric) + " |",
    ]
    lines += ["| " + " | ".join(str(row[c]) for c in columns) + " |" for row in table]
    return "\n".join(lines)


def run(peps: list[Row], authors: list[Row], log_entries: list[tuple[str, int, str]]) -> None:
    """Compute every table, write the CSV files and results/summary.md."""
    standards = [row for row in peps if row["type"] == "Standards Track"]
    decided_dated = [row for row in peps if row["decision_date"] != ""]
    period_names = [name for name, _ in PERIODS]

    tables: dict[str, tuple[str, Table]] = {
        "outcomes": (
            "Outcomes by PEP type (all 747 PEPs)",
            outcome_table(peps, "type", lambda row: row["type"]),
        ),
        "outcomes_by_period": (
            "Outcomes of Standards Track PEPs by period of decision "
            "(PEPs with a decision date not from a bulk commit)",
            outcome_table(
                [r for r in standards if r["decision_date"] and not r["decision_in_bulk_commit"]],
                "decision_period",
                lambda row: period_of(str(row["decision_date"])),
                keys=period_names,
            ),
        ),
        "decisions_by_period": (
            "Decisions of all types by period of decision (not from a bulk commit)",
            outcome_table(
                [r for r in peps if r["decision_date"] and not r["decision_in_bulk_commit"]],
                "decision_period",
                lambda row: period_of(str(row["decision_date"])),
                keys=period_names,
            ),
        ),
        "time_to_decision": (
            "Days from Created to decision, by outcome (all types)",
            time_table(peps, "scope", lambda row: "all periods"),
        ),
        "time_to_decision_by_period": (
            "Days from Created to decision, Standards Track, by period of decision",
            time_table(standards, "decision_period", lambda r: period_of(str(r["decision_date"]))),
        ),
        "open_by_created_period": (
            "PEPs still open, by period of creation (right-censoring check)",
            open_table(peps),
        ),
    }

    # Authors inherit the creation year of their PEP, used for "new authors".
    year_of = {row["pep"]: row["created_year"] for row in peps}
    authors = [{**row, "created_year": year_of[row["pep"]]} for row in authors]
    peps_per_author, _ = participation.author_stats(authors)
    years = sorted({str(row["created_year"]) for row in peps})
    tables["authors_by_pep_count"] = (
        "Authors by number of PEPs written",
        participation.bucket_table(peps_per_author),
    )
    tables["participation_by_period"] = (
        "Participation by period of creation",
        participation.by_group(
            peps, authors, "created_period", lambda r: period_of(str(r["created"])), period_names
        ),
    )
    tables["participation_by_year"] = (
        "Participation by year of creation",
        participation.by_group(
            peps, authors, "created_year", lambda r: str(r["created_year"]), years
        ),
    )
    tables["delegation_by_period"] = (
        "Standards Track decisions naming a delegate, by period of decision",
        participation.delegation_table(peps),
    )

    totals = Counter(row["outcome"] for row in peps)
    excluded_bulk = sum(bool(row["decision_in_bulk_commit"]) for row in peps)
    no_date = sum(row["outcome"] in CLOSED and row["decision_date"] == "" for row in peps)

    lines = [
        "# Results summary",
        "",
        f"Generated from python/peps at commit `{PINNED_COMMIT}`.",
        "Do not edit: this file is regenerated by `uv run pep-analysis`.",
        "",
        "## Totals",
        "",
        f"- PEPs analysed: {len(peps)} (Standards Track: {len(standards)})",
        "- Outcomes: " + ", ".join(f"{o} {totals[o]}" for o in OUTCOME_ORDER),
        f"- PEPs with a decision date: {len(decided_dated)}",
        f"- Decisions dated by a bulk commit (excluded from time and period tables): "
        f"{excluded_bulk}",
        f"- Closed PEPs without a measurable decision date: {no_date}",
        "",
        "## Periods",
        "",
        *[f"- {name}: from {start}" for name, start in PERIODS],
    ]
    lines += ["", "## Authorship concentration", ""]
    lines += participation.summary_lines(peps_per_author, peps, authors)
    lines += ["", "## Charts", ""]
    lines += [f"- `results/{name}`" for name in charts.draw(peps, tables)]
    for name, (title, table) in tables.items():
        write_csv(table, RESULTS_DIR / f"{name}.csv")
        lines += ["", f"## {title}", "", f"`results/{name}.csv`", "", markdown(table)]

    log_table = [{"rule": r, "records": n, "note": note} for r, n, note in log_entries]
    lines += ["", "## Cleaning log", "", markdown(log_table), ""]
    (RESULTS_DIR / "summary.md").write_text("\n".join(lines), encoding="utf-8")
