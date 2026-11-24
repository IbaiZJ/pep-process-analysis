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
