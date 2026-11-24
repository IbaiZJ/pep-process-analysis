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
git -C data/peps rev-parse HEAD                      # -> af21ad1e51fe60aaa3fa2f48392ab4cecfd5fd58
git -C data/peps rev-parse --is-shallow-repository   # -> false (full history)
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

- `README.md` was first created from PowerShell (`echo ... > README.md`), which saved it
  as UTF-16 with CRLF line endings. Rewrote it as UTF-8 and added `.gitattributes` and
  `.editorconfig` so that it does not happen again.
- Some files were saved with CRLF in the working tree; Git stores them as LF in the
  index thanks to `.gitattributes`, and they were converted to LF on disk too.

### Checks

- `ls data/peps/peps/pep-*.rst | wc -l` -> 748 proposal files at the pinned commit.
- `git status` does not list `data/` or the assignment document.
- `git ls-files --eol` shows `i/lf` (LF in the index) for every committed text file.
