# Changelog

All notable changes to the QEDCode Agent Skill. The format follows
[Keep a Changelog](https://keepachangelog.com/). Each entry names the QEDCode version it was
verified against.

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
