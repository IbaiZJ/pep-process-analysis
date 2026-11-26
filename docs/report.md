# Who Decides? The Python Enhancement Proposal process


Everything here is based on [python/peps](https://github.com/python/peps) at commit
`af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58`. Links to PEP files point to that commit and to the exact lines cited. All numbers
in Part 2 are produced by `uv run --locked pep-analysis` and collected in
`results/summary.md`.

## Part 1: Stakeholder map

Sources: PEP 1 (*PEP Purpose and Guidelines*), PEP 13 (*Python Language Governance*)
and the Python Developer's Guide.

### 1.1 Roles

| Role | Who | What they do | Source |
| --- | --- | --- | --- |
| **Author** | Anyone | Writes the PEP, leads the discussion and tries to reach consensus. Should test the idea publicly first. | PEP 1, [What is a PEP?](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L11-L31), [Start with an idea](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L120-L158) |
| **Sponsor** | Core team, PEP editors, Typing or Packaging Council members, or someone appointed by a council | Mentors the author through the process. Not needed if an author is a core developer. | PEP 1, [Finding a sponsor](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L160-L181) |
| **PEP editors** | Invited by the current editors | Check format, assign numbers, merge drafts, update statuses. They do not judge whether a PEP is good. | PEP 1, [PEP Editors](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L106-L118), [Editor workflow](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L775-L855) |
| **Steering Council** | 5 people elected by the core team after each feature release | Final authority on every PEP. Expected to use that power as little as possible. | PEP 1, [Steering Council](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L79-L86); PEP 13, [Composition](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0013.rst?plain=1#L43-L47), [Powers](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0013.rst?plain=1#L67-L96), [Election](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0013.rst?plain=1#L98-L126) |
| **PEP-Delegate** | A core developer approved by the Council | Decides one PEP for the Council. Formerly called `BDFL-Delegate`. | PEP 1, [Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L331-L410) |
| **Typing Council** | Defined in PEP 729 | Advises the Council on typing PEPs; does not decide. | PEP 1, [Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L346-L355) |
| **Core team** | Trusted volunteers | Elect the Council, review and merge code, and decide when a change needs a PEP. | PEP 13, [Role](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0013.rst?plain=1#L212-L231), [Prerogatives](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0013.rst?plain=1#L233-L238); Developer's Guide, [Core team responsibilities](https://devguide.python.org/core-team/responsibilities/) |
| **Commenters** | Anyone | Discuss on the public thread linked in `Discussions-To`. Their feedback is a key input for the decision. | PEP 1, [Discussing a PEP](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L270-L329) |
| **Release manager** | One per release | Publishes the release that brings the change to users. | [PEP 101](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0101.rst) |
| **Affected, no formal role** | Users, library and tool maintainers, other Python implementations | Live with the result; can join the discussion but have no vote. | PEP 1, [PEP Audience](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L33-L44) |

**Who can propose?** Anyone, but they need a sponsor unless an author is a core
developer, and editors check this before merging a draft
([Finding a sponsor](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L160-L181), [Editor workflow](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L786-L790)). Small changes
skip the PEP process and go to the issue tracker ([Start with an idea](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L120-L130);
[Changing Python](https://devguide.python.org/developer-workflow/lang-changes/)).

**Who decides?** The Steering Council, or a PEP-Delegate it appoints
([Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L331-L410)). Its authority comes from being elected by the
core team ([Python's BDFL](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L95-L104)). Until 2018 that authority belonged to
Guido van Rossum as BDFL, Python's creator (PEP 13, [History](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0013.rst?plain=1#L314-L340)).

**Where is it discussed?** On a public thread linked in `Discussions-To`, today usually
the Discourse forum and historically the Python-Dev mailing list. Decisions are posted
on Discourse and linked in the `Resolution` header
([Discussing a PEP](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L270-L329), [Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L411-L450)).

**Who implements?** PEP 1 only says the implementation must be merged before the PEP
becomes Final ([Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L416-L419)). In practice core team members
merge the code and are responsible for it ([Core team responsibilities](https://devguide.python.org/core-team/responsibilities/)).

### 1.2 Lifecycle

1. **Idea:** discussed in public, usually in the Discourse *Ideas* category
   ([Start with an idea](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L120-L158)).
2. **Sponsor:** found if no author is a core developer
   ([Finding a sponsor](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L160-L181)).
3. **Draft:** submitted as a pull request with `Status: Draft`; editors check the form,
   assign a number and merge it ([Submitting a PEP](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L183-L268)).
4. **Discussion:** on a public thread linked from the PEP
   ([Discussing a PEP](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L270-L329)).
5. **Decision:** the authors ask the Council for a review; the Council or a delegate
   accepts or rejects, and the decision is linked in `Resolution`
   ([Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L331-L450)).
6. **Implementation:** once the code is merged, the PEP becomes Final, and users get it
   in the next release ([Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L416-L419)).

### 1.3 Statuses

From [PEP Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L331-L473); allowed transitions are shown in the
[process flow diagram](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001/process_flow.svg).

| Status | Meaning |
| --- | --- |
| **Draft** | Under discussion. Every PEP starts here. |
| **Accepted** | Approved; implementation may still be pending. |
| **Provisional** | Accepted for now, but may still be rejected after release if feedback is bad. |
| **Final** | Accepted and implemented. |
| **Active** | Informational or Process PEPs that stay in force (such as PEP 1). |
| **Deferred** | No progress, or no delegate available. Can return to Draft. |
| **Rejected** | The decision-maker said no. |
| **Withdrawn** | The authors gave up, or prefer a competing proposal. |
| **Superseded** | Replaced by a newer PEP; meant for Informational PEPs. |

Two details matter for Part 2: rejected and withdrawn are different answers (one comes
from the decision-maker, the other from the authors), and an accepted PEP can still be
rejected, but only before it is released ([Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L461-L469)).

## Part 2: The process in data

### 2.1 Method

The code reads only the pinned commit:

- **Headers** of the 748 PEP files (`headers.py`), then cleaned (`clean.py`).
- **Status history** from the Git history (`history.py`). A PEP's **decision date** is
  when it last moved into its final group (Draft -> Accepted counts, Accepted -> Final
  does not). **Time to decision** is the decision date minus `Created`.
- **Outcome groups:** *accepted* (Accepted, Provisional, Final, Active), *rejected*,
  *withdrawn*, *superseded* and *open* (Draft, Deferred).
- **Rates** are computed over closed PEPs only (accepted, rejected or withdrawn), since
  open ones have no answer yet.
- **Periods:** BDFL until 2018-07-12, Transition until 2019-02-19, Steering Council
  after that (see 2.6).

### 2.2 Cleaning

The code logs every rule in `results/cleaning_log.csv`:

| Problem | Records | Fix |
| --- | ---: | --- |
| Joke PEP 401 (`April Fool!`) | 1 | Excluded, leaving 747 PEPs |
| E-mail addresses in `Author` | 1093 | Removed |
| Empty authors from trailing commas | 12 | Dropped |
| "Fred L. Drake, Jr." split in two | 2 | Not split before `Jr.` |
| "The Python core team and community" as author | 1 | Not counted as a person |
| Same name with and without accent | 1 | Merged |
| `BDFL-Delegate` / `PEP-Delegate` | 82 / 39 | Merged into one column |
| Old or misspelt statuses in history (`Incomplete`, `Acepted`, `Draught`...) | 33 | Mapped to PEP 1 statuses |
| Empty status in history | 1 | Ignored |
| Renumbered PEPs (e.g. 837 -> 840) | 7 | History moved to the new number |
| Status changed only in a merge commit (PEP 405) | — | Merge commits included |
| Bulk commits changing 10+ statuses at once | 4 commits | Their 13 decisions excluded from timing |
| PEPs added to the repository already decided | 47 | No decision date |

Two checks run every time and both give 0: PEPs whose history ends in a different status
than their header, and PEPs with no status in their history.

I checked a few PEPs by hand against the repository: PEP 160 has one author, not two;
PEP 394 has six authors on several lines; PEP 484 has three authors, a delegate, and is
dated to its acceptance commit in May 2015; PEP 572 to its
[acceptance commit](https://github.com/python/peps/commit/8846efd623531c0c50ff417800235ce92dc1d51c); PEP 405 to May 2012,
which only worked after including merge commits.

### 2.3 Outcomes

Of 747 PEPs, 426 are accepted, 131 rejected, 74 withdrawn, 25 superseded and 91 open
(`results/outcomes.csv`):

| Type | PEPs | Closed | Accepted | Rejected | Withdrawn |
| --- | ---: | ---: | ---: | ---: | ---: |
| Standards Track | 589 | 489 | 65.2 % | 23.7 % | 11.0 % |
| Informational | 106 | 94 | 75.5 % | 12.8 % | 11.7 % |
| Process | 52 | 48 | 75.0 % | 6.2 % | 18.8 % |

For proposals that change the language (Standards Track), about a third end in a no:
23.7 % rejected by the decision-makers and 11.0 % withdrawn by their own authors.

One mismatch with the documentation: PEP 1 says Superseded is meant for Informational
PEPs ([Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L451-L453)), but 16 of the 25 superseded PEPs are
Standards Track.

### 2.4 Time to decision

Days from `Created` to decision (`results/time_to_decision.csv`):

| Outcome | PEPs | Median | 25 % | 75 % |
| --- | ---: | ---: | ---: | ---: |
| Accepted | 381 | 148 | 47 | 409 |
| Rejected | 120 | 275.5 | 53 | 1169 |
| Withdrawn | 70 | 735.5 | 176 | 1862 |

Yes comes faster than no: about five months for acceptance, nine for rejection and two
years for withdrawal. Many rejected and withdrawn PEPs sit for years before anyone
closes them.

### 2.5 Participation

There are 370 distinct authors, and a small group writes much of the work
(`results/authors_by_pep_count.csv`):

| PEPs written | Authors | % of authors | % of authorships |
| --- | ---: | ---: | ---: |
| 1 | 201 | 54.3 % | 17.3 % |
| 2-4 | 113 | 30.5 % | 24.8 % |
| 5-9 | 35 | 9.5 % | 19.7 % |
| 10+ | 21 | 5.7 % | 38.2 % |

The 21 authors with ten or more PEPs appear on 49.5 % of all PEPs, and the top 10 % of
authors hold 49.0 % of authorships. At the same time, more than half of all authors
wrote only one PEP. New authors arrive every year (`results/participation_by_year.csv`,
`results/authors_by_year.png`).

### 2.6 Change over time

The history of PEP 1 and PEP 13 shows when the rules changed (all links in
`docs/worklog.md`):

| Date | Change | Evidence |
| --- | --- | --- |
| 2012-05-06 | BDFL can delegate decisions (`BDFL-Delegate`) | [73310d44](https://github.com/python/peps/commit/73310d446896704e8a434fcd704463fd47b0364b) |
| 2018-07-12 | BDFL steps down | [python-committers](https://mail.python.org/pipermail/python-committers/2018-July/005664.html) |
| 2019-02-20 | Steering Council becomes final authority | [83687f6e](https://github.com/python/peps/commit/83687f6ee354a6feac2f1ddc7a0f27fd8bbe65ef) |
| 2019-03-04 | Sponsors introduced | [c58d32c3](https://github.com/python/peps/commit/c58d32c33bd06eb386d3f33963a1434510528f68) |
| 2020-10-26 | `BDFL-Delegate` renamed `PEP-Delegate` | [a169cac7](https://github.com/python/peps/commit/a169cac7d59498d3b1d8e611756eac973d0bf402) |
| 2022-09-20 | Discourse replaces Python-Dev as main venue | [b18ca66c](https://github.com/python/peps/commit/b18ca66cb5bcbad28b938752fc650839a1cce63d) |

**During the transition, decisions stopped.** From July 2018 to February 2019, no
Standards Track PEP was decided. The only 8 decisions were about governance itself
(`results/decisions_by_period.csv`). PEP 572 was accepted the same day the BDFL
stepped down, so the transition starts the following day.

Standards Track, by period of decision (`results/outcomes_by_period.csv`,
`results/time_to_decision_by_period.csv`, `results/delegation_by_period.csv`,
`results/documentation_by_period.csv`):

| | BDFL | Steering Council |
| --- | ---: | ---: |
| Decisions | 279 | 189 |
| Accepted | 64.2 % | 69.8 % |
| Rejected | 26.2 % | 17.5 % |
| Withdrawn | 9.7 % | 12.7 % |
| Median days to accept | 99 | 151.5 |
| Median days to reject | 376 | 234 |
| Decided by a named delegate | 12.5 % | 31.2 % |
| `Resolution` link present | 28.0 % | 78.3 % |
| `Sponsor` present | 0 | 35.4 % |

By period of creation (`results/participation_by_period.csv`, `results/venue_by_year.csv`):

| | BDFL | Steering Council |
| --- | ---: | ---: |
| PEPs created | 467 | 268 |
| Mean authors per PEP | 1.39 | 1.80 |
| PEPs with an author of 10+ PEPs | 53.1 % | 41.4 % |

The discussion venue is rarely recorded before 2019 (392 of 467 BDFL-period PEPs have
no `Discussions-To`). Discourse already appears in 15 of 32 PEPs created in 2019, and in
22 of 25 in 2022, the year PEP 1 made it official.

Charts (generated, not committed): `results/peps_by_year.png`,
`results/time_to_decision_by_year.png`, `results/authors_by_year.png`.

### 2.7 Limits

- **Time to decision is the least reliable number.** It runs from `Created` to the
  status change in the repository, which can lag behind the real discussion and the
  announcement.
- **The Steering Council period is not over.** 21.3 % of its PEPs are still open, against
  7.3 % for the BDFL period (`results/open_by_created_period.csv`). Late rejections and
  withdrawals are still missing, so its lower rejection rate may not hold.
- **Who decided is often unrecorded.** Without a named delegate, the data cannot show
  who made the call, so the delegate share is a minimum.
- **Author counts are approximate.** Names are matched only up to accents and case, and
  recent authors have had less time to reach ten PEPs.
- **Some dates are missing:** 13 decisions come from bulk clean-ups and 47 PEPs were
  added already decided.

## Part 3: Tracing one change

**PEP 572, Assignment Expressions** (the `:=` "walrus" operator), released in
Python 3.8. It is a good case because it is the last decision of the BDFL era and the one
that ended it.

### 3.1 From idea to release

| Date | Stage | Evidence | Roles |
| --- | --- | --- | --- |
| before 2018 | **Earlier ideas.** The PEP itself says similar proposals had come up often on python-ideas. | [PEP 572, Rejected alternatives](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0572.rst?plain=1#L675-L679) | Community |
| 2018-02-27 | **First public proposal.** Chris Angelico posts the full draft to python-ideas as "Statement-Local Name Bindings". | [python-ideas post](https://mail.python.org/pipermail/python-ideas/2018-February/049041.html); [first commit cc710b28](https://github.com/python/peps/commit/cc710b28c89ea6152e81e12aa85405070df84f53) | Author |
| Mar-Jul 2018 | **Discussion.** Eight rounds on python-ideas and python-dev (listed in `Post-History`). The design changes completely, from a statement-local name to `:=`. | [PEP 572 header](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0572.rst?plain=1#L1-L12) | Author, commenters |
| 2018-05-22 | **Guido van Rossum and Tim Peters become co-authors.** | [commit 6d81538e](https://github.com/python/peps/commit/6d81538ecb9592ed14aa5bdeadf1502dda7cd0d3) | Authors |
| 2018-07-10 | **Last call.** Guido announces he plans to accept within a week and asks only for wording fixes. | [python-dev thread](https://mail.python.org/archives/list/python-dev@python.org/thread/4DVSDPKXF4V7II4MYO2FVOISI6XPLEIA/) | Decision-maker |
| 2018-07-11 | **Decision.** Guido accepts the PEP on python-dev; status changes to Accepted. | [python-dev, "Accepting PEP 572"](https://mail.python.org/pipermail/python-dev/2018-July/154601.html) (the `Resolution` link); [commit 8846efd6](https://github.com/python/peps/commit/8846efd623531c0c50ff417800235ce92dc1d51c) | BDFL (also co-author) |
| 2018-07-12 | **Guido steps down as BDFL**, citing the fight over this PEP. | [python-committers, "Transfer of power"](https://mail.python.org/pipermail/python-committers/2018-July/005664.html) | — |
| 2018-11-12 | **Implementation starts.** Emily Morehouse opens a tracker issue and a pull request. | [bpo-35224](https://bugs.python.org/issue35224); [cpython PR #10497](https://github.com/python/cpython/pull/10497) | Implementer |
| 2019-01-24 | **Implementation merged** into CPython after review by other core developers. | [cpython commit 8f59ee01](https://github.com/python/cpython/commit/8f59ee01be3d83d5513a9a3f654a237d77d80d9a) | Implementer, reviewers |
| 2019 | **Spec adjusted during implementation**, e.g. the planned `TargetScopeError` is dropped in favour of `SyntaxError`. | [PEP 572, Specification changes during implementation](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0572.rst?plain=1#L456-L473) | Core developers |
| 2019-10-14 | **Release.** Python 3.8.0 ships with assignment expressions. | [What's New in Python 3.8](https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions); [PEP 569 schedule](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0569.rst?plain=1#L23-L26) and [release date](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0569.rst?plain=1#L68-L69) | Release manager (Łukasz Langa) |
| 2022-11-06 | **Status set to Final**, three years after the release. | [commit a1f1fed4](https://github.com/python/peps/commit/a1f1fed495befa6eb9e935102bbfa714c7e1b863) | PEP editors |

### 3.2 Compared with the general process

**What matches Part 1:**

- The idea was tested in public before anything was decided, the discussion was public
  (`Post-History`), and the decision was posted and linked in `Resolution`.
- No sponsor was needed because one of the authors was a core developer.
- The specification was adjusted during implementation and the changes were recorded in
  the PEP, as PEP 1 asks.

**What departs from it:**

- **The decision-maker was also an author.** Guido joined as co-author in May and
  accepted the PEP in July. Under the BDFL model nobody stood above him. Today PEP 1
  names conflicts of interest as a reason to refuse someone as PEP-Delegate
  ([Review & Resolution](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0001.rst?plain=1#L373-L380)), and PEP 13 makes council members with a
  conflict abstain ([Powers](https://github.com/python/peps/blob/af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58/peps/pep-0013.rst?plain=1#L88-L91)).
- **The decision cost the decision-maker his role.** The next day Guido stepped down,
  and for seven months no Standards Track PEP was decided (Part 2.6). The
  implementation, however, kept going: it was merged during that gap.
- **The implementer was not an author.** Emily Morehouse wrote and merged the code,
  which PEP 1 leaves open (Part 1.1).
- **The paperwork lagged behind reality.** The PEP was marked Final only in 2022, in a
  clean-up commit, although the feature had shipped in 2019. This is the same effect that
  makes time-to-decision in Part 2 measure "when the file was updated" rather than
  "when it was decided".

## Part 4: Interpretation

### Where does power sit?

On paper, with the Steering Council (1.1). In practice it is shared out more and more:
the share of Standards Track decisions taken by a named delegate went from 12.5 % to
31.2 % (2.6). That is what PEP 13 asks for: the Council should use its power rarely and
set up processes instead of ruling case by case (1.1).

Under the BDFL the power was real but concentrated in one person, who could even decide
his own proposal (3.2). That made him a single point of failure. When he stepped down,
decisions on language changes stopped completely for seven months (2.6), while work that
was already decided, such as the PEP 572 implementation, carried on (3.1). Authority to
decide was the bottleneck, not people willing to do the work.

### How open is it really?

Open to take part, less open to shape. Anyone can propose and comment (1.1). More than
half of all authors wrote a single PEP, and new authors appear every year (2.5). But
half of all PEPs have one of 21 frequent authors on them (2.5), and since 2019 an outsider
needs a core developer or other approved person as sponsor (1.1). About a third of
Council-era decisions record one (2.6). Users and other affected groups can speak but
have no vote; the decision-makers are chosen by the core team only (1.1).

### Where are the bottlenecks?

- **Saying no.** Acceptance takes about five months, rejection nine and withdrawal two
  years (2.4). Proposals nobody wants to decide on simply stay open.
- **The decision-maker.** The transition shows the cost of having one (2.6); delegation
  spreads the load (2.6).
- **Paperwork.** Status changes often lag behind events. PEP 572 shipped in 2019 but was
  marked Final in 2022 (3.1), and many statuses were later fixed in bulk commits (2.2).
  In course terms, the *definition of done* for a PEP ("implementation merged", 1.2) is
  clear, but the status that should show it is not kept up to date.

### Why did it change, and did it work?

The change was not planned. It was triggered by one hard decision, PEP 572, after which
the BDFL stepped down (3.1). The community then spent seven months choosing a new model
(2.6). The new rules aimed at shared, public and recorded decisions (1.1). The data
mostly moves in that direction:

- **More delegation** (12.5 % -> 31.2 %, 2.6).
- **Decisions better recorded:** a `Resolution` link in 78.3 % of decisions instead of
  28.0 % (2.6). This works as a quality gate that is now actually used.
- **Discussion in one public place:** Discourse took over in practice around 2019-2022,
  before PEP 1 made it the rule in 2022 (2.6). Here the documentation followed practice,
  not the other way round.
- **More collaboration:** 1.80 authors per PEP instead of 1.39 (2.6).

Other changes, such as the lower rejection rate (26.2 % -> 17.5 %) and faster rejections,
should not be read as success yet: a fifth of the Council-era PEPs are still open, and
late rejections are exactly what is missing (2.7).
