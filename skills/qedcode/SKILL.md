---
name: qedcode
description: >-
  Use QEDCode (the `qed` CLI or the `qedcode` MCP server) to grade code changes with deterministic
  checks and proof receipts, and, when a local or cloud model is configured, to generate verified
  bug fixes. Use it when a Python or JavaScript/TypeScript git project with tests has a
  reproducible bug, a failing test, a regression, or a small feature to build; when you have just
  written a fix and want it graded (A proven to D unchecked) before reporting done; when the user
  mentions QEDCode, `qed`, a grade or a `.qed/receipts/` file; or when a receipt needs re-checking.
  Skip it for documentation-only edits, projects without git, and languages other than Python and
  JS/TS.
---

# QEDCode

[QEDCode](https://github.com/AdityaTummuri/QEDCode) is a separate, local-first engine by Aditya
Tummuri. It tests every change in a throw-away git worktree, grades it **A** (proven) / **B**
(tested) / **C** (checked) / **D** (not checked) and writes a proof receipt that `qed verify`
re-runs. This skill only teaches you to use it. It contains no copy of the engine.

Verified against QEDCode **0.1.0**: the release commit `8824706`, the fix commit `005c8d2`
(which makes `check` stricter about weakened tests and adds `notes` to MCP `check`), and
`50a45de` (which adds `qed connect antigravity` and `vscode`), and `7edcca1` (which makes
`qed verify` use the project's Python). All report 0.1.0. The advice
below is correct on all of them. Where they differ, it says so. If
`qed --version` reports a newer version, read `qed --help` and trust it over this file.

## Two jobs, two requirements

| Job | Command | Needs a model? | Changes the user's files? |
| --- | --- | --- | --- |
| Grade changes already in the working tree (yours or the user's) | `qed check` | **No** | No |
| Generate a fix: several tries, one best verified result | `qed solve "<task>"` | **Yes** (`qed setup` done) | No, until `qed apply` |
| Re-run a proof receipt | `qed verify <receipt>` | No | No |
| Apply a finished result / take it back out | `qed apply [task id]` / `qed undo` | No | **Yes** |

`qed check` is the dependable default: it works as soon as `qed` is installed. Use it to grade a fix
you just wrote before you tell the user it is done.

## Workflow

1. **Is it a fit?** A git repository with at least one commit, Python (pytest) or JS/TS
   (`node --test`, Vitest, Jest), and preferably tests. Without tests the best possible grade is C.
   Not a fit: docs-only edits, large refactors, exploratory work, other languages.
2. **Is it available?** Run `command -v qed && qed --version`, and check for tools from an MCP
   server named `qedcode`: `solve`, `check`, `verify`, `status` (in Claude Code they're
   `mcp__qedcode__solve` and so on; Antigravity and VS Code list them under the `qedcode`
   server). Inside an IDE the MCP tools are often there even when `qed` isn't on the terminal's
   PATH, so use them. If neither is present, say so,
   point to [references/installation.md](references/installation.md), and carry on with your
   normal workflow. Still add a regression test and run the suite with the project's own
   interpreter (`.venv/bin/python -m pytest` when a `.venv` exists). **Never** run an install,
   `qed setup`, `qed models download`, `qed connect` or `qed sandbox setup` without the user's
   explicit OK: they download gigabytes or edit agent config.
3. **Inspect the project.** Run `git status`. `qed check` grades **all** uncommitted work against
   `HEAD`, including untracked files and changes the user made before you started. Say so if the
   user has unrelated work in progress.
4. **Run QEDCode.** See [references/commands-and-interfaces.md](references/commands-and-interfaces.md)
   for exact flags, JSON fields and exit codes.
   - Grade: `qed check --json` (progress goes to stderr, one JSON object to stdout).
   - Generate: `qed solve "<plain-words task>" --json`. It takes minutes. Do not pass `--apply`,
     `--allow-risky` or `--yes` unless the user asked for that.
   - Over MCP: always pass `project_dir` as the absolute repository root. If `solve` returns
     `status: "running"`, poll `status` with its `job_id`.
5. **Verify; don't trust the grade alone.** Follow [references/verification.md](references/verification.md):
   read the diff, run the project's tests yourself, and look for the red flags below. If a receipt
   matters, run `qed verify <receipt_path>`.
6. **Apply only with consent.** A solve result is not in the user's files. Show the diff and grade,
   then run `qed apply <task id>` once the user agrees. Grade C or D needs extra confirmation; never
   add `--yes` on their behalf. `qed undo` reverts the last apply.
7. **Report honestly**, using the template in [references/workflow.md](references/workflow.md):
   what QEDCode was asked, the grade and its one-line summary, the files changed, the tests run and
   their results, the receipt path, and what is still unproven.

## Red flags (seen in real runs)

- **Grade C · "tests could not run: ..."** (on `8824706`: "no tests ran") in a project that has
  tests: the test runner couldn't start, usually because the chosen Python has no pytest. That's an
  environment problem, not a code problem. QEDCode uses the project's `.venv/` or `venv/`, then
  `VIRTUAL_ENV`, then `python3` on PATH. The MCP server doesn't inherit your shell's virtualenv.
  `notes` names the interpreter and the reason. MCP `check` returns `notes` only from `005c8d2` on;
  before that, re-run `qed check --json` from the CLI to see them. Fix the environment (with the
  user's OK) rather than reporting C as a result.
- **"tests weakened in ..."** (grade C), or **"protected files changed"** (grade B), in a `qed
  check` summary: existing tests or test configuration were edited. `check` reports this instead
  of rejecting it. Inspect those files. On `8824706` a weakened test still shows only "protected
  files changed" at grade B, so read the test diff yourself.
- **Exit code 0 is not success.** `qed check` exits 0 for any graded result, C and D included.
  Read `status` and `grade`, not just the exit code.
- **`fbpa: skipped (no new test)`**: nothing proved the bug was fixed. For grade A, add a test that
  fails on the old code. A **new** test file works on every build. Appending new test functions to
  an existing Python test file also earns A from `005c8d2` on, but on `8824706` it counts as a
  protected change and caps the grade at B.
- **`status: "busy"`**: another QEDCode job holds this project. Wait; don't delete `.qed/lock`.

## Hard rules

- Don't invent `qed` commands or flags. If you need one that isn't documented here, check `qed --help`.
- Never edit `.qed/` or receipts by hand, and never present a receipt as verified without running
  `qed verify`.
- Never claim a fix works just because QEDCode produced a candidate. Grades A and B are evidence,
  not a guarantee. Tests run on the local machine without network isolation unless the sealed test
  box (`qed sandbox`) is on, and receipts say so under "not proven".
- If QEDCode fails, report the message and carry on without it. Don't loop on retries.

See [references/safety-and-permissions.md](references/safety-and-permissions.md),
[references/troubleshooting.md](references/troubleshooting.md), and the worked examples in
[examples/](examples/).
