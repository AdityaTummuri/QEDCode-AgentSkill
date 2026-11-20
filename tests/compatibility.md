# Compatibility

Only environments that were actually tested are listed as working.

## QEDCode versions

| QEDCode | Commit | Status | Notes |
| --- | --- | --- | --- |
| 0.1.0 | `8824706` (release) | Verified (partial) | `check`, `verify`, exit codes, `--json` output and all four MCP tools were run. `solve` was run up to the "no model installed" error |
| 0.1.0 | `005c8d2` (fixes) | Verified (partial) | Stricter `check` (appended tests, weakened tests, "tests could not run" summary) and `notes` in MCP `check`; 1,210 engine tests pass. It sits on top of `e1f95ec` (which adds `qed benchy` and grades comment-only changes C). Live CLI run: appended test → A + VERIFIED, weakened test → C "tests weakened in tests/test_pages.py". `solve → verify → apply` was run end to end with the scripted stand-in model. A **real-model** solve is not yet tested: run `tests/run_solve_smoke.py` on a computer with `qed setup` done |
| 0.1.0 | `7edcca1` (verify fix) | Verified | `qed verify` re-runs tests with the project's detected Python, like `qed check`. Before it, with QEDCode installed as a `uv tool`, a fresh grade-A receipt came back NOT VERIFIED ("pytest is not installed in .../uv/tools/qedcode/bin/python"). Found by `check_contract.py` in CI |
| 0.1.0 | `50a45de` (IDE connect) | Verified (partial) | Adds `qed connect antigravity` and `qed connect vscode`; no change to `check`, `solve`, `verify` or the MCP tools. `validate_skill.py` and `check_contract.py` pass (correct fix → A + VERIFIED, wrong fix → rejected, no changes → exit 2, weakened test → C) |

Minimum supported version: **0.1.0**. CI (`sync-with-qedcode`) re-runs `validate_skill.py` and
`check_contract.py` against QEDCode's main branch on every push and every Monday.

## Agents

| Agent / platform | Tested version | Status | Notes |
| --- | --- | --- | --- |
| Claude Code | 2.1.329 (Sonnet, headless `claude -p`) | **Works** (2026-11-21; with QEDCode, and fallback without it) | Project-level skill in `.claude/skills/qedcode`. The skill was picked up from a plain bug report that didn't mention QEDCode. The agent added a regression test, reached grade A with `qed check`, ran `qed verify`, and reported honestly, including what it couldn't run. Found and fixed one gap: the agent appended to an existing test file (grade B) before moving the test to a new file |
| Claude Code + QEDCode MCP | 2.1.329 (Sonnet) | **Works** (2026-11-21) | `qed mcp` (build `005c8d2`) connected through `--mcp-config`, with the CLI not allowed. The agent used `mcp__qedcode__check` with `project_dir` and got grade A, then ran `mcp__qedcode__verify` (verified) and its own pytest run |
| Google Antigravity (`agy` CLI; the IDE shares its MCP file) | 1.5.13 (default model) | **Works** (2026-11-21) | 4 of 4 bug-zoo projects through `tests/run_ide_smoke.py`, with prompts that don't name QEDCode, plus 2 of 2 with QEDCode reachable only over MCP: skill picked up from the workspace, fix + regression test in a new file, grade A, `qed verify` VERIFIED, hidden tests pass. `qed connect antigravity` ran the real `agy mcp add`. Headless `agy` needs an allow-list for commands and MCP tools (the script passes one per run). Skill folders: `~/.gemini/config/skills/`, `<workspace>/.agents/skills/`. Tested with the `agy` CLI |
| VS Code (Copilot agent mode) | — | Not tested | No VS Code on the test machine. `qed connect vscode` (`code --add-mcp`) is unit-tested only. Skill folders from the VS Code docs: `.github/skills/`, `~/.copilot/skills/` (also `.claude/skills/`, `.agents/skills/`) |
| Agensi | — | Not tested | Check the current ZIP and package requirements before submitting |
| Other agents (OpenCode, Cline, Cursor) | — | Not tested | QEDCode's MCP server supports them; this skill's instructions haven't been tested there |

## Test log

### 2026-11-21 — Antigravity agent runs (`agy` 1.5.13), QEDCode `7edcca1` as a `uv tool`

`python3 tests/run_ide_smoke.py --zoo ../QEDCode/bugzoo --only 001 002 007 010`, default model,
prompt = task.txt + "make sure the fix is actually proven" (QEDCode not named):

| Project | Seconds | Receipts | Grade | qed verify | Hidden tests |
| --- | --- | --- | --- | --- | --- |
| 001_paginate_off_by_one | 137.3 | 1 | A | VERIFIED | pass 3/3 |
| 002_discount_threshold | 142.3 | 1 | A | VERIFIED | pass 3/3 |
| 007_sort_order | 143.4 | 1 | A | VERIFIED | pass 2/2 |
| 010_cart_quantity | 52.7 | 1 | A | VERIFIED | pass 2/2 |

- MCP only (`--mcp-only`: the `qed` command not allowed, so receipts can only come through MCP;
  the prompt asks for the qedcode MCP tools): 002 → A, VERIFIED, hidden 3/3 (62 s); 010 → A,
  VERIFIED, hidden 2/2 (85 s). The agent's report names the `qedcode:verify` tool.
- First attempt: `--mode auto` isn't available on every account, and headless `agy` silently
  denies any tool needing a "command" permission. The agent fixed 002 without QEDCode, so no
  proof. The script now passes a one-run allow-list (`--settings`): QEDCode's MCP tools, `qed`,
  `.venv/bin/python`, read-only git and file commands. The saved agy settings are untouched.
- `agy -p` prints only the final answer, so the transcript doesn't show whether the agent used
  MCP or the CLI; both were allowed. Its report gave grade, summary, receipt and the verify result.

### 2026-11-21 — Antigravity integration (`agy` 1.5.10), QEDCode `50a45de`

- `HOME=<tmp> qed connect antigravity --yes`: the preview named `agy mcp add qedcode -- <abs qed>
  mcp`; `~/.gemini/config/mcp_config.json` got the entry; `agy mcp list` → `qedcode stdio enabled`.
  The user's real Antigravity settings were not touched.
- `tests/run_ide_smoke.py --only 002` with a stand-in `agy` that applies the zoo fix and runs
  `qed check`: the workspace `.agents/` folder stayed out of the graded diff; grade A, VERIFIED,
  hidden tests 3/3. This proves the harness, not the agent.
- (The real agent runs followed once `agy` was signed in: see the entry above.)

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
