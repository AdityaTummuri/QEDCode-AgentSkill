# Changelog

All notable changes to the QEDCode Agent Skill. The format follows
[Keep a Changelog](https://keepachangelog.com/). Each entry names the QEDCode version it was
verified against.

## [0.3.1] - 2026-11-22

Verified against QEDCode 0.1.0, commit `5953682` (`check` gives a big repository's full suite at
most 120 s / 300 s and remembers a too-slow suite).

### Changed
- Iterate with `qed check --speed fast` (MCP `speed="fast"`), then run one final check at the
  default speed for the grade you report. Found by Benchy's agent mode: Antigravity with QEDCode
  hit its 15-minute limit on a sympy task while `qed check` waited for the full suite. Measured on
  that task: 306 s per check before `5953682`, 126 s at normal after it, 6 s at fast (same grade B).
- The command reference explains what each `check` speed runs and why `fast` caps the grade at B.

## [0.3.0] - 2026-11-21

Verified against QEDCode 0.1.0, commits `50a45de` (adds `qed connect antigravity` and
`qed connect vscode`) and `7edcca1` (`qed verify` uses the project's detected Python).

### Tested
- Antigravity (`agy` 1.5.13): 4 of 4 bug-zoo projects reached grade A, VERIFIED, with hidden tests
  passing, through `tests/run_ide_smoke.py` with prompts that don't name QEDCode; 2 of 2 again
  with `--mcp-only` (the `qed` command not allowed).

### Added
- Google Antigravity and VS Code: skill install folders, `qed connect antigravity` / `vscode`, and
  a cloud-model setup for IDE users without a GPU (README, installation, troubleshooting).
- `tests/check_contract.py`: runs the real `qed check` and `qed verify` on a bug zoo project and
  fails if a grade, exit code or JSON field the skill documents has changed. No model needed.
- `tests/run_ide_smoke.py`: an agent test inside Antigravity (`agy -p`), with the skill and MCP
  server set up per workspace and a one-run permission allow-list, then `qed verify` and the
  hidden tests on the agent's result.
- Troubleshooting: NOT VERIFIED from a QEDCode `uv tool` install before `7edcca1`.
- CI workflow `sync-with-qedcode`: validation, contract test and packaging against QEDCode's
  main branch on every push, pull request and every Monday.

### Changed
- SKILL.md finds QEDCode's MCP tools by server name, not only by Claude Code's `mcp__qedcode__`
  prefix, and prefers them inside an IDE where `qed` may not be on the PATH.
- README: weakened tests are grade C on current QEDCode (B only on the release commit), and a
  missing pytest reads "tests could not run".

## [0.2.0] - 2026-11-21

Verified against QEDCode 0.1.0, commits `8824706` (release) and `005c8d2` (engine fixes).

### Added
- `tests/run_solve_smoke.py`: a real-model `qed solve` test over QEDCode's bug zoo. It checks each
  result with `qed verify` and with the zoo's hidden tests, and prints a Markdown report.
- Compatibility: QEDCode MCP inside a Claude Code session is tested and works.

### Changed
- The skill covers both engine builds: on `005c8d2`, appended regression tests can earn A,
  weakened tests are grade C with "tests weakened in ...", a missing test runner reads
  "tests could not run: ...", and MCP `check` returns `notes`. The release commit's behaviour
  is still described where it differs.
- `solve --json` fields are now confirmed from a real run (scripted model), not only from source.

## [0.1.0] - 2026-11-21

Verified against QEDCode 0.1.0 (commit `8824706`).

### Added
- `skills/qedcode/SKILL.md`: when to use QEDCode, availability checks, the check/solve workflow,
  red flags found in testing, and hard rules.
- References: commands and interfaces (CLI flags, JSON fields, exit codes, MCP tools), installation,
  workflow and report template, verification, safety and permissions, troubleshooting.
- Examples: a `qed check` bug fix with real output and outcome table, and a `qed solve` regression
  fix over MCP.
- `tests/validate_skill.py`, which checks every `qed` command and flag against the installed
  QEDCode. Also a compatibility log and a release checklist.
- `scripts/package.sh` (ZIP build) and a Claude Code plugin marketplace manifest.

### Tested
- Claude Code 2.1.329: the skill triggered from a plain bug report, and the agent reached grade A
  with `qed check` and verified the receipt.
- Not yet tested: a full `qed solve` with a real model, the MCP tools inside a Claude Code session,
  and agents other than Claude Code.
