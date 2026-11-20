#!/usr/bin/env python3
"""Agent smoke test inside Google Antigravity (the `agy` CLI), run on QEDCode's bug zoo.

It checks the whole IDE integration with Antigravity's own cloud model driving the agent:
the skill is picked up from the workspace, the agent reaches QEDCode through MCP, and the fix it
reports really works. For each bug zoo project it:

  1. copies the project (without its hidden tests and solution) into a fresh git repository,
     with a .venv that has pytest,
  2. installs the skill for that workspace only (`.agents/skills/qedcode`) and registers
     `qed mcp` for that workspace only (`.agents/mcp_config.json`); your global Antigravity
     settings are never touched,
  3. runs `agy -p "<task.txt> ... make sure the fix is proven"` (the prompt doesn't name QEDCode
     unless --name-qedcode is given),
  4. looks for QEDCode receipts, re-runs the newest with `qed verify`, and runs the zoo's HIDDEN
     tests on the agent's result as an independent check,

then prints a Markdown table for tests/compatibility.md and keeps each transcript.

Usage:
  python3 tests/run_ide_smoke.py --zoo ../QEDCode/bugzoo --only 002
  python3 tests/run_ide_smoke.py --zoo ../QEDCode/bugzoo --only 001 002 --name-qedcode
  python3 tests/run_ide_smoke.py --zoo ../QEDCode/bugzoo --qed ../QEDCode/.venv/bin/qed

Needs: git, uv, `qed` (or --qed) and `agy`, signed in (run `agy` once by itself to sign in).
`qed check` and `qed verify` need no model; if the agent calls `solve`, QEDCode uses the model
from `qed setup` (local or cloud). Exit code 0 if every agent result passes its hidden tests.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_solve_smoke import prepare, run, venv_python  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent / "skills" / "qedcode"
PROOF = "Fix it, and make sure the fix is actually proven before you tell me it is done."


@dataclass
class Row:
    project: str
    agent: str = "-"
    seconds: float = 0.0
    receipts: int = 0
    grade: str = "-"
    verified: str = "-"
    hidden: str = "-"
    note: str = ""


def install_workspace(proj: Path, qed: list[str]) -> None:
    """Skill + MCP server for this workspace only, hidden from git so `qed check` ignores them."""
    agents = proj / ".agents"
    shutil.copytree(SKILL, agents / "skills" / "qedcode")
    command = shutil.which(qed[0]) or qed[0]
    server = {"command": command, "args": [*qed[1:], "mcp"]}
    (agents / "mcp_config.json").write_text(
        json.dumps({"mcpServers": {"qedcode": server}}, indent=2) + "\n", encoding="utf-8"
    )
    exclude = proj / ".git" / "info" / "exclude"
    with exclude.open("a", encoding="utf-8") as fh:
        fh.write("\n.agents/\n")


def newest_receipt(proj: Path) -> tuple[int, Path | None]:
    folder = proj / ".qed" / "receipts"
    found = sorted(folder.glob("*.json"), key=lambda p: p.stat().st_mtime) if folder.is_dir() else []
    return len(found), (found[-1] if found else None)


def smoke_one(src: Path, work: Path, out: Path, args: argparse.Namespace, qed: list[str]) -> Row:
    row = Row(src.name)
    proj = work / src.name
    try:
        task = prepare(src, proj)
        install_workspace(proj, qed)
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        row.note = f"setup failed: {exc}"
        return row
    prompt = f"{task} {PROOF}"
    if args.name_qedcode:
        prompt += " Use QEDCode (the qedcode MCP tools) for the proof."
    cmd = ["agy", "-p", prompt, "--print-timeout", f"{args.timeout}s"]
    cmd += ["--dangerously-skip-permissions"] if args.skip_permissions else ["--mode", "auto"]
    if args.model:
        cmd += ["--model", args.model]
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    start = time.monotonic()
    try:
        done = run(cmd, proj, timeout=args.timeout + 120, env=env)
    except subprocess.TimeoutExpired:
        row.agent, row.note = "timeout", f"agy ran over {args.timeout + 120}s"
        return row
    row.seconds = round(time.monotonic() - start, 1)
    transcript = out / f"{src.name}.txt"
    transcript.write_text(f"$ {shlex.join(cmd)}\n\n{done.stdout}\n{done.stderr}", encoding="utf-8")
    row.agent = "ok" if done.returncode == 0 else f"exit {done.returncode}"
    if "authentication" in done.stderr.lower():
        row.note = "agy is not signed in: run `agy` once by itself"
        return row
    row.receipts, receipt = newest_receipt(proj)
    if receipt is not None:
        data = json.loads(receipt.read_text(encoding="utf-8"))
        row.grade = data.get("grade") or "-"
        ver = run([*qed, "verify", str(receipt)], proj, env=env)
        row.verified = "VERIFIED" if ver.returncode == 0 else "NOT VERIFIED"
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
    row.note = row.note or f"transcript: {transcript.name}"
    return row


def table(rows: list[Row], versions: str, named: bool) -> str:
    lines = [
        f"{versions}, prompt {'names' if named else 'does not name'} QEDCode, "
        f"{time.strftime('%Y-%m-%d')}",
        "",
        "| Project | Agent | Seconds | Receipts | Grade | qed verify | Hidden tests | Note |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        note = r.note.replace("|", "/").replace("\n", " ")
        lines.append(
            f"| {r.project} | {r.agent} | {r.seconds} | {r.receipts} | {r.grade} | {r.verified} "
            f"| {r.hidden} | {note} |"
        )
    used = [r for r in rows if r.receipts]
    ok = [r for r in rows if r.hidden.startswith("pass")]
    lines += ["", f"QEDCode used in {len(used)}/{len(rows)}; hidden tests pass for "
              f"{len(ok)}/{len(rows)}."]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--zoo", required=True, type=Path, help="QEDCode's bugzoo folder")
    parser.add_argument("--qed", default="qed", help='command that runs QEDCode (default "qed")')
    parser.add_argument("--only", nargs="*", default=["002"], help="project name prefixes")
    parser.add_argument("--name-qedcode", action="store_true", help="name QEDCode in the prompt")
    parser.add_argument("--model", help="Antigravity model for the agent (see `agy models`)")
    parser.add_argument("--timeout", type=int, default=900, help="seconds per agent run")
    parser.add_argument(
        "--skip-permissions",
        action="store_true",
        help="pass --dangerously-skip-permissions to agy (default: --mode auto)",
    )
    parser.add_argument("--out", type=Path, help="folder for transcripts and the report")
    parser.add_argument("--keep", action="store_true", help="keep the temporary projects")
    args = parser.parse_args()

    qed = shlex.split(args.qed)
    for program in (qed[0], "agy", "uv", "git"):
        if shutil.which(program) is None:
            print(f"Cannot find {program!r} on PATH.", file=sys.stderr)
            return 2
    versions = (
        f"QEDCode `{run([*qed, '--version'], Path.cwd()).stdout.strip() or '?'}`, "
        f"agy `{run(['agy', '--version'], Path.cwd()).stdout.strip() or '?'}`"
    )
    projects = sorted(p for p in args.zoo.resolve().iterdir() if p.is_dir() and p.name[:3].isdigit())
    projects = [p for p in projects if any(p.name.startswith(o) for o in args.only)]
    if not projects:
        print(f"No matching bug zoo projects in {args.zoo}", file=sys.stderr)
        return 2
    out = args.out or Path(tempfile.mkdtemp(prefix="qed-ide-smoke-report-"))
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="qed-ide-smoke-"))
    rows: list[Row] = []
    try:
        for src in projects:
            print(f"[{len(rows) + 1}/{len(projects)}] {src.name} ...", file=sys.stderr, flush=True)
            rows.append(smoke_one(src, work, out, args, qed))
            r = rows[-1]
            print(f"    agent={r.agent} receipts={r.receipts} grade={r.grade} {r.hidden}",
                  file=sys.stderr)
    finally:
        if args.keep:
            print(f"Projects kept in {work}", file=sys.stderr)
        else:
            shutil.rmtree(work, ignore_errors=True)
    report = table(rows, versions, args.name_qedcode)
    (out / "report.md").write_text(report + "\n", encoding="utf-8")
    print(report)
    print(f"Transcripts and report.md in {out}", file=sys.stderr)
    return 0 if rows and all(r.hidden.startswith("pass") for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
