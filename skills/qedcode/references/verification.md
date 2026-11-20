# Verifying a QEDCode result

A grade is evidence from deterministic checks, not proof that the change is what the user wanted.
Do all of these before calling the work done.

## 1. Understand the grade

| Grade | What QEDCode established | What you still owe |
| --- | --- | --- |
| **A** Proven | A new test failed on the old code and passes now; the full suite shows no regressions; no protected file changed | Read the diff and the new test: does the test express the user's actual requirement? |
| **B** Tested | Tests pass, but nothing proved the exact problem, **or** protected files (existing tests or test config) changed, **or** risky code needed approval | Find out which. The summary line says (`protected files changed`, `fbpa: skipped`) |
| **C** Checked | It parses (and lints, for Python), but **no test ran**, or (`check`, from `005c8d2`) a test was weakened | Read the summary. `tests could not run` / `no tests ran` with tests present is an environment problem (troubleshooting.md). `tests weakened in <file>` means a skip, removed asserts or an assert that can never fail: undo that. From `e1f95ec`, a change that alters only comments or formatting outside tests is also C: it doesn't fix anything |
| **D** Not checked | No check could run | Treat it as an unverified suggestion |
| none / `rejected` | Failed a stage | Not a result. Fix the code, or report that it failed |

## 2. Read the actual diff

- `git diff` (path A) or the `diff` field (path B). Every changed line should relate to the task.
- Look for edits to existing tests, skipped tests (`skip`, `xfail`, `.only`), weakened assertions,
  broad `except`, or hard-coded expected values.
- New tests should assert the behaviour the user described, not just whatever the code now returns.

## 3. Run the tests yourself

Run the project's normal test command in the real working tree (after `qed apply`, for path B),
for example `.venv/bin/python -m pytest -q` or `npm test`. Use the interpreter named in the
`qed check --json` `notes`, so your run matches QEDCode's. Report the command and its result. If
your run disagrees with the grade, say so and trust the run you can see.

## 4. Re-check the receipt when it matters

```bash
qed verify <receipt_path>
```

`VERIFIED` means the recorded results still reproduce from the base commit. `NOT VERIFIED` lists
what no longer matches. That usually means the code or the base changed since the receipt was
written. A grade C receipt has no tests to re-run; the note says only the patch was checked.

## 5. State what isn't proven

Receipts list gaps under "not proven". Typical gaps: tests ran without network isolation (no
sealed test box); known failing tests on the base were ignored; the full suite didn't run; JS
projects get no lint stage. Include the relevant gaps in your report.
