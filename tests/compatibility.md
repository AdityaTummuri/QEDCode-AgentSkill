# Compatibility

Only environments that were actually tested are listed as working.

## QEDCode versions

| QEDCode | Commit | Status | Notes |
| --- | --- | --- | --- |
| 0.1.0 | `8824706` (release) | Verified (partial) | `check`, `verify`, exit codes, `--json` output and all four MCP tools were run. `solve` was run up to the "no model installed" error |
| 0.1.0 | `005c8d2` (fixes) | Verified (partial) | Stricter `check` (appended tests, weakened tests, "tests could not run" summary) and `notes` in MCP `check`; 1,210 engine tests pass. It sits on top of `e1f95ec` (which adds `qed benchy` and grades comment-only changes C). Live CLI run: appended test → A + VERIFIED, weakened test → C "tests weakened in tests/test_pages.py". `solve → verify → apply` was run end to end with the scripted stand-in model. A **real-model** solve is not yet tested: run `tests/run_solve_smoke.py` on a computer with `qed setup` done |

Minimum supported version: **0.1.0**.

## Agents

| Agent / platform | Tested version | Status | Notes |
| --- | --- | --- | --- |
| Claude Code | 2.1.329 (Sonnet, headless `claude -p`) | **Works** (2026-11-21; with QEDCode, and fallback without it) | Project-level skill in `.claude/skills/qedcode`. The skill was picked up from a plain bug report that didn't mention QEDCode. The agent added a regression test, reached grade A with `qed check`, ran `qed verify`, and reported honestly, including what it couldn't run. Found and fixed one gap: the agent appended to an existing test file (grade B) before moving the test to a new file |
| Claude Code + QEDCode MCP | 2.1.329 (Sonnet) | **Works** (2026-11-21) | `qed mcp` (build `005c8d2`) connected through `--mcp-config`, with the CLI not allowed. The agent used `mcp__qedcode__check` with `project_dir` and got grade A, then ran `mcp__qedcode__verify` (verified) and its own pytest run |
| Agensi | — | Not tested | Check the current ZIP and package requirements before submitting |
| Other agents (OpenCode, Cline, Cursor) | — | Not tested | QEDCode's MCP server supports them; this skill's instructions haven't been tested there |

## Test log

### 2026-11-21 — Claude Code + QEDCode MCP, bug-zoo `010_cart_quantity`

- Setup: the skill was installed for the project; `qed mcp` came from the fix build, given through
  `--mcp-config --strict-mcp-config`; only MCP tools were allowed (no `qed` CLI).
- Prompt: "Cart.total() ignores the quantity... use the qedcode MCP tools to prove the fix."
- Result: the skill was invoked. The agent fixed `total()` and wrote tests in a new file, then
  called `mcp__qedcode__check` with `project_dir`: grade A. `mcp__qedcode__verify` verified, and
  its own `.venv/bin/python -m pytest` run passed 5. The report included the "not proven" items.
  13 turns.

### 2026-11-21 — `run_solve_smoke.py` with the scripted stand-in model

- `solve` came from QEDCode's FakeModel scripts through a test shim; every other command was the
  real `qed`. Projects 001 and 002: `done`, grade A, `qed verify` VERIFIED, `qed apply` OK, and
  the hidden bug-zoo tests passed 3/3 each. This proves the script and the `solve --json` fields,
  not model quality.
- Without a model, every row reports `exit 2` with the "engine is not installed" message.

### 2026-11-21 — Claude Code, bug-zoo `002_discount_threshold`

- Setup: a fresh copy of the project with `.venv` + pytest, the skill symlinked into
  `.claude/skills/`, and `qed` 0.1.0 on PATH. No model was installed.
- Prompt: "Customers who spend exactly 100 are not getting their 10% discount... make sure the fix
  is actually proven before you tell me it's done."
- Result: the `qedcode` skill was invoked on turn 2. Fix `>` → `>=`. New test file. `qed check`
  grade A. `qed verify` VERIFIED. 15 turns.
- Issue: the first attempt appended tests to `tests/test_pricing.py` and got grade B
  ("protected files changed"). The skill now says to use a new test file.

### 2026-11-21 — Claude Code, QEDCode not installed, bug-zoo `007_sort_order`

- Prompt: "Use QEDCode to check and prove a fix: the leaderboard is sorted the wrong way round..."
- Result: the skill was invoked, and the agent found `qed` missing. It didn't install anything. It
  fixed the bug, added tests in a new file, and reported "not proven", saying QEDCode wasn't
  installed and offering the install route. 16 turns.
- Issue: it tried system `python3 -m pytest` rather than the project's `.venv`. SKILL.md now names
  the project interpreter in the fallback step.

### 2026-11-21 — QEDCode CLI/MCP audit, bug-zoo `001_paginate_off_by_one`

| Scenario | Interface | Observed |
| --- | --- | --- |
| Correct fix + new regression test | CLI `check --json` | `graded`, A, exit 0; `qed verify` → VERIFIED, exit 0 |
| Wrong fix | CLI | `rejected` at fbpa, exit 1 |
| Syntax error | CLI | `Rejected at parse` |
| Existing test weakened | CLI | grade B, "protected files changed", exit 0 |
| No changes | CLI | "identical to HEAD", exit 2 |
| Correct fix, no project `.venv` | MCP `check` | grade C, "no tests ran". The interpreter fell back to `python3` without pytest; the MCP result has no `notes` |
| Same, with a project `.venv` + pytest | MCP `check` | grade A |
| `solve` without a model | CLI `--json` | plain-text error on stderr, exit 2 |
| Unknown job id | MCP `status` | `status: error` |
