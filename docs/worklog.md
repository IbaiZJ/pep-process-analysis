# Worklog

## 2026-11-24 — Repository setup and pinned snapshot

### What I did

- Created the GitHub repository `IbaiZJ/pep-process-analysis` and cloned it locally
  into the folder `ad-lo1-hw`.
- Added an MIT licence.
- Cloned the PEP repository into `data/peps/` as the data source for the analysis.
- Added `.gitignore`, `.gitattributes` and `.editorconfig`.
- Started `docs/worklog.md` and `docs/links.md`.

### Commands

```bash
git clone https://github.com/IbaiZJ/pep-process-analysis.git ad-lo1-hw
cd ad-lo1-hw
git clone https://github.com/python/peps.git data/peps
git -C data/peps rev-parse HEAD # -> af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58
git -C data/peps rev-parse --is-shallow-repository
git -C data/peps log -1 --format='%H %ci %s' af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58
```

### Decisions

- **Pinned snapshot:** `af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58`, the latest commit on `main` when I cloned
  (committed 2026-11-23 23:38 +0200, "PEP 847: link to living PyPA spec (#5239)").
  Every result will be computed from this commit only, so the numbers stay the same
  even when the PEP repository changes later. Code will read files with
  `git show <commit>:<path>` and history with `git log <commit>`, never from the
  working tree or plain `git log`.
- **Full clone, not shallow:** the analysis needs the complete Git history (dates of
  status changes, authors over time), so `--depth 1` is not an option.
- **`data/` is ignored:** the studied repository must never be committed.
- **Assignment document kept out of the repository:** `docs/ad-lo1-hw.docx` is listed
  in `.gitignore`; it is not part of the project.
- **Line endings:** `.gitattributes` with `* text=auto eol=lf` enforces LF in the
  repository regardless of each machine's `core.autocrlf`; `.editorconfig` sets UTF-8,
  LF and final newlines for editors.

### Problems

- Some files were saved with CRLF in the working tree; Git stores them as LF in the
  index thanks to `.gitattributes`, and they were converted to LF on disk too.

### Checks

- `ls data/peps/peps/pep-*.rst | wc -l` -> 748 proposal files at the pinned commit.
- `git status` does not list `data/` or the assignment document.
- `git ls-files --eol` shows `i/lf` (LF in the index) for every committed text file.

## 2026-11-24 — Linux environment (WSL) and Python project setup

### What I did

- Moved development to WSL, because the project is reviewed on Linux. The first
  terminal I opened was Docker Desktop's internal `docker-desktop` distribution (no
  `sudo`, no `apt`); installed Ubuntu as a proper WSL distribution and made it the default.
- Installed `git` and `uv` inside Ubuntu. uv also downloads and manages the Python
  interpreter, so Python is not installed separately.
- Kept working in the existing Windows folder, opened from WSL through `/mnt/c/...`,
  instead of cloning again into the Linux home directory. From now on all `git`
  commands for this repository are run from WSL only.
- Created the Python project with uv and added Ruff as a pinned development dependency.

### Commands

```powershell
# Windows PowerShell
wsl -l -v
wsl --install -d Ubuntu-24.04
wsl --set-default Ubuntu-24.04
```

```bash
# Ubuntu (WSL)
sudo apt update && sudo apt install -y git
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
git --version
uv --version
lsb_release -a

uv init --package --name pep-analysis --python 3.13
uv add --dev ruff
uv run ruff format --check .
uv run ruff check .
uv run pep-analysis
```

### Toolchain

| Tool | Version |
| --- | --- |
| Linux distribution | Ubuntu 24.04 (WSL 2) — TODO: exact release from `lsb_release -a` |
| git | TODO: from `git --version` |
| uv | 0.13.9 |
| Python | 3.13 (managed by uv) — TODO: exact patch version from `uv run python --version` |
| Ruff | 0.17.6 (pinned in `uv.lock`) |

### Decisions

- **uv as the package and project manager:** one tool installs the Python version,
  creates the virtual environment and writes a lockfile (`uv.lock`), so the reviewer gets
  exactly the same versions.
- **Packaged layout (`uv init --package`):** code lives in `src/pep_analysis/`, which is
  the layout uv expects, and the analysis can be started with `uv run pep-analysis`.
- **Python 3.13**, pinned in `.python-version` and `requires-python`.
- **Ruff for formatting and linting**, configured in `pyproject.toml`. Besides the default
  pycodestyle (`E`, `W`) and pyflakes (`F`) rules, I enabled:
  - `I` (import order), `N` (naming conventions) and `UP` (modern syntax) for consistent style;
  - `B` (bugbear) and `SIM` (simplify) to catch likely bugs and needlessly complex code;
  - `PTH` (pathlib), because all paths must be resolved relative to the repository and
    pathlib makes that explicit;
  - `RUF` (Ruff's own rules).
- Line length 100 instead of 88, to keep long `git` command strings readable.
- Added `.venv/`, `__pycache__/` and `.ruff_cache/` to `.gitignore`: generated files
  are never committed.

### Checks

- `uv run ruff format --check .` and `uv run ruff check .` pass with no errors.
- `uv run pep-analysis` runs the placeholder entry point.
- `git status` does not list `.venv/`, `.ruff_cache/` or `__pycache__/`.

## 2026-11-24 — Fetching the data and extracting PEP headers

### What I did

- Wrote the first part of the pipeline in `src/pep_analysis/`:
  - `config.py`: repository paths and the pinned commit, hard-coded.
  - `git.py`: helper to run `git -C data/peps ...` and to check that a commit exists.
  - `fetch.py`: clones `python/peps` into `data/peps/` if it is missing and checks that
    the pinned commit is present (fetching once if it is not).
  - `headers.py`: lists the PEP files at the pinned commit, reads each one with
    `git show`, parses its header block and writes `results/pep_headers_raw.csv`.
  - `main()` in `__init__.py` runs both steps and prints the raw status counts.

### Commands

```bash
uv run pep-analysis
uv run ruff format --check .
uv run ruff check .
```

### Decisions

- **Files are read only through git at the pinned commit:** the file list comes from
  `git ls-tree --name-only <commit> peps/` and each file from
  `git show <commit>:<path>`, so the result does not depend on what is checked out.
- **Clone with `--no-checkout`:** no working tree is needed for this, and it makes it
  impossible to read the working tree by mistake.
- **PEP files are matched with `^peps/pep-(\d{4})\.(rst|txt)$`**, because `peps/` also
  contains other files (`conf.py`, `contents.rst`, image folders, etc.).
- **Header parsing:** the header ends at the first blank line; lines starting with
  whitespace continue the previous field.
- **No cleaning yet:** the CSV keeps the raw values so that every cleaning step can be
  documented and counted later.

### Checks

- 748 PEP files read at the pinned commit, with 18 distinct header fields.
- Raw `Status` values: Final 375, Rejected 131, Withdrawn 74, Draft 56, Active 38,
  Deferred 35, Superseded 25, Accepted 12, Provisional 1, `April Fool!` 1.
- Tested from scratch in an empty directory: the clone is created automatically and the
  counts are identical (about 20 s, mostly the clone).
- Ruff format and lint checks pass.

### Notes for the next steps

- `April Fool!` is a joke PEP: needs an explicit cleaning decision.
- `Author` values contain e-mail addresses: strip them during cleaning (personal data).
- `BDFL-Delegate` and `PEP-Delegate` both exist: likely related to the 2018 governance
  change, to be checked against PEP 13 and the history.

## 2026-11-24 — Cleaning the PEP headers

### What I did

- Inspected the raw headers before writing any rule: `Type` has only three values,
  every `Created` value uses `DD-Mon-YYYY`, 681 PEPs have e-mail addresses in `Author`,
  and `Resolution` is missing for 288 Accepted, Final or Rejected PEPs, so it cannot be
  used as the decision date.
- Wrote `src/pep_analysis/clean.py`, which produces `results/peps_clean.csv`,
  `results/pep_authors.csv` and `results/cleaning_log.csv`, and called it from `main()`.

### Decisions (counts come from `results/cleaning_log.csv`)

| Rule | Records | Why |
| --- | ---: | --- |
| Exclude statuses outside the PEP 1 lifecycle | 1 | PEP 401 has status `April Fool!` (a joke) |
| Parse `Created` as `DD-Mon-YYYY` | 747 | Any other format stops the run instead of being ignored |
| Remove e-mail addresses from `Author` | 1093 | Personal data; never written to any output |
| Drop empty author entries | 12 | Trailing commas in the header |
| Do not split on the comma before `Jr.` | 2 | "Fred L. Drake, Jr." is one person |
| Do not count group names as people | 1 | "The Python core team and community" |
| Merge spelling variants of a name | 1 | Same name with and without an accent |
| Merge `BDFL-Delegate` / `PEP-Delegate` into one column | 82 / 39 | Same role, renamed after the 2018 governance change; the original field is kept |

- **Outcome groups** (from the statuses defined in PEP 1): accepted = Accepted, Final,
  Active, Provisional; rejected = Rejected; withdrawn = Withdrawn; open = Draft,
  Deferred; superseded = Superseded. (Provisional was first grouped as open; moved to
  accepted while building the history, see the next entry.) Rejections (decision-makers) and withdrawals
  (authors) are kept separate, as the assignment requires.
- Name matching ignores accents, case and dots. It cannot detect the same person under
  completely different names, so the number of distinct authors may be slightly too high.

### Checks

- 747 PEPs kept; outcomes at that point: accepted 425, rejected 131, open 92,
  withdrawn 74, superseded 25 (sum 747).
- Spot-checked by hand against `git show <commit>:<path>`:
  - PEP 160: one author "Fred L. Drake, Jr.", not two.
  - PEP 484: three authors in order, delegate Mark Shannon from `BDFL-Delegate`.
  - PEP 394: six authors from a multi-line `Author` header ending in a comma.
- No `@` in `pep_authors.csv`; the only `@` in `peps_clean.csv` is in the title of PEP 403.
- Ruff format and lint checks pass.

### To check later

- Whether `Active` should count as accepted when comparing Standards Track PEPs only
  (it is used almost only by Process and Informational PEPs).

## 2026-11-24 — Status history and decision dates

### What I did

- Wrote `src/pep_analysis/history.py`, which rebuilds the status history of every PEP
  from the Git history up to the pinned commit and adds these columns to
  `results/peps_clean.csv`: `status_changes`, `first_status_date`, `decision_date`,
  `days_to_decision`, `decision_in_bulk_commit`, `added_already_decided`.
- Moved writing the outputs to the end of `main()`, so that the cleaning log also
  contains the history rules.

### Commands

```bash
# every commit that touches a Status line, oldest first, merges diffed against parent 1
git -C data/peps log <commit> --reverse -M -G'^Status:' --diff-merges=first-parent \
    -p --unified=0 --format='%x00%H%x09%cI'
# renames that change the PEP number
git -C data/peps log <commit> -M --diff-merges=first-parent --diff-filter=R --name-status
# commit order
git -C data/peps rev-list --reverse <commit>
```

### Decisions

- **One `git log -p` for the whole repository** instead of one `git log --follow` per PEP:
  about 5 s instead of about 8 minutes, and `--follow` cannot track several files at once.
- **PEPs are identified by the number in the file name**, so the move into `peps/`
  (2023) and the `.txt` -> `.rst` conversion (2017) do not break the history.
- **Only header lines count:** a `+Status:` line is used only if it is within the first
  60 lines of the file; further down it is example text.
- **Committer date (UTC)** is the date of a change: for a merged pull request it is when
  the change landed in the repository.
- **Decision date** = the last time the status entered the PEP's final outcome group
  (for example Draft -> Accepted counts, Accepted -> Final does not).
  `days_to_decision` = decision date - `Created`. Open PEPs have none.
- **Provisional moved from "open" to "accepted"**: PEP 1 defines it as provisionally
  accepted. Before this change PEP 484 was dated 2022 (Provisional -> Final) instead of
  its acceptance in May 2015.
- **Repeated identical statuses are not changes** (e.g. a Status line re-added when a
  file was converted).

### Problems found in the history (counts from `results/cleaning_log.csv`)

| Problem | Records | Handling |
| --- | ---: | --- |
| Old or misspelt statuses (`Incomplete`, `Replaced`, `Finished`, `Approved`, `Postponed`, `Acepted`, `Draught`, `Withdrawal`, `Complete`) | 33 | Mapped to the PEP 1 status (`HISTORICAL_STATUS`) |
| Empty `Status:` value | 1 | Ignored |
| Status changed only in a merge commit (found via PEP 405) | — | `--diff-merges=first-parent` |
| Renumbered proposals (3000->3100, 3142->3120, 500->501, 13->103, 9999->610, 9999->654, 837->840) | 7 | Earlier history moved to the new number |
| Bulk commits changing the status of >= 10 PEPs | 4 | Flagged; 13 decisions dated by them are unreliable |
| PEPs first committed already decided | 47 | No decision date (cannot be measured) |

- Bulk commits found: a mass deferral (2013), "a whole slew of peps that are implemented"
  (2009), "Change the status of a whole lotta PEPs" (2007), "Mark various accepted PEPs
  as Final" (2026).
- Some old PEPs in the history are Latin-1, not UTF-8: undecodable bytes are replaced
  when reading git output instead of crashing.
- Swaps without a rename (PEP 404 and 405 swapped contents in 2011) cannot be detected:
  the status changes before the swap are attributed to the wrong proposal. Known
  limitation; for PEP 405 it does not change the decision date.

### Checks

- The last status in the history equals the header status for all 747 PEPs (0 mismatches),
  and every PEP has at least one Status line (0 missing).
- No negative `days_to_decision`.
- Spot-checked decision dates against the commit messages and the `Resolution` links:
  PEP 484 accepted 2015-05-23 (UTC; commit "accepted by BDFL-Delegate"), PEP 405
  2012-05-25, PEP 572 2018-07-12, PEP 634 2021-02-09.
- Ruff format and lint checks pass.

### Trust

- Least trusted: decision dates of the 13 PEPs dated by bulk commits, and the time for
  `superseded` PEPs, which measures when a replacement appeared, not a decision.

## 2026-11-24 — Finding the process changes

### What I did

- Listed the history of the process documents at the pinned commit and read the diffs of
  the commits that change who decides, who may propose and where discussion happens.
- Cross-checked with the data: which delegate field PEPs use by year, and the venue in
  `Discussions-To` by year of creation.

### Commands

```bash
git -C data/peps log <commit> --format='%h %cs %s' -- peps/pep-0001.rst pep-0001.txt
git -C data/peps log <commit> --format='%h %cs %s' -- peps/pep-0013.rst pep-0013.rst
git -C data/peps show --unified=0 <change-commit> -- pep-0001.txt peps/pep-0001.rst
```

### Process changes found (commits in python/peps)

| Date | Commit | Change |
| --- | --- | --- |
| 2012-05-06 | [73310d4468](https://github.com/python/peps/commit/73310d446896704e8a434fcd704463fd47b0364b) | PEP 1: `BDFL-Delegate` header introduced |
| 2016-06-25 | [30784d4044](https://github.com/python/peps/commit/30784d40447b1879a7ab099454a2d1854e1a8e70) | PEP 1: version control references point to GitHub |
| 2018-10-27 | [f6abb96c8a](https://github.com/python/peps/commit/f6abb96c8a9fdbb4eceefd2c86fe36752d72edc0) | PEP 1: Guido removed from PEP editors, note about future governance |
| 2018-12-26 | [d4a5364baf](https://github.com/python/peps/commit/d4a5364baf4e814c522079262df1535808da113a) | PEP 13 becomes the governance model |
| 2019-02-04 | [9b05b181d0](https://github.com/python/peps/commit/9b05b181d0b8e199e43b2ee81b0fd9ca58185fdd) | PEP 13: results of the first Steering Council election (PEP 8100) |
| 2019-02-20 | [83687f6ee3](https://github.com/python/peps/commit/83687f6ee354a6feac2f1ddc7a0f27fd8bbe65ef) | PEP 1: Steering Council becomes the final authority on PEPs |
| 2019-03-04 | [c58d32c33b](https://github.com/python/peps/commit/c58d32c33bd06eb386d3f33963a1434510528f68) | PEP 1: sponsors introduced |
| 2020-10-26 | [a169cac7d5](https://github.com/python/peps/commit/a169cac7d59498d3b1d8e611756eac973d0bf402) | PEP 1: `BDFL-Delegate` renamed `PEP-Delegate` |
| 2022-02-22 | [b1e81ac1dc](https://github.com/python/peps/commit/b1e81ac1dc83b8d2d1943542010e15f9d57c3b80) | PEP 1: best practice for PEP announcement and discussion |
| 2022-09-20 | [b18ca66cb5](https://github.com/python/peps/commit/b18ca66cb5bcbad28b938752fc650839a1cce63d) | PEP 1: main discussion venue moves from Python-Dev to Discourse |
| 2023-11-29 | [84fc526aaa](https://github.com/python/peps/commit/84fc526aaad90cc3cc4c877b217b0ed9dd53e212) | PEP 1: Typing Council mentioned |

### What the data shows

- **Discussion venue (`Discussions-To`, by year created):** almost always empty until
  2018. Discourse appears from 2019 (15 of 32 PEPs) and dominates from 2022 (22 of 25),
  matching the PEP 1 change of September 2022, which only made official a shift that had
  already started.
- **Delegate field:** `BDFL-Delegate` is used up to 2020 and `PEP-Delegate` from 2021,
  matching the rename of October 2020. The field name shows **when the header was
  written, not who delegated**: a few older PEPs carry `PEP-Delegate` (2009, 2015)
  because they were edited later. The governance change cannot be dated from this field.
- **Who decided is often not recorded:** most accepted or rejected PEPs have no delegate
  field. Before 2018 that means the BDFL decided, after 2019 the Steering Council, but
  this is an inference from PEP 1 and PEP 13, not a recorded value.

### Decision

- **Main split: the Steering Council era** (PEP 1 names the Council as final authority
  on 2019-02-20, after the first election on 2019-02-04). The period between the BDFL
  stepping down and the first Council (mid 2018 to early 2019) is a transition and will
  be reported separately rather than forced into one side.
- **Secondary split: Discourse as the main venue** (2022-09-20), for the participation
  analysis.
- Sponsors (2019-03-04) almost coincide with the Council, so their effect cannot be
  separated from it with this data.

### To check

- The date and announcement of the BDFL stepping down is not in this repository; find the
  primary source (python-committers mailing list) and add it to `links.md`.

## 2026-11-24 — Outcomes and time to decision by period

### What I did

- Found the primary source for the end of the BDFL era: the "Transfer of power" thread on
  python-committers, 2018-07-12 (added to `links.md`).
- Defined three governance periods in `config.py`: BDFL (to 2018-07-12), Transition
  (2018-07-13 to 2019-02-19) and Steering Council (from 2019-02-20, when PEP 1 names the
  Council as final authority).
- Wrote `src/pep_analysis/analysis.py`: outcome counts and rates, time to decision and a
  right-censoring check, overall and by period. It writes one CSV per table and
  `results/summary.md` with every table in Markdown, which is what the report cites.

### Decisions

- **Rates use closed PEPs only** (accepted + rejected + withdrawn) as denominator; open
  PEPs have no answer yet and would make the "no" rate look lower. Superseded PEPs are
  shown apart.
- **Rejected and withdrawn are separate rates**, as required.
- **Period comparisons use Standards Track PEPs** (changes to the language and library);
  Process and Informational PEPs are reported in the type table.
- **A PEP belongs to the period of its decision date**, not its creation date, because
  the question is who was deciding at the time.
- **Medians and quartiles, not means:** a few PEPs took more than ten years.
- **Excluded from time and period tables:** decisions dated by a bulk commit (13) and
  closed PEPs without a measurable decision date (47).
- **Transition starts 2018-07-13, not 07-12:** PEP 572, the BDFL's last decision, was
  committed at 00:54 UTC on 2018-07-12 (commit 8846efd6, 17:54 on 07-11 in the author's
  time zone), hours before the announcement. With day-level periods it would otherwise
  count as a transition decision.
- **Empty periods are shown with 0** instead of being dropped.

### Results (from `results/summary.md`)

- Standards Track, closed: acceptance 65.2 %, rejection 23.7 %, withdrawal 11.0 %.
- By period (Standards Track): BDFL 279 closed, rejection 26.2 %; Steering Council 189
  closed, rejection 17.5 %; Transition **0 decisions**.
- All types in the Transition: 8 decisions, all governance PEPs (PEP 8001 and PEP 8016
  accepted, six other governance models rejected).
- Median days to acceptance (Standards Track): BDFL 99, Steering Council 151.5;
  to rejection: 376 and 234.

### Checks

- Listed every decision between 2018-06-01 and 2019-04-01 and every status-changing
  commit in the Transition: confirms that only governance PEPs were decided then.
- Open PEPs by period of creation: 7.3 % (BDFL) vs 21.3 % (Steering Council). The
  recent period is right-censored, so its rejection rate and times are likely to change
  as open PEPs are closed.
- Ruff format and lint checks pass.

### Least trusted numbers

- Times in the Steering Council period: 21.3 % of its PEPs are still open, and the ones
  that will be decided late are missing from the medians, which biases them downwards.
- `days_to_decision` starts at `Created`, which may be before or after the first public
  discussion, and ends when the status was changed in the repository, not when the
  decision was announced.

## 2026-11-24 — Participation, delegation and charts

### What I did

- Wrote `src/pep_analysis/participation.py`: distinct authors, authors by number of PEPs,
  concentration, new authors per year and per period, and how many Standards Track
  decisions name a delegate.
- Wrote `src/pep_analysis/charts.py` with three charts in `results/`:
  `peps_by_year.png`, `time_to_decision_by_year.png`, `authors_by_year.png`, with the
  process changes marked as vertical lines.
- Moved helpers shared by the analysis modules to `analysis_common.py`.
- Added the Discourse date (2022-09-20) to `config.py` as a chart marker.

### Decisions

- **Authors are matched by `author_key`** (normalised name, see cleaning). A "new author"
  is one whose first PEP was created that year.
- **Concentration is reported two ways:** authors with 10 or more PEPs ("frequent
  authors"), and the share of all authorships held by the top 10 % of authors.
- **Only counts and shares are written, never a ranking with names** (assignment,
  section 8). Delegates are counted, not listed.
- **matplotlib keeps its cache in `results/.matplotlib`** (`MPLCONFIGDIR`), set before
  importing it, so the project writes nothing in the home directory. `results/` is ignored.
- matplotlib uses the `Agg` backend: no display is needed in the review container.

### Results (from `results/summary.md`)

- 370 distinct authors. 54.3 % of them wrote a single PEP; 21 authors (5.7 %) wrote 10 or
  more and co-authored 49.5 % of all PEPs. The top 10 % of authors (37 people) hold
  49.0 % of authorships.
- Mean authors per PEP: 1.39 (BDFL), 1.80 (Steering Council).
- PEPs with a frequent author: 53.1 % (BDFL) vs 41.4 % (Steering Council).
- Standards Track decisions naming a delegate: 12.5 % (BDFL, 14 people) vs
  31.2 % (Steering Council, 18 people).
- More distinct authors per year since 2019 (40-62 vs mostly 10-37 before).

### Checks

- Looked at all three charts: period lines are at the right dates; the 2026 bar is mostly
  open PEPs, as expected for the current year.
- Two PEPs have `Created` before 2000 (PEP 248, 1996, and PEP 249, 1999: the database API
  specifications, written before the PEP process and added as PEPs later). Kept as they
  are; they explain the bars before 2000.
- Ruff format and lint checks pass.

### Caveats

- The yearly time-to-decision chart is noisy: some years have only a handful of
  decisions. The period table is the one to cite; the chart only shows the trend.
- Delegation may be under-recorded before 2012, when the `BDFL-Delegate` header did not
  exist yet.

## 2026-11-24 — Faster, isolated git access and a fresh-run test

### What I did

- Read all PEP files in one `git cat-file --batch` call instead of one `git show` per
  file. The whole pipeline went from about 69 s to about 7 s on `/mnt/c`.
- Run every read-only git command with `GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_NOSYSTEM=1` and `LC_ALL=C`, so that settings in the reviewer's own git
  configuration (for example `log.showSignature`) cannot change the output. Network
  commands (`clone`, `fetch`) keep the user's configuration, which may contain proxy
  settings.
- Added matplotlib 3.11.2 as a dependency (`uv add matplotlib`), pinned in `uv.lock`.

### Checks

```bash
sha256sum results/*.csv results/summary.md > /tmp/before.sha   # before the change
uv run pep-analysis
sha256sum -c /tmp/before.sha                                    # after: all OK
```

- Every CSV and `summary.md` is byte-for-byte identical before and after the change.
- Fresh run: copied only the files tracked by git into an empty directory (no `data/`,
  `results/` or `.venv/`) and ran `uv run --locked pep-analysis`. It cloned python/peps,
  created the environment from `uv.lock` and produced identical results in about 21 s.
  Everything it created (`.venv/`, `data/`, `results/`, `results/.matplotlib/`) is inside
  the directory and ignored by git.

## 2026-11-26 — Writing the report

### What I did

- Read PEP 1 and PEP 13 at the pinned commit (`git show <commit>:peps/pep-0001.rst`) and
  two Developer's Guide pages, and wrote Part 1. Every claim links to the exact lines at
  the pinned commit (`?plain=1#Lx-Ly`); I checked that each line range contains the text
  it is cited for.
- Added three tables to the code so that every number in the report comes from it:
  discussion venue (`Discussions-To`) by year and period, and the share of Standards
  Track decisions with a `Resolution` link and a `Sponsor`, by period. New columns in
  `peps_clean.csv`: `has_sponsor`, `venue`.
- Wrote Part 2 from `results/summary.md` and the earlier worklog entries.
- Chose PEP 572 for Part 3 and followed it through the PEP's own history, the mailing
  list archives, the CPython tracker and pull request, and the 3.8 release notes.
  Opened every link to check that it shows what it is cited for.
- Wrote Part 4, pointing every claim back to a section of Parts 1-3.
- Added all 48 new report links to `docs/links.md`.

### Decisions

- **PEP 572** for Part 3: accepted, released (3.8) and the case that ended the BDFL
  model, so it connects Parts 1, 2 and 4.
- The first public proposal is the python-ideas post of 2018-02-27 (EST), which is
  2018-02-28 in UTC and matches the `Created` header.
- Line-level permalinks instead of section anchors: GitHub anchors for reStructuredText
  are not stable, line numbers at a fixed commit are.

### Findings worth noting

- PEP 1 says Superseded is meant for Informational PEPs, but 16 of the 25 superseded
  PEPs are Standards Track.
- `Resolution` (required by PEP 1 for Standards Track) is present in 28.0 % of
  BDFL-period decisions and 78.3 % of Steering Council decisions.
- PEP 572: Guido became co-author on 2018-05-22 and accepted it on 2018-07-11; the PEP
  was marked Final only on 2022-11-06, three years after Python 3.8.0.

### Checks

- Script: every number in Parts 2 and 4 appears in `results/summary.md` (the only
  exceptions are section numbers, PEP numbers and the "75 %" percentile heading).
- Script: every link in `docs/report.md` appears in `docs/links.md`.
- Ruff format and lint checks pass.
