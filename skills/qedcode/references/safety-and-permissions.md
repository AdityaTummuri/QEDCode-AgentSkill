# Safety and permissions

## What QEDCode guarantees (per its README and source, 0.1.0)

- Candidates are built and tested in git worktrees under `.qed/worktrees/`. Only `qed apply` and
  `qed undo` write to the user's working tree, and both refuse if a file they would touch changed
  since the snapshot.
- `qed check` never modifies files. It snapshots the tree into a private ref
  (`refs/qed/snapshots/<task id>`) without touching the index or running git hooks.
- The model never runs commands. Only fixed commands built by QEDCode run: git, the project's
  Python with pytest, ruff, Node with the project's test runner, and the llama.cpp server.
- In `solve`, a candidate that edits, deletes, skips or weakens existing tests is rejected. Risky
  code (subprocess, network, `eval`, ...) needs approval and then reaches grade B at most.
- `qed verify` treats a receipt as data: it runs only the project's test command on files inside
  the project.
- Local mode sends no code anywhere. Mix mode (a helper model) and cloud mode send parts of the
  code to a provider.

## What it does **not** guarantee

- **No sandbox by default.** Project tests run on the user's machine, with network access and
  without a container, unless `qed sandbox setup` was done. The project's own test code is
  therefore as trusted or untrusted as running `pytest` yourself.
- `qed check` does **not** reject edits to existing tests. It flags them (`protected files
  changed`) and caps the grade at B. From commit `005c8d2`, a detected weakening (added skip,
  removed asserts, an assert that can never fail) caps it at C with `tests weakened in <file>`.
  Subtler weakening, such as an edited expected value, still shows only as "protected files
  changed", so read every test diff.
- A grade doesn't prove that the requirement was understood correctly. It proves what the tests
  check.

## What the agent must ask the user before doing

| Action | Why |
| --- | --- |
| Installing or upgrading QEDCode, `qed setup`, `qed models download/use/remove` | Software install; multi-GB downloads |
| `qed connect`, `claude mcp add ...` | Edits agent configuration |
| `qed apply`, `qed solve --apply`, MCP `solve(apply=true)` | Writes to the user's files |
| `--yes` on `apply` for grade C/D | Skips QEDCode's own low-grade confirmation |
| `--allow-risky` | Approves subprocess, network or `eval` code on the user's behalf |
| Mix or cloud mode, a helper model | Sends code off the machine |
| `qed sandbox setup/off`, `qed memory clear/forget`, `qed uninstall` | Changes or deletes the user's setup |
| Installing pytest or Node packages, `uv sync` | Changes the project environment |

Safe to run without asking: `qed --version`, `qed --help`, `qed doctor`, `qed check`,
`qed verify`, `qed models list`, `qed models recommend`, `qed connect --list`, MCP
`check`/`verify`/`status`, and MCP `solve` with `apply=false`. These run the project's tests, the
same as running the test suite yourself.

## Preserving user changes

- `qed check` grades every uncommitted change, the user's included. Before you start, note what
  was already modified, and keep it separate in your report.
- Never `git stash`, reset, or commit the user's work to make a check "clean" unless they ask.
- Don't delete `.qed/lock` or `.qed/worktrees/` while a job might be running.
