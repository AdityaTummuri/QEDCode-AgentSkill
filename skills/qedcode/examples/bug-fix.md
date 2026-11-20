# Example: fix a bug yourself, then prove it with `qed check`

Recorded with QEDCode 0.1.0 on its bug-zoo project `001_paginate_off_by_one`. The commands and
output are real. No model was needed.

**User:** "Every page of my product list shows one item fewer than the page size. Fix paginate."

## 1. Look before touching anything

```bash
$ git status --short          # clean: nothing of the user's is uncommitted
$ command -v qed && qed --version
/Users/me/.local/bin/qed
0.1.0
```

## 2. Write the fix and a regression test that fails on the old code

```diff
 def paginate(items, page, size):
     """Return the items on a 1-based page of the given size."""
     start = (page - 1) * size
-    end = start + size - 1
+    end = start + size
     return list(items[start:end])
```

A **new** file, `tests/test_regression.py`, asserts that full pages have `size` items. The existing
tests are left alone.

## 3. Grade it

```bash
$ qed check --json 2>/dev/null
{
 "status": "graded",
 "grade": "A",
 "summary": "Grade A · repro test failed before, passes now · 8/8 tests pass · lint clean · no protected files changed",
 "failing_tests": [],
 "receipt_path": "/path/to/project/.qed/receipts/t-20261121-010331-d204.json",
 "notes": ["Using the detected Python (/path/to/project/.venv/bin/python). ..."],
 ...
}
$ qed verify .qed/receipts/t-20261121-010331-d204.json
VERIFIED
Grade A · repro test failed before, passes now · 8/8 tests pass · lint clean · no protected files changed
```

## 4. Report

```
QEDCode: check of my change
Result:  Grade A — repro test failed before, passes now · 8/8 tests pass · lint clean · no protected files changed
Files:   src/shop/pages.py (1 line), tests/test_regression.py (new)
Tests:   pytest -q → 8 passed
Receipt: .qed/receipts/t-20261121-010331-d204.json (qed verify: VERIFIED)
Not proven: tests ran on this machine without network isolation (no sealed test box)
```

## What the other outcomes looked like (same project, real runs)

| Change | `qed check` result | Exit |
| --- | --- | --- |
| Wrong fix (`end = start + size + 1`) | `rejected`, `Rejected at fbpa`, failing `tests.test_regression::test_full_pages_have_the_page_size` | 1 |
| Syntax error added | `Rejected at parse` · `src/shop/pages.py, line 16: invalid syntax` | 1 |
| An existing test weakened (`assert True or ...`), no fix | **Grade B** · `5/5 tests pass · lint clean · protected files changed` | 0 |
| No changes at all | `Your files are identical to HEAD, so there is nothing to check.` | 2 |
| Same correct fix, but the interpreter had no pytest (MCP, no `.venv`) | **Grade C** · `no tests ran` | 0 |

Rows 3 and 5 are the traps: a weakened test still earned B, and a missing test runner looked like an
ordinary C. Read the summary line every time.
