"""Charts for the report, written as PNG files to results/."""

import os
from collections import Counter

from pep_analysis.analysis_common import OUTCOME_ORDER, Row, Table, measurable
from pep_analysis.config import DISCOURSE_DATE, PERIODS, RESULTS_DIR

COLOURS = {
    "accepted": "#2a9d8f",
    "rejected": "#e76f51",
    "withdrawn": "#f4a261",
    "superseded": "#8d99ae",
    "open": "#cfd8dc",
}


def year_fraction(day: str) -> float:
    """2019-02-20 -> 2019.14, to draw a date on a year axis."""
    year, month, dom = (int(part) for part in day.split("-"))
    return year + (month - 1) / 12 + (dom - 1) / 365


def mark_changes(ax) -> None:
    """Vertical lines at each period start (except the first) and the Discourse change."""
    for name, start in PERIODS[1:]:
        ax.axvline(year_fraction(start), color="black", linestyle="--", linewidth=0.8)
        ax.annotate(
            name[2:],
            (year_fraction(start), 1),
            xycoords=("data", "axes fraction"),
            rotation=90,
            va="top",
            ha="right",
            fontsize=8,
        )
    ax.axvline(year_fraction(DISCOURSE_DATE), color="grey", linestyle=":", linewidth=0.8)
    ax.annotate(
        "Discourse",
        (year_fraction(DISCOURSE_DATE), 1),
        xycoords=("data", "axes fraction"),
        rotation=90,
        va="top",
        ha="right",
        fontsize=8,
        color="grey",
    )


def draw(peps: list[Row], tables: dict[str, tuple[str, Table]]) -> list[str]:
    """Draw every chart and return the file names."""
    # Keep matplotlib's cache inside the repository instead of the home directory,
    # so running the project writes nothing outside it. Must be set before importing.
    os.environ.setdefault("MPLCONFIGDIR", str(RESULTS_DIR / ".matplotlib"))
    import matplotlib  # imported here on purpose, after MPLCONFIGDIR is set

    matplotlib.use("Agg")  # no display needed
    import matplotlib.pyplot as plt

    RESULTS_DIR.mkdir(exist_ok=True)
    files = []

    # 1. PEPs created per year, stacked by outcome.
    years = sorted({int(row["created_year"]) for row in peps})
    counts = {o: Counter() for o in OUTCOME_ORDER}
    for row in peps:
        counts[row["outcome"]][int(row["created_year"])] += 1
    fig, ax = plt.subplots(figsize=(10, 4.5))
    bottom = [0] * len(years)
    for outcome in OUTCOME_ORDER:
        values = [counts[outcome][y] for y in years]
        ax.bar(
            [y + 0.5 for y in years],
            values,
            width=0.9,
            bottom=bottom,
            label=outcome,
            color=COLOURS[outcome],
        )
        bottom = [b + v for b, v in zip(bottom, values, strict=True)]
    mark_changes(ax)
    ax.set_xlabel("Year created")
    ax.set_ylabel("PEPs")
    ax.set_title("PEPs by year of creation and current outcome")
    ax.legend(ncols=5, fontsize=8, loc="upper left")
    files.append(save(fig, "peps_by_year.png"))

    # 2. Median days to decision by year of decision (Standards Track, accepted/rejected).
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for outcome in ("accepted", "rejected"):
        by_year: dict[int, list[int]] = {}
        for row in peps:
            if row["type"] == "Standards Track" and row["outcome"] == outcome and measurable(row):
                year = int(str(row["decision_date"])[:4])
                by_year.setdefault(year, []).append(int(row["days_to_decision"]))
        xs = sorted(by_year)
        medians = [sorted(by_year[x])[len(by_year[x]) // 2] for x in xs]
        ax.plot([x + 0.5 for x in xs], medians, marker="o", label=outcome, color=COLOURS[outcome])
    mark_changes(ax)
    ax.set_yscale("log")
    ax.set_xlabel("Year of decision")
    ax.set_ylabel("Median days from Created (log scale)")
    ax.set_title("Time to decision, Standards Track")
    ax.legend(fontsize=8)
    files.append(save(fig, "time_to_decision_by_year.png"))

    # 3. Distinct and new authors per year of creation.
    rows = tables["participation_by_year"][1]
    xs = [int(r["created_year"]) + 0.5 for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(
        xs,
        [r["distinct_authors"] for r in rows],
        width=0.9,
        color="#cfd8dc",
        label="distinct authors",
    )
    ax.bar(
        xs,
        [r["new_authors"] for r in rows],
        width=0.5,
        color="#264653",
        label="first PEP that year",
    )
    mark_changes(ax)
    ax.set_xlabel("Year created")
    ax.set_ylabel("Authors")
    ax.set_title("Authors of PEPs created each year")
    ax.legend(fontsize=8, loc="upper left")
    files.append(save(fig, "authors_by_year.png"))

    plt.close("all")
    return files


def save(fig, name: str) -> str:
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / name, dpi=120)
    return name
