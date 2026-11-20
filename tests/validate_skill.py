#!/usr/bin/env python3
"""Validate the QEDCode skill package.

Checks:
  1. skills/qedcode/SKILL.md has valid frontmatter (name matches the folder, lowercase-hyphen,
     <= 64 chars; description present, <= 1024 chars, no angle brackets).
  2. SKILL.md stays concise (<= 500 lines).
  3. Every relative Markdown link in the package resolves to a file.
  4. Every `qed <command>` and every `--flag` used with it exists in the installed QEDCode
     (read from `qed --help` / `qed <command> --help`). Skipped with a warning if `qed` is not
     found; pass --qed "<command>" to point at one, e.g. --qed "uv run --project ../QEDCode qed".

Run: python3 tests/validate_skill.py [--qed "<command>"]
Exit code 0 = all checks passed, 1 = problems found.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "qedcode"
MAX_SKILL_LINES = 500

# `qed <sub>` inside code: the token after `qed` that looks like a subcommand.
QED_CALL = re.compile(r"(?<![\w/.-])qed\s+([a-z][a-z-]*)((?:[ \t]+[^\s`]+)*)")
FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z-]*)")
# Generic words that follow "qed" in prose-like code comments, not commands.
NOT_COMMANDS = {"is", "and", "or", "the", "with", "in"}
# Flags that belong to other programs that can appear on the same line.
FOREIGN_FLAGS = {"--project", "--python", "--force"}


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with a --- frontmatter block")
    end = text.index("\n---", 4)
    block = text[4:end]
    data: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        m = re.match(r"^([a-z_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            value = m.group(2).strip()
            data[key] = "" if value in (">-", ">", "|", "|-") else value
        elif key and line.startswith("  "):
            data[key] = (data[key] + " " + line.strip()).strip()
    return data


def check_frontmatter(problems: list[str]) -> None:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    try:
        meta = frontmatter(text)
    except ValueError as exc:
        problems.append(str(exc))
        return
    name = meta.get("name", "")
    desc = meta.get("description", "")
    if name != SKILL_DIR.name:
        problems.append(f"frontmatter name '{name}' != folder name '{SKILL_DIR.name}'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append(f"name '{name}' must be lowercase-hyphenated and <= 64 chars")
    if not desc:
        problems.append("description is missing")
    if len(desc) > 1024:
        problems.append(f"description is {len(desc)} chars (max 1024)")
    if "<" in desc or ">" in desc:
        problems.append("description must not contain angle brackets")
    lines = text.count("\n") + 1
    if lines > MAX_SKILL_LINES:
        problems.append(f"SKILL.md is {lines} lines (max {MAX_SKILL_LINES})")


def markdown_files() -> list[Path]:
    return sorted(SKILL_DIR.rglob("*.md"))


def check_links(problems: list[str]) -> None:
    for md in markdown_files():
        text = md.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if re.match(r"^[a-z]+://", target) or target.startswith("#"):
                continue
            path = (md.parent / target.split("#", 1)[0]).resolve()
            if not path.exists():
                problems.append(f"{md.relative_to(ROOT)}: broken link -> {target}")


def code_snippets(text: str) -> list[str]:
    """Inline code spans and fenced code block lines."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            out.append(line.split("#", 1)[0] if "qed" in line else line)
        else:
            out.extend(re.findall(r"`([^`]+)`", line))
    return out


def find_qed(explicit: str | None) -> list[str] | None:
    if explicit:
        return shlex.split(explicit)
    found = shutil.which("qed")
    return [found] if found else None


def help_text(qed: list[str], *args: str) -> str:
    env = dict(os.environ, COLUMNS="200", NO_COLOR="1", TERM="dumb")
    proc = subprocess.run(
        [*qed, *args, "--help"], capture_output=True, text=True, timeout=120, env=env
    )
    return proc.stdout + proc.stderr


def check_commands(problems: list[str], warnings: list[str], qed: list[str] | None) -> None:
    used: dict[str, set[str]] = {}
    where: dict[str, str] = {}  # "sub" or "sub --flag" -> first file that uses it
    for md in markdown_files():
        for snippet in code_snippets(md.read_text(encoding="utf-8")):
            for m in QED_CALL.finditer(snippet):
                sub, rest = m.group(1), m.group(2)
                if sub in NOT_COMMANDS:
                    continue
                flags = {f for f in FLAG.findall(rest) if f not in FOREIGN_FLAGS}
                used.setdefault(sub, set()).update(flags)
                rel = str(md.relative_to(ROOT))
                where.setdefault(sub, rel)
                for flag in flags:
                    where.setdefault(f"{sub} {flag}", rel)
    if qed is None:
        warnings.append("`qed` not found: command and flag checks skipped (use --qed)")
        return
    top = help_text(qed)
    commands = set(re.findall(r"^[│ ]\s*([a-z][a-z-]+)\s{2,}", top, flags=re.M))
    if not commands:
        problems.append("could not read the command list from `qed --help`")
        return
    for sub, flags in sorted(used.items()):
        if sub not in commands:
            problems.append(f"{where[sub]}: `qed {sub}` is not a QEDCode command")
            continue
        if flags:
            sub_help = help_text(qed, sub)
            for flag in sorted(flags):
                if flag not in sub_help:
                    problems.append(f"{where[f'{sub} {flag}']}: `qed {sub} {flag}` is not a known flag")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--qed", help='command that runs QEDCode, e.g. "qed"')
    args = parser.parse_args()
    problems: list[str] = []
    warnings: list[str] = []
    check_frontmatter(problems)
    check_links(problems)
    check_commands(problems, warnings, find_qed(args.qed))
    for w in warnings:
        print(f"warning: {w}")
    for p in problems:
        print(f"FAIL: {p}")
    if problems:
        return 1
    print(f"OK: {len(markdown_files())} files checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
