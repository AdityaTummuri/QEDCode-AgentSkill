# QEDCode Agent Skill

An agent skill that teaches AI coding agents such as Claude Code to use
[**QEDCode**](https://github.com/AdityaTummuri/QEDCode) correctly: grade a change with deterministic
checks before calling it done, generate verified fixes, re-run proof receipts, and report the
results honestly.

> QEDCode Agent Skill is an integration guide for [QEDCode](https://github.com/AdityaTummuri/QEDCode),
> an open-source coding engine created by Aditya Tummuri. The skill contains instructions only. It
> doesn't bundle the engine, and it isn't an official integration of any agent platform.

## What QEDCode is

QEDCode is a local-first coding engine. It doesn't trust a model's first answer: it tests every
candidate change in a throw-away git worktree and grades it:

- **A** Proven: a new test failed before and passes now, with no regressions.
- **B** Tested: the tests pass, but nothing proved the exact problem.
- **C** Checked: the code parses and lints, but no test ran.
- **D** Not checked.

Each grade comes with a proof receipt that `qed verify` re-runs.

## What the skill adds

With the skill installed, an agent will:

1. Recognise suitable tasks: a reproducible bug, a failing test, a regression or a small feature
   in a Python or JS/TS git project with tests.
2. Check that `qed` (or the `qedcode` MCP server) is available. It never installs or sets anything
   up unasked.
3. Grade its own fix with `qed check`, which needs no model, or, when a model is configured, let
   `qed solve` generate one.
4. Read the diff, run the tests, and watch for traps found in testing:
   - a weakened test still gets grade B;
   - a missing pytest shows up as grade C "no tests ran";
   - exit code 0 doesn't mean success.
5. Apply results only with your consent, and report the grade, files, tests, receipt and what is
   still unproven.

## Requirements

- QEDCode **0.1.0** or later on PATH (`qed --version`). Install it with
  `uv tool install git+https://github.com/AdityaTummuri/QEDCode`.
  See [installation](skills/qedcode/references/installation.md).
- A git repository with at least one commit, in Python (pytest) or JS/TS (`node --test`, Vitest,
  Jest).
- `qed solve` only: a local or cloud model set up with `qed setup`. `qed check` and `qed verify`
  need no model.

## Install the skill

**Claude Code plugin (recommended):**

```
/plugin install qedcode --marketplace AdityaTummuri/QEDCode-AgentSkill
```

**Or as a plain skill:** copy or symlink the `skills/qedcode` folder into your skills directory:

```bash
git clone https://github.com/AdityaTummuri/QEDCode-AgentSkill
ln -s "$PWD/QEDCode-AgentSkill/skills/qedcode" ~/.claude/skills/qedcode          # all projects
# or: ln -s ... <project>/.claude/skills/qedcode                                   # one project
```

**Optional:** connect QEDCode's MCP server too (`qed connect`, or
`claude mcp add qedcode -- qed mcp`). The skill works with either the CLI or MCP.

## Usage

Just describe the problem. The skill activates on its own:

> Customers who spend exactly 100 aren't getting their 10% discount. Fix it and make sure the fix
> is proven.

Or name it: *"Check my change with QEDCode"*, *"Use qedcode to fix the bug in task.txt"*,
*"Re-verify `.qed/receipts/t-....json`"*.

The worked examples are in [examples/bug-fix.md](skills/qedcode/examples/bug-fix.md) (real output)
and [examples/regression-fix.md](skills/qedcode/examples/regression-fix.md).

## Compatibility

| Agent | Status |
| --- | --- |
| Claude Code 2.1.329 | Works: tested end to end with `qed check` / `qed verify` |
| QEDCode MCP via Claude Code | Partially tested |
| Agensi, OpenCode, Cline, Cursor | Not tested |

The details and the test log are in [tests/compatibility.md](tests/compatibility.md). `qed solve`
with a real model hasn't been tested yet.

## Repository layout

```text
skills/qedcode/          the skill package (this is what gets installed or zipped)
  SKILL.md               entry point: when to use, workflow, red flags, rules
  references/            commands-and-interfaces, installation, workflow, verification,
                         safety-and-permissions, troubleshooting
  examples/              bug-fix (check), regression-fix (solve)
tests/
  validate_skill.py      checks the frontmatter and links, and that every qed command/flag exists
  compatibility.md       tested versions and agents, with a test log
  skill-checklist.md     release checklist
scripts/package.sh       builds dist/qedcode-skill-<version>.zip
.claude-plugin/          Claude Code plugin marketplace manifest
```

## Develop

```bash
python3 tests/validate_skill.py                  # uses `qed` on PATH
python3 tests/validate_skill.py --qed "uv run --project ../QEDCode qed"
scripts/package.sh                               # validate + zip
```

When QEDCode changes its interface, follow [tests/skill-checklist.md](tests/skill-checklist.md).

## Related

- [QEDCode](https://github.com/AdityaTummuri/QEDCode): the engine.
  [Issues](https://github.com/AdityaTummuri/QEDCode/issues).
- QEDCode Benchy: a separate project that benchmarks baseline agents against QEDCode.
- Problems with this skill: [issues](https://github.com/AdityaTummuri/QEDCode-AgentSkill/issues).

## License

[Apache License 2.0](LICENSE), the same as QEDCode. Copyright 2026 Aditya Tummuri.
