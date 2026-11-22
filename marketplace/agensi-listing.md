# Agensi listing (draft, to paste into the Creator Dashboard)

Submitting is done by hand. It needs an Agensi account with Creator Mode, and the listing goes
through Agensi's security scan and review. Check the dashboard's current upload rules first: no
official public zip spec was found, so the layout below follows Agensi's creator guide and
checklist.

## Package

- File: `dist/qedcode-skill-<version>.zip`, built by `scripts/package.sh`
- Layout: one top-level folder `qedcode/` with `SKILL.md` at its root, plus `references/` and
  `examples/` (Markdown only)
- `SKILL.md` frontmatter: `name: qedcode` and `description`, checked by `tests/validate_skill.py`
- No scripts, binaries, secrets or network calls in the package. The skill tells the agent to run
  the user's separately installed `qed` command, and never to install software unasked

## Listing fields

**Title:** QEDCode: proven fixes for coding agents

**Icon / image:** `assets/mark.svg` (square QEDCode mark; export a PNG if the dashboard needs one)

**Price:** Free

**Tags:** testing, verification, debugging, bug-fix, python, javascript, typescript, mcp,
claude-code, code-quality

**Short description (one line):**
Teaches your coding agent to grade its own fixes A to D with QEDCode's deterministic checks and
proof receipts, before it says "done".

**Description:**

> Coding agents often say a bug is fixed when it isn't. This skill teaches the agent to prove it
> with [QEDCode](https://github.com/AdityaTummuri/QEDCode), an open-source, local-first coding
> engine by Aditya Tummuri.
>
> With the skill installed, the agent:
>
> - writes a regression test that fails on the old code, then grades its change with `qed check`.
>   That needs no model: QEDCode runs your tests in a throw-away git worktree and returns grade A
>   (proven), B (tested), C (checked) or D (not checked), plus a receipt that `qed verify` re-runs;
> - can let `qed solve` generate several candidate fixes and keep the best verified one, if you
>   have set up a local or cloud model for QEDCode;
> - watches for the traps found in testing: weakened tests, a missing test runner that shows up as
>   "no tests ran", and exit code 0 on a low grade;
> - never installs software, downloads models or applies changes to your files without asking;
> - reports the grade, files, tests, receipt and what is still unproven, and doesn't hide failures.
>
> Works with the `qed` CLI or QEDCode's MCP server. Tested in Claude Code (CLI and MCP), on Python
> projects with pytest. JavaScript/TypeScript projects are supported by QEDCode but haven't been
> tested with this skill yet.
>
> **Requires:** QEDCode installed separately (`uv tool install
> git+https://github.com/AdityaTummuri/QEDCode`), and a git project with tests. This package
> contains instructions only, not the engine.

**Links:**
- Source: https://github.com/AdityaTummuri/QEDCode-AgentSkill
- Engine: https://github.com/AdityaTummuri/QEDCode

**Attribution:**
QEDCode Agent Skill is an integration guide for QEDCode, an open-source coding engine created by
Aditya Tummuri. It isn't an official integration of Agensi or of any agent platform.

## Notes for the reviewer (if the form asks)

- What the skill makes the agent run: `qed --version`, `qed doctor`, `qed check --json`,
  `qed solve ... --json`, `qed verify <receipt>`, and `qed apply` / `qed undo` (only after the user
  agrees). Plus the project's own tests, `git status` and `git diff`.
- What it forbids without consent: installs, `qed setup`, model downloads, `qed connect`, sandbox
  setup, `--yes`, `--allow-risky`, MCP `solve(apply=true)`.
- Licence: Apache-2.0, the same as QEDCode.

## Before submitting

- [ ] `QED=qed scripts/package.sh` passes and builds the zip
- [ ] The version in `CHANGELOG.md`, `.claude-plugin/marketplace.json` and the zip name all match
- [ ] Compatibility claims above match `tests/compatibility.md`
