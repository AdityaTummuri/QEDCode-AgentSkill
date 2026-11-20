# Workflow in detail

## Choosing the path

```
Is there a git repo with a commit, in Python or JS/TS?   no  -> don't use QEDCode
              | yes
Is `qed` installed (or are the qedcode MCP tools present)?   no  -> tell the user, link installation.md, continue normally
              | yes
Did you (or the user) already write the change?          yes -> qed check   (path A)
              | no
Is a model ready? (`qed doctor`: engine build + model file ok, or cloud set)
              | no  -> write the fix yourself, then qed check (path A); mention that `qed solve` needs `qed setup`
              | yes -> qed solve  (path B)
```

## Path A — grade a change with `qed check`

1. `git status` and `git diff`. Know exactly what's uncommitted. `check` grades all of it.
2. For a bug fix, **add a regression test that fails on the old code**. This is what earns grade A:
   QEDCode runs the new test on `HEAD` (it must fail) and on your change (it must pass). Put it in a
   **new test file** (e.g. `tests/test_<bug>_regression.py`): that earns A on every build. On
   QEDCode `8824706`, appending a test to an existing test file counts as a protected change and
   caps the grade at B (seen in testing). From `005c8d2` on, appending new `test_*` functions
   without touching the old ones is fine, and only the new tests count as proof.
3. Run `qed check --json`. Parse stdout as JSON. Progress lines go to stderr.
4. Read `status`, `grade`, `summary`, `failing_tests`, `notes`.
   - `rejected`: the summary names the stage (`Rejected at parse`, `Rejected at fbpa`, ...) and
     `failing_tests` lists failures. Fix the code and check again.
   - `graded`: continue with verification.md.
   - `no_changes`: nothing differs from the base. Pass `--base <ref>` to compare with an older
     commit.
5. Keep the `receipt_path` for the report.

## Path B — generate a fix with `qed solve`

1. Write the task in plain words, with the symptom and where it shows: `"paginate drops the last
   item of every page"`. QEDCode writes its own failing test, finds the files and tries several
   candidates.
2. Pick a speed: `fast` for a quick try, `normal` (default), or `sure` for a hard bug. Expect minutes.
3. CLI: `qed solve "<task>" --json`. MCP: `solve(task=..., project_dir=<abs root>)`, then poll
   `status(job_id)` while it returns `running`.
4. Handle the status:
   - `done`: inspect `best.diff` (CLI) or `diff` (MCP), `grade`, `explanation`, `receipt_path`.
   - `no_fix`: no candidate passed. Report that and either fix it yourself or try `--speed sure`
     once, with the user's agreement.
   - `needs_input`: relay `question` to the user. Don't make up an answer.
   - `busy` / `error`: report the message.
5. Nothing is applied yet. Show the user the diff and grade. Apply only after they agree:
   `qed apply <task id>` (the task id is the receipt file name without `.json`). Then run the
   project's tests in the real working tree.

## Report template

```
QEDCode: <check of my change | solve "<task>">
Result:  Grade <X> — <summary line>
Files:   <list from git diff --stat, or apply output>
Tests:   <command you ran yourself> → <n passed / n failed>; QEDCode full suite: <n/n>
Receipt: <path> (qed verify: VERIFIED | NOT VERIFIED | not run)
Not proven: <e.g. no network isolation; fbpa skipped; known failures ignored; grade C has no test coverage>
```

Keep it short, and never leave out a failure. If QEDCode wasn't used, or failed, say why in one line.
