"""Helpers shared by the analysis modules."""

from datetime import date

from pep_analysis.config import PERIODS

Row = dict[str, object]
Table = list[dict[str, object]]

OUTCOME_ORDER = ["accepted", "rejected", "withdrawn", "superseded", "open"]
# A PEP has a final answer if it was accepted, rejected or withdrawn. Superseded PEPs are
# counted apart: being replaced by a later proposal is not an answer to the proposal.
CLOSED = ("accepted", "rejected", "withdrawn")


def period_of(day: str) -> str:
    """Return the governance period that contains an ISO date."""
    current = PERIODS[0][0]
    for name, start in PERIODS:
        if date.fromisoformat(day) >= date.fromisoformat(start):
            current = name
    return current


def pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.1f}" if whole else ""


def measurable(row: Row) -> bool:
    """True if the PEP has a decision date that can be trusted (see history.py)."""
    return (
        row["outcome"] in CLOSED
        and row["days_to_decision"] != ""
        and not row["decision_in_bulk_commit"]
    )
