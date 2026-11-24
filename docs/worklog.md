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
