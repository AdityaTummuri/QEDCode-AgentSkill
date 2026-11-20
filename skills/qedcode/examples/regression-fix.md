# Example: let QEDCode generate the fix with `solve` (model required)

The argument names, statuses and fields come from QEDCode 0.1.0's source (`mcp_server.py`, `cli.py`).
This skill's tests didn't run a full solve, because that needs a downloaded model. The progress
lines follow the README's recorded session.

**User:** "Customers who spend exactly 100 aren't getting their 10% discount. Can QEDCode fix it?"
(This is QEDCode's bug-zoo project `002_discount_threshold`, so you can reproduce it.)

## 1. Preconditions

```bash
$ git status --short            # note anything the user has in progress
$ qed doctor                    # look for "ok" on engine build + model file (or a cloud model)
```

If the doctor shows `FAIL engine build` / `FAIL model file`, stop here. Tell the user `solve` needs
`qed setup` (which they run themselves), and offer to write the fix and grade it with `qed check`
instead (see bug-fix.md).

## 2. Run it (MCP shown; the CLI equivalent is `qed solve "<task>" --json`)

```
mcp__qedcode__solve(
  task="Customers who spend exactly 100 are not getting their 10% discount; it should start at 100 or more",
  speed="normal",
  project_dir="/abs/path/to/repo",
  wait_seconds=60
)
→ {"status": "running", "job_id": "3f9c0a1b2d", "progress": ["Taking a snapshot of your project...", ...]}

mcp__qedcode__status(job_id="3f9c0a1b2d")      # repeat until status is no longer "running"
→ {"status": "done", "grade": "A", "summary": "...", "explanation": "...", "diff": "...",
   "receipt_path": "/abs/path/to/repo/.qed/receipts/t-....json"}
```

`apply` stays `false`: nothing in the user's files has changed.

## 3. Review, then ask

Read `diff` (does it touch only the discount logic, plus a new test?) and `explanation`. Then tell
the user:

> QEDCode found a grade A fix (a new test failed before, passes now, full suite green). It changes
> one comparison in `src/store/pricing.py` from `>` to `>=` and adds a new test file
> (`<name from the diff>`). Shall I apply it?

## 4. After the user says yes

```bash
$ qed apply t-....        # task id = receipt file name without .json
Applied to src/store/pricing.py, tests/.... Undo any time with `qed undo`.
$ pytest -q               # your own run in the real working tree
```

## If it doesn't work out

- `no_fix`: say that no candidate passed the checks. Offer `speed="sure"` once, or fix it
  yourself and `qed check` it.
- `needs_input`: relay `question` word for word.
- `busy`: another job holds the project. Poll the returned `job_id`.
