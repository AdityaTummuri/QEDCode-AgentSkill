# Commands and interfaces

Verified against QEDCode 0.1.0 (commits `8824706` and `005c8d2`) by reading `src/qedcode/cli.py`,
`src/qedcode/mcp_server.py` and `src/qedcode/engine/api.py`, and by running `check`, `verify`,
`apply` and the MCP server on real projects. `solve --json` was run end to end with QEDCode's
scripted stand-in model, so its fields are real, but answer quality from a real model is not yet
measured. On any other version, `qed --help` and `qed <command> --help` win.

All commands act on the git repository containing the current directory. Run them from the
project root.

## CLI

### `qed check` — grade uncommitted changes (no model)

```
qed check [--speed fast|normal|sure] [--base <ref>] [--json] [--allow-risky]
```

- Compares the working tree (tracked **and** untracked, non-ignored files) with `--base`
  (default `HEAD`). Runs parse, scope, risk, lint, fail-before/pass-after, targeted and full tests.
- `--json`: progress goes to stderr and one JSON object to stdout:

  | Field | Meaning |
  | --- | --- |
  | `status` | `graded`, `rejected`, `no_changes`, `cancelled`, `busy`, `error` |
  | `grade` | `A`, `B`, `C`, `D`, or `null` when rejected |
  | `summary` | one line, e.g. `Grade A · repro test failed before, passes now · 8/8 tests pass · lint clean · no protected files changed` |
  | `failing_tests` | test ids such as `tests.test_regression::test_full_pages_have_the_page_size` |
  | `receipt_path` | absolute path to `.qed/receipts/<task id>.json` |
  | `task_id`, `base`, `message`, `notes` | `notes` names the Python interpreter that was used, and why tests could not run |

- Exit codes: **0** graded (any grade), **1** rejected or cancelled, **2** no changes, busy or error.
- Speed: `fast` skips the full suite (seconds, but the grade is at most B, and the receipt says
  "Full suite not run (fast speed)"). `normal` (default) and `sure` also run the full suite before
  and after the change, given at most 120 s / 300 s. A suite that doesn't finish in time is marked
  too slow, the related test files run instead (60 s each; slower files are left out and named in
  the receipt), and the best grade is B. From `5953682` on the project remembers a too-slow suite
  (`.qed/full_suite_too_slow.json`), so later checks skip the wait; before it, `check` waited the
  project's whole test timeout (300 s by default). Use `fast` while iterating and the default for
  the final grade.
- `--allow-risky` lets code that uses subprocess, network, `eval` and similar pass the risk stage.
  Use it only when the user approved that code.

### `qed solve` — generate a verified change (needs a model)

```
qed solve "<task>" [--speed fast|normal|sure] [--apply] [--json] [--allow-risky]
```

- Speed: `fast` = 1 try, `normal` = 3, `sure` = 6. QEDCode stops early once a try is proven. With
  no `--speed`, the saved default applies.
- It never changes the user's files unless `--apply` is given **and** the grade is A or B.
- `--json` prints the full result: `status` (`done`, `no_fix`, `needs_input`, `cancelled`,
  `error`), `task.id`, `best.grade`, `best.diff`, `best.checks`, `candidates`, `receipt_path`,
  `explanation`, `question`, `message`.
- If no model is ready, it prints a plain-text message on **stderr** (not JSON) and exits 2.
  Observed: `The llama.cpp engine (b12549) is not installed. Run qed setup ...`.
- Exit codes: **0** done, **1** no_fix / needs_input / cancelled, **2** error (including no model),
  **3** internal crash (details in `~/.qedcode/logs/qedcode.log`).
- Non-interactive runs never answer the engine's questions. A `needs_input` result carries a
  `question` to relay to the user.

### `qed verify <receipt.json>`

- Checks the patch checksum and base commit, then re-runs the recorded tests on the original and
  the patched code in fresh copies.
- Prints `VERIFIED` plus the summary line (exit 0), or `NOT VERIFIED` plus a list of mismatches
  (exit 1).
- It only runs the project's own test command on test files inside the project. A receipt that
  asks for anything else is refused as "not safe to run here".
- A receipt with no test commands (grade C) "verifies" only the patch. The note says so; don't call
  that a proof.

### `qed apply [task id] [--yes]` / `qed undo`

- `apply` writes a finished result into the user's files. It defaults to the last result. Grade C
  or D asks for confirmation; `--yes` skips that question, so use it only on an explicit
  instruction from the user.
- Both commands refuse (exit 1) if a file they would touch changed since the snapshot.
  Exit 2 = error. `undo` reverts the last apply.
- The task id is the receipt file name without `.json`, e.g. `t-20261121-010331-d204`.

### Diagnostics and setup (ask before running anything that downloads or reconfigures)

| Command | Effect | Safe to run unasked? |
| --- | --- | --- |
| `qed --version`, `qed --help` | print info | yes |
| `qed doctor` | checks git, Python/Node, pytest, ruff, GPU, engine, model, disk; prints fixes | yes (read-only) |
| `qed models list` / `qed models recommend` | show the model catalog / the best fit | yes |
| `qed connect --list` | show which agents are connected | yes |
| `qed setup` | interactive wizard; may download an engine and a model | **no** |
| `qed models download <id>` / `use` / `remove` | changes models | **no** |
| `qed connect [agent]` | edits agent MCP config | **no** |
| `qed sandbox setup` / `off` | builds a Docker test box / turns it off | **no** |
| `qed memory forget <#>` / `clear`, `qed uninstall` | deletes data | **no** |
| `qed benchy status` | shows whether the optional QEDCode Benchy benchmark is installed (commit `e1f95ec` and later) | yes |
| `qed benchy install` / `run` / `share` | installs Benchy into QEDCode's environment / runs a benchmark / shares results | **no** |
| `qed` (no args) | opens the interactive terminal UI | not useful to an agent |

## MCP server (`qed mcp`, stdio)

Register it with `qed connect` (agents: `claude`, `opencode`, `cline`, `cursor`, and on newer
builds `antigravity` and `vscode`) or `claude mcp add qedcode -- qed mcp`. In Claude Code the tools
appear as `mcp__qedcode__<tool>`. Antigravity and VS Code list them under the `qedcode` server. All four were listed and called in testing (`solve` only up to the
point where a model is needed), and a Claude Code session completed a fix using `check` and
`verify` over MCP.

| Tool | Arguments | Returns |
| --- | --- | --- |
| `solve` | `task`, `speed="normal"`, `apply=false`, `wait_seconds=600`, `project_dir=""` | `status` (`done`, `running`, `no_fix`, `needs_input`, `busy`, `error`), `job_id`, `grade`, `summary`, `explanation`, `diff`, `receipt_path`, `question`, `message` |
| `check` | `speed="normal"`, `base="HEAD"`, `project_dir=""` | `status`, `job_id`, `grade`, `summary`, `failing_tests`, `receipt_path`, `message`, and `notes` (from `005c8d2`; absent on `8824706`) |
| `verify` | `receipt_path` | `verified`, `mismatches`, `notes` |
| `status` | `job_id` | `running` with `progress` lines and `seconds`, or the final result |

MCP-specific behaviour:

- **Always pass `project_dir`** (absolute repository root). Otherwise the server uses its own
  working directory, which may not be the user's project.
- `solve` with `apply=true` applies A/B results straight into the user's files. Leave it `false`;
  after review, apply with the CLI: `qed apply <task id>`. There is no MCP `apply` or `undo` tool.
- One job per project. A second call returns `status: "busy"` with the running `job_id`.
- MCP runs never answer questions, never approve risky code, and use the helper model only if the
  user's config pre-approves it.
- The MCP server does not inherit a virtualenv from your shell. If the project's tests depend on
  one, make sure it lives at `<project>/.venv` or `<project>/venv`. Otherwise `check` may report
  "no tests ran" (see [troubleshooting.md](troubleshooting.md)).
- If a tool call times out in Claude Code, the user can raise `MCP_TOOL_TIMEOUT`. Or pass a small
  `wait_seconds` and poll `status`.

## Files QEDCode writes

| Path | Contents |
| --- | --- |
| `<project>/.qed/receipts/<task id>.json` | proof receipts |
| `<project>/.qed/runs/`, `.qed/worktrees/`, `.qed/tmp/` | logs and throw-away copies |
| `<project>/.qed/project.toml` | confirmed project settings (`python`, `test_command`, `test_timeout_seconds`, ...), written once the user confirms detection in the `qed` terminal UI |
| `~/.qedcode/` (or `$QEDCODE_HOME`) | global `config.toml`, engines, models, logs |

`.qed/` is added to `.git/info/exclude`, so it never shows up in `git status` or in commits.
