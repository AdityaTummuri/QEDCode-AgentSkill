#!/usr/bin/env python3
"""Real-model smoke test for `qed solve`, run on QEDCode's bug zoo.

The skill's other tests need no model. This one needs a computer where `qed setup` has finished
(a local model, or a cloud model). For each bug zoo project it:

  1. copies the project (without its hidden tests and solution) into a fresh git repository,
     with a .venv that has pytest,
  2. runs `qed solve "<task.txt>" --json --speed <speed>`; nothing is applied yet,
  3. runs `qed verify` on the receipt,
  4. applies the result with `qed apply` and runs the zoo's HIDDEN tests, which QEDCode never
     saw, as an independent check,

then prints a Markdown table, and writes it to --report, ready for tests/compatibility.md.

Usage:
  python3 tests/run_solve_smoke.py --zoo ../QEDCode/bugzoo                 # every project
  python3 tests/run_solve_smoke.py --zoo ../QEDCode/bugzoo --only 001 002 --speed fast
  python3 tests/run_solve_smoke.py --zoo ../QEDCode/bugzoo --qed "uv run --project ../QEDCode qed"

Needs: git, uv, and `qed` (or --qed). It works in a temporary folder and never touches the zoo.
Exit code 0 if every solved project also passes its hidden tests, 1 otherwise.
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
import time
from dataclasses import dataclass
from pathlib import Path

LEFTOVERS = ("hidden", "solution.patch", "edits.txt", "task.txt")


@dataclass
class Row:
    project: str
    status: str = "-"
    grade: str = "-"
    seconds: float = 0.0
    verified: str = "-"
    hidden: str = "-"
    note: str = ""


def run(cmd: list[str], cwd: Path, timeout: float = 3600, env=None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env, check=False
    )


def venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def prepare(src: Path, dest: Path) -> str:
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    task = (dest / "task.txt").read_text(encoding="utf-8").strip()
    for name in LEFTOVERS:
        target = dest / name
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    (dest / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n.venv/\n")
    for cmd in (
        ["git", "init", "-q"],
        ["git", "add", "-A"],
        ["git", "-c", "user.name=qed-smoke", "-c", "user.email=smoke@example.invalid",
         "commit", "-q", "-m", "buggy"],
        ["uv", "venv", "-q", ".venv"],
        ["uv", "pip", "install", "-q", "--python", str(venv_python(dest / ".venv")), "pytest"],
    ):
        done = run(cmd, dest, timeout=600)
        if done.returncode != 0:
            raise RuntimeError(f"{' '.join(cmd)} failed: {done.stderr.strip()[-300:]}")
    return task


def smoke_one(src: Path, work: Path, qed: list[str], speed: str) -> Row:
    row = Row(src.name)
    proj = work / src.name
    try:
        task = prepare(src, proj)
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        row.note = f"setup failed: {exc}"
        return row
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    start = time.monotonic()
    try:
        done = run([*qed, "solve", task, "--json", "--speed", speed], proj, env=env)
    except subprocess.TimeoutExpired:
        row.status, row.note = "timeout", "solve took over an hour"
        return row
    row.seconds = round(time.monotonic() - start, 1)
    try:
        result = json.loads(done.stdout)
    except json.JSONDecodeError:
        row.status = f"exit {done.returncode}"
        row.note = (done.stderr.strip() or done.stdout.strip())[-200:]
        return row
    row.status = result.get("status", "?")
    best = result.get("best") or {}
    row.grade = best.get("grade") or "-"
    row.note = (result.get("message") or "")[:160]
    receipt = result.get("receipt_path")
    if receipt:
        ver = run([*qed, "verify", receipt], proj, env=env)
        row.verified = "VERIFIED" if ver.returncode == 0 else "NOT VERIFIED"
    if row.status == "done":
        task_id = (result.get("task") or {}).get("id", "")
        applied = run([*qed, "apply", task_id, "--yes"], proj, env=env)
        if applied.returncode != 0:
            row.hidden = "apply failed"
            row.note = applied.stdout.strip()[-160:]
            return row
        shutil.copytree(src / "hidden", proj / "hidden_check")
        hidden = run(
            [str(venv_python(proj / ".venv")), "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "hidden_check"],
            proj,
            timeout=600,
            env={**env, "PYTHONPATH": str(proj / "src")},
        )
        last = (hidden.stdout.strip().splitlines() or ["?"])[-1]
        row.hidden = ("pass: " if hidden.returncode == 0 else "FAIL: ") + last
    return row


def table(rows: list[Row], qed_version: str, speed: str) -> str:
    lines = [
        f"QEDCode `{qed_version}`, speed `{speed}`, {time.strftime('%Y-%m-%d')}",
        "",
        "| Project | Status | Grade | Seconds | qed verify | Hidden tests | Note |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        note = r.note.replace("|", "/").replace("\n", " ")
        lines.append(
            f"| {r.project} | {r.status} | {r.grade} | {r.seconds} | {r.verified} | "
            f"{r.hidden} | {note} |"
        )
    done = [r for r in rows if r.status == "done"]
    ok = [r for r in done if r.hidden.startswith("pass")]
    lines += ["", f"Solved {len(done)}/{len(rows)}; hidden tests pass for {len(ok)}/{len(done)}."]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--zoo", required=True, type=Path, help="QEDCode's bugzoo folder")
    parser.add_argument("--qed", default="qed", help='command that runs QEDCode (default "qed")')
    parser.add_argument("--speed", default="normal", choices=["fast", "normal", "sure"])
    parser.add_argument("--only", nargs="*", default=[], help="project name prefixes, e.g. 001")
    parser.add_argument("--report", type=Path, help="also write the Markdown table here")
    parser.add_argument("--keep", action="store_true", help="keep the temporary projects")
    args = parser.parse_args()

    qed = shlex.split(args.qed)
    if shutil.which(qed[0]) is None:
        print(f"Cannot find {qed[0]!r}. Install QEDCode or pass --qed.", file=sys.stderr)
        return 2
    version = run([*qed, "--version"], Path.cwd()).stdout.strip() or "?"
    projects = sorted(p for p in args.zoo.resolve().iterdir() if p.is_dir() and p.name[:3].isdigit())
    if args.only:
        projects = [p for p in projects if any(p.name.startswith(o) for o in args.only)]
    if not projects:
        print(f"No bug zoo projects found in {args.zoo}", file=sys.stderr)
        return 2

    work = Path(tempfile.mkdtemp(prefix="qed-solve-smoke-"))
    rows: list[Row] = []
    try:
        for src in projects:
            print(f"[{len(rows) + 1}/{len(projects)}] {src.name} ...", file=sys.stderr, flush=True)
            rows.append(smoke_one(src, work, qed, args.speed))
            r = rows[-1]
            print(f"    {r.status} grade={r.grade} {r.seconds}s {r.hidden}", file=sys.stderr)
    finally:
        if args.keep:
            print(f"Projects kept in {work}", file=sys.stderr)
        else:
            shutil.rmtree(work, ignore_errors=True)
    report = table(rows, version, args.speed)
    print(report)
    if args.report:
        args.report.write_text(report + "\n", encoding="utf-8")
    solved = [r for r in rows if r.status == "done"]
    return 0 if solved and all(r.hidden.startswith("pass") for r in solved) else 1


if __name__ == "__main__":
    sys.exit(main())
