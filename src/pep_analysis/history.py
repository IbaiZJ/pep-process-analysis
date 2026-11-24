"""Reconstruct the status history of every PEP from the Git history at the pinned commit.

A single `git log -p` over the whole repository (stopping at the pinned commit) lists
every commit that added or removed a `Status:` line. Files are matched to PEPs by their
file name (pep-NNNN.txt or pep-NNNN.rst), so moves between directories and the
.txt -> .rst conversion do not break the history of a proposal. A second `git log`
finds renames that change the PEP number (renumbered proposals), and the earlier
history is moved to the new number.
"""

import itertools
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime

from pep_analysis.clean import OUTCOMES, CleaningLog
from pep_analysis.config import PINNED_COMMIT
from pep_analysis.git import git

# Status values that appear in the history but are not (or no longer) defined in PEP 1,
# mapped to their PEP 1 equivalent. "Incomplete" was used in the initial set of PEPs in
# 2000 for proposals that were not written yet. The rest are older names or typos.
HISTORICAL_STATUS = {
    "Incomplete": "Draft",
    "Draught": "Draft",
    "Approved": "Accepted",
    "Acepted": "Accepted",
    "Complete": "Final",
    "Finished": "Final",
    "Replaced": "Superseded",
    "Postponed": "Deferred",
    "Withdrawal": "Withdrawn",
}

PEP_PATH = re.compile(r"(?:^|/)pep-(\d{4})\.(?:txt|rst)$")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
# Only Status lines in the header count; the header of every PEP is far shorter than this,
# so a "Status:" line further down is example text in the body.
MAX_HEADER_LINE = 60
# A commit that changes the status of this many PEPs or more is a bulk clean-up by the
# editors, not an individual decision; its date says when the file was updated, not
# when the proposal was decided.
BULK_THRESHOLD = 10
# Separates commits in the git log output (git writes it for %x00); cannot appear in a
# diff. It cannot be passed literally because arguments may not contain NUL bytes.
COMMIT_MARK = "\x00"


@dataclass
class StatusEvent:
    pep: int
    commit: str
    day: date
    raw: str
    status: str


def commit_order() -> dict[str, int]:
    """Position of every commit up to the pinned one, oldest first (same order as git log)."""
    hashes = git("rev-list", "--reverse", PINNED_COMMIT).split()
    return {commit: position for position, commit in enumerate(hashes)}


def read_renumberings() -> list[tuple[str, int, int]]:
    """Return (commit, old number, new number) for every rename that changed the number."""
    output = git(
        "log",
        PINNED_COMMIT,
        "-M",
        "--diff-merges=first-parent",
        "--diff-filter=R",
        "--name-status",
        "--format=%x00%H",
    )
    renames = []
    for block in output.split(COMMIT_MARK)[1:]:
        lines = block.splitlines()
        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) != 3 or not parts[0].startswith("R"):
                continue
            old, new = PEP_PATH.search(parts[1]), PEP_PATH.search(parts[2])
            if old and new and old.group(1) != new.group(1):
                renames.append((lines[0], int(old.group(1)), int(new.group(1))))
    return renames


def read_status_lines() -> list[tuple[int, str, date, str]]:
    """Return (pep, commit, commit date in UTC, raw status) for every added Status line."""
    output = git(
        "log",
        PINNED_COMMIT,  # never anything newer than the snapshot
        "--reverse",  # oldest first
        "-M",  # detect renames so pure moves produce no Status lines
        "-G^Status:",  # only commits whose diff touches a Status line
        # Show merge commits as a diff against their first parent: some status changes
        # were only made while merging (for example PEP 405 becoming Final in 2012).
        "--diff-merges=first-parent",
        "-p",
        "--unified=0",
        "--no-color",
        "--format=%x00%H%x09%cI",
    )
    lines_found = []
    for block in output.split(COMMIT_MARK)[1:]:
        lines = block.splitlines()
        commit, committed = lines[0].split("\t")
        # Committer date: when the change landed in the repository (for merged pull
        # requests this is the merge, not when the author first wrote it).
        day = datetime.fromisoformat(committed).astimezone(UTC).date()
        pep = None
        new_line = 0
        for line in lines[1:]:
            if line.startswith("+++ "):
                match = PEP_PATH.search(line[4:])
                pep = int(match.group(1)) if match else None
            elif (hunk := HUNK.match(line)) is not None:
                new_line = int(hunk.group(1))
            elif line.startswith("+") and not line.startswith("+++"):
                if pep is not None and line.startswith("+Status:") and new_line <= MAX_HEADER_LINE:
                    lines_found.append((pep, commit, day, line[len("+Status:") :].strip()))
                new_line += 1
    return lines_found


def normalise(raw: str) -> str | None:
    """Map a raw status to a PEP 1 status, or None if it is not a status at all."""
    value = HISTORICAL_STATUS.get(raw, raw)
    return value if value in OUTCOMES else None


def run(peps: list[dict[str, object]], log: CleaningLog) -> list[StatusEvent]:
    """Add decision dates to the PEP rows and return the status events used."""
    wanted = {row["pep"] for row in peps}
    order = commit_order()
    lines = sorted(read_status_lines(), key=lambda line: order[line[1]])

    # Renumbered proposals: Status lines written under the old number before the rename
    # belong to the new number. Renames are applied oldest first, so chains work.
    renumberings = sorted(read_renumberings(), key=lambda rename: order[rename[0]])
    moved = 0
    for rename_commit, old, new in renumberings:
        position = order[rename_commit]
        for index, (pep, commit, day, raw) in enumerate(lines):
            if pep == old and order[commit] < position:
                lines[index] = (new, commit, day, raw)
                moved += 1

    events: list[StatusEvent] = []
    renamed = 0
    ignored: list[str] = []
    for pep, commit, day, raw in lines:
        if pep not in wanted:
            continue
        status = normalise(raw)
        if status is None:
            ignored.append(raw)
            continue
        if status != raw:
            renamed += 1
        events.append(StatusEvent(pep, commit, day, raw, status))

    # Keep only real transitions: a Status line re-added with the same value (for example
    # when a file was converted from .txt to .rst) is not a change.
    by_pep: dict[int, list[StatusEvent]] = defaultdict(list)
    for event in events:
        history = by_pep[event.pep]
        if not history or history[-1].status != event.status:
            history.append(event)

    changes_per_commit: dict[str, int] = defaultdict(int)
    for history in by_pep.values():
        for event in history[1:]:
            changes_per_commit[event.commit] += 1
    bulk_commits = {c for c, n in changes_per_commit.items() if n >= BULK_THRESHOLD}

    mismatches = 0
    no_history = 0
    added_decided = 0
    bulk_decisions = 0
    for row in peps:
        history = by_pep.get(row["pep"], [])
        row["status_changes"] = max(len(history) - 1, 0)
        row["first_status_date"] = history[0].day.isoformat() if history else ""
        row["decision_date"] = ""
        row["days_to_decision"] = ""
        row["decision_in_bulk_commit"] = False
        row["added_already_decided"] = False
        if not history:
            no_history += 1
            continue
        if history[-1].status != row["status"]:
            mismatches += 1
        if row["outcome"] == "open":
            continue
        # Decision = the last time the status entered the final outcome group.
        group = row["outcome"]
        decision = history[0]
        for previous, event in itertools.pairwise(history):
            if OUTCOMES[event.status] == group and OUTCOMES[previous.status] != group:
                decision = event
        if decision is history[0]:
            # The file was first committed with its final status (e.g. a PEP written up
            # after the fact): there is no decision event to measure.
            added_decided += 1
            row["added_already_decided"] = True
            continue
        row["decision_date"] = decision.day.isoformat()
        row["days_to_decision"] = (decision.day - date.fromisoformat(row["created"])).days
        if decision.commit in bulk_commits:
            bulk_decisions += 1
            row["decision_in_bulk_commit"] = True

    ignored_note = ", ".join(sorted({repr(value) for value in ignored}))
    log.add("History: Status lines read (up to the pinned commit)", len(events) + len(ignored))
    log.add(
        "History: renumbered proposals (history moved to new number)",
        len(renumberings),
        f"{moved} Status lines moved; "
        + ", ".join(f"{old}->{new}" for _, old, new in renumberings),
    )
    log.add("History: old or misspelt statuses mapped to PEP 1", renamed, "see HISTORICAL_STATUS")
    log.add("History: values that are not a status ignored", len(ignored), ignored_note)
    log.add("History: PEPs whose last status differs from header", mismatches, "should be 0")
    log.add("History: PEPs with no Status line in history", no_history, "should be 0")
    log.add(
        f"History: bulk commits (>= {BULK_THRESHOLD} status changes)",
        len(bulk_commits),
        ", ".join(sorted(c[:10] for c in bulk_commits)),
    )
    log.add("History: decisions dated by a bulk commit", bulk_decisions, "date is unreliable")
    log.add("History: decided PEPs first committed already decided", added_decided, "no date")
    return events
