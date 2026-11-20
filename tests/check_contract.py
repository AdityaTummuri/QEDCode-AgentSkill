#!/usr/bin/env python3
"""Contract test: the `qed check` / `qed verify` behaviour this skill documents still holds.

No model is needed. On a copy of one QEDCode bug zoo project it checks, against the real `qed`:

  1. a correct fix with a regression test in a NEW test file -> status graded, grade A, exit 0,
     and every JSON field named in references/commands-and-interfaces.md is present;
  2. `qed verify <receipt>` -> VERIFIED, exit 0;
  3. a wrong fix -> status rejected, exit 1;
  4. no changes -> exit 2;
  5. a weakened existing test -> grade C with "tests weakened in" in the summary.

CI runs it weekly against QEDCode's main branch, so a change in QEDCode that makes the skill's
advice wrong fails here first.

Run: python3 tests/check_contract.py --zoo ../QEDCode/bugzoo [--qed "<command>"]
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_solve_smoke import prepare, run  # noqa: E402

PROJECT = "002_discount_threshold"
CHECK_FIELDS = {
    "status", "grade", "summary", "failing_tests", "receipt_path", "task_id", "base", "message",
    "notes",
}
REGRESSION = """from store.pricing import apply_discount


def test_exactly_the_threshold_gets_the_discount():
    assert apply_discount(100) == 90
"""


def check(qed: list[str], proj: Path) -> tuple[int, dict]:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    done = run([*qed, "check", "--json"], proj, timeout=900, env=env)
    try:
        return done.returncode, json.loads(done.stdout)
    except json.JSONDecodeError:
        return done.returncode, {"_raw": (done.stdout + done.stderr)[-400:]}


def reset(proj: Path) -> None:
    run(["git", "checkout", "-q", "--", "."], proj)
    run(["git", "clean", "-qfd", "-e", ".venv", "-e", ".qed"], proj)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--zoo", required=True, type=Path, help="QEDCode's bugzoo folder")
    parser.add_argument("--qed", default="qed", help='command that runs QEDCode (default "qed")')
    args = parser.parse_args()
    qed = shlex.split(args.qed)
    if shutil.which(qed[0]) is None:
        print(f"Cannot find {qed[0]!r}. Install QEDCode or pass --qed.", file=sys.stderr)
        return 2
    src = args.zoo.resolve() / PROJECT
    problems: list[str] = []
    work = Path(tempfile.mkdtemp(prefix="qed-contract-"))
    try:
        proj = work / PROJECT
        prepare(src, proj)
        patch = (src / "solution.patch").read_bytes()

        # 1 + 2: correct fix, new regression test file
        subprocess.run(["git", "apply", "-"], cwd=proj, input=patch, check=True)
        (proj / "tests" / "test_threshold_regression.py").write_text(REGRESSION)
        code, out = check(qed, proj)
        missing = CHECK_FIELDS - out.keys()
        if missing:
            problems.append(f"check --json lacks documented fields: {sorted(missing)} ({out})")
        if (code, out.get("status"), out.get("grade")) != (0, "graded", "A"):
            problems.append(f"correct fix: expected exit 0, graded, A; got {code}, {out}")
        receipt = out.get("receipt_path")
        if receipt:
            ver = run([*qed, "verify", receipt], proj, timeout=900)
            if ver.returncode != 0 or "VERIFIED" not in ver.stdout:
                problems.append(f"verify: expected VERIFIED, exit 0; got {ver.returncode}")

        # 3: wrong fix (the bug stays, the new test still fails)
        reset(proj)
        (proj / "tests" / "test_threshold_regression.py").write_text(REGRESSION)
        pricing = proj / "src" / "store" / "pricing.py"
        pricing.write_text(pricing.read_text().replace('"""Orders', '"""Orders (checked)'))
        code, out = check(qed, proj)
        if (code, out.get("status")) != (1, "rejected"):
            problems.append(f"wrong fix: expected exit 1, rejected; got {code}, {out}")

        # 4: no changes
        reset(proj)
        code, out = check(qed, proj)
        if code != 2:
            problems.append(f"no changes: expected exit 2; got {code}, {out}")

        # 5: weakened existing test
        test_file = next((proj / "tests").glob("test_*.py"))
        text = test_file.read_text()
        test_file.write_text("import pytest\n\n" + text.replace("def test_", '@pytest.mark.skip("x")\ndef test_', 1))
        code, out = check(qed, proj)
        if out.get("grade") != "C" or "tests weakened in" not in out.get("summary", ""):
            problems.append(f"weakened test: expected grade C, 'tests weakened in'; got {out}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    for p in problems:
        print(f"FAIL: {p}")
    if problems:
        return 1
    print("OK: qed check/verify behave as the skill documents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
