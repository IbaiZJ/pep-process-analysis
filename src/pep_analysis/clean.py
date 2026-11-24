"""Clean the raw PEP headers into analysable tables, logging every cleaning decision.

Outputs (in results/):
- peps_clean.csv     one row per PEP kept in the analysis
- pep_authors.csv    one row per (PEP, author) pair, names only (no e-mail addresses)
- cleaning_log.csv   every cleaning rule and how many records it affected
"""

import csv
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from pep_analysis.config import RESULTS_DIR

# Statuses defined in PEP 1, grouped into outcomes. PEP 1 describes Accepted, Final and
# Active as states of a proposal that was approved (Active is used by Process and
# Informational PEPs that stay in force). Rejected is a "no" by the decision-maker,
# Withdrawn a "no" by the authors themselves, so they are kept separate.
OUTCOMES = {
    "Accepted": "accepted",
    "Final": "accepted",
    "Active": "accepted",
    "Rejected": "rejected",
    "Withdrawn": "withdrawn",
    "Draft": "open",
    "Deferred": "open",
    "Provisional": "open",
    "Superseded": "superseded",
}

# Values of Author that name a group rather than a person. They are kept on the PEP but
# not counted as authors in the participation analysis.
NON_PERSON_AUTHORS = {"the python core team and community"}

# Authors are separated by commas, except before a suffix such as "Jr."
# ("Fred L. Drake, Jr." is one person).
AUTHOR_SEPARATOR = re.compile(r",(?!\s*Jr\.)")
# E-mail addresses appear as "<user@host>" or obfuscated as "<user at host>".
EMAIL = re.compile(r"\s*<[^>]*>")


@dataclass
class CleaningLog:
    """Collects (rule, records affected, note) entries in the order the rules run."""

    entries: list[tuple[str, int, str]] = field(default_factory=list)

    def add(self, rule: str, affected: int, note: str = "") -> None:
        self.entries.append((rule, affected, note))


def author_key(name: str) -> str:
    """Normalise a name for matching: no accents, case-folded, single spaces, no dots.

    This merges spelling variants such as "Marc-André" and "Marc-Andre".
    """
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return " ".join(ascii_name.casefold().replace(".", " ").split())


def split_authors(value: str) -> tuple[list[str], int, int]:
    """Split an Author header into names.

    Returns the names, the number of e-mail addresses removed and the number of empty
    entries dropped (caused by trailing commas such as "Name <email>,").
    """
    names = []
    emails = 0
    empty = 0
    for part in AUTHOR_SEPARATOR.split(value):
        if EMAIL.search(part):
            emails += 1
        name = EMAIL.sub("", part).strip()
        if name:
            names.append(name)
        else:
            empty += 1
    return names, emails, empty


def parse_created(value: str, pep: str) -> date:
    """Parse the Created header ("29-Sep-2014"). Fail loudly on any other format."""
    try:
        return datetime.strptime(value, "%d-%b-%Y").date()
    except ValueError as error:
        msg = f"PEP {pep}: unexpected Created value {value!r}"
        raise ValueError(msg) from error


def clean(
    raw_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], CleaningLog]:
    """Apply every cleaning rule and return (PEP rows, author rows, log)."""
    log = CleaningLog()
    log.add("PEP files read at the pinned commit", len(raw_rows))

    # Rule 1: drop statuses that are not part of the PEP 1 lifecycle. The only one at the
    # pinned commit is "April Fool!" (PEP 401, a joke). Anything else unknown is an error.
    kept = [row for row in raw_rows if row.get("Status") in OUTCOMES]
    excluded = [row for row in raw_rows if row.get("Status") not in OUTCOMES]
    for row in excluded:
        if row.get("Status") != "April Fool!":
            msg = f"PEP {row['PEP']}: unknown Status {row.get('Status')!r}"
            raise ValueError(msg)
    log.add(
        "Excluded: Status not in PEP 1 lifecycle",
        len(excluded),
        "; ".join(f"PEP {row['PEP']} ({row['Status']})" for row in excluded),
    )

    peps: list[dict[str, object]] = []
    authors: list[dict[str, object]] = []
    emails_removed = 0
    empty_dropped = 0
    non_person = 0
    jr_suffix = 0
    spellings: dict[str, set[str]] = defaultdict(set)

    for row in kept:
        pep = row["PEP"]
        names, emails, empty = split_authors(row.get("Author", ""))
        emails_removed += emails
        empty_dropped += empty
        jr_suffix += sum("Jr." in name for name in names)

        people = []
        for name in names:
            if author_key(name) in NON_PERSON_AUTHORS:
                non_person += 1
                continue
            people.append(name)
            spellings[author_key(name)].add(name)

        # Rule: BDFL-Delegate (before the 2018 governance change) and PEP-Delegate
        # (after it) record the same role, so they are merged into one column while
        # keeping which field it came from.
        if row.get("BDFL-Delegate"):
            delegate, delegate_field = row["BDFL-Delegate"], "BDFL-Delegate"
        elif row.get("PEP-Delegate"):
            delegate, delegate_field = row["PEP-Delegate"], "PEP-Delegate"
        else:
            delegate, delegate_field = "", ""

        created = parse_created(row["Created"], pep)
        peps.append(
            {
                "pep": int(pep),
                "title": row.get("Title", ""),
                "type": row.get("Type", ""),
                "topic": row.get("Topic", ""),
                "status": row["Status"],
                "outcome": OUTCOMES[row["Status"]],
                "created": created.isoformat(),
                "created_year": created.year,
                "python_version": row.get("Python-Version", ""),
                "n_authors": len(people),
                "delegate": EMAIL.sub("", delegate).strip(),
                "delegate_field": delegate_field,
                "has_resolution": bool(row.get("Resolution")),
            }
        )
        for position, name in enumerate(people, start=1):
            authors.append(
                {
                    "pep": int(pep),
                    "position": position,
                    "author": name,
                    "author_key": author_key(name),
                }
            )

    log.add("Created parsed as DD-Mon-YYYY", len(peps), "any other format stops the run")
    log.add("Author: e-mail addresses removed", emails_removed, "personal data, never output")
    log.add("Author: empty entries dropped", empty_dropped, "trailing commas in the header")
    log.add("Author: 'Jr.' kept with the preceding name", jr_suffix, "not split on that comma")
    log.add("Author: group names not counted as people", non_person, ", ".join(NON_PERSON_AUTHORS))
    variants = {key: names for key, names in spellings.items() if len(names) > 1}
    log.add(
        "Author: spelling variants merged (accents, case, dots)",
        len(variants),
        "; ".join(" = ".join(sorted(names)) for names in variants.values()),
    )
    by_field = defaultdict(int)
    for pep_row in peps:
        if pep_row["delegate_field"]:
            by_field[pep_row["delegate_field"]] += 1
    log.add("Delegate taken from BDFL-Delegate", by_field["BDFL-Delegate"])
    log.add("Delegate taken from PEP-Delegate", by_field["PEP-Delegate"])
    log.add("PEPs kept for analysis", len(peps))
    return peps, authors, log


def write_rows(rows: list[dict[str, object]], path: Path) -> None:
    """Write a list of dicts with identical keys to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(raw_rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], CleaningLog]:
    """Clean the raw headers and write the clean tables and the cleaning log."""
    peps, authors, log = clean(raw_rows)
    write_rows(peps, RESULTS_DIR / "peps_clean.csv")
    write_rows(authors, RESULTS_DIR / "pep_authors.csv")
    log_rows = [{"rule": r, "records": n, "note": note} for r, n, note in log.entries]
    write_rows(log_rows, RESULTS_DIR / "cleaning_log.csv")
    return peps, log
