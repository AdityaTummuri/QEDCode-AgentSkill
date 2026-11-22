<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img src="assets/logo-light.svg" alt="QEDCode" width="300">
  </picture>
</p>

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
   - a weakened test is grade C ("tests weakened in ...") on current QEDCode, but only B on the
     0.1.0 release commit, so the agent reads the test diff itself;
   - a missing pytest shows up as grade C "tests could not run" (older builds: "no tests ran");
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

**Or as a plain skill:** copy or symlink the `skills/qedcode` folder into the folder your agent
reads skills from:

```bash
git clone https://github.com/AdityaTummuri/QEDCode-AgentSkill
ln -s "$PWD/QEDCode-AgentSkill/skills/qedcode" ~/.claude/skills/qedcode          # all projects
# or: ln -s ... <project>/.claude/skills/qedcode                                   # one project
```

| Agent | All projects | One project |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/qedcode` | `<project>/.claude/skills/qedcode` |
| Google Antigravity (IDE and `agy`) | `~/.gemini/config/skills/qedcode` | `<project>/.agents/skills/qedcode` |
| VS Code (Copilot agent mode) | `~/.copilot/skills/qedcode` | `<project>/.github/skills/qedcode` |

VS Code also reads `.claude/skills` and `.agents/skills`, so one copy can serve several agents.
On Windows, copy the folder instead of linking it. The folder must stay named `qedcode`, the same
as the skill's `name` (VS Code silently skips a skill whose folder name differs).

**Connect QEDCode's MCP server too** (the skill works with the CLI or MCP, and inside an IDE MCP is
the usual route):

```bash
qed connect antigravity        # Antigravity IDE + agy (QEDCode commit 50a45de or later)
qed connect vscode             # VS Code, through `code --add-mcp` (same commit or later)
qed connect                    # every agent found: Claude Code, OpenCode, Cline, Cursor, ...
claude mcp add qedcode -- qed mcp   # Claude Code by hand
```

### Using it from Antigravity or VS Code with a cloud model

No GPU is needed. The IDE's agent runs on the IDE's own cloud model, `qed check` and `qed verify`
need no model, and `qed solve` can use a cloud model:

1. `uv tool install git+https://github.com/AdityaTummuri/QEDCode`
2. `qed setup`: choose **cloud**, pick a provider and model, and paste the API key. It goes into
   the system keychain. Don't put it in an MCP `env` block: an IDE started from the Dock or Start
   menu doesn't see your shell's environment variables, and keys don't belong in config files.
3. `qed connect antigravity` or `qed connect vscode`, then install the skill (table above).
4. Restart the IDE's agent. In Antigravity: agent panel → **…** → MCP Servers, check that
   `qedcode` is listed. In VS Code: open the chat in Agent mode and look in the tools list.
5. Ask: *"Customers who spend exactly 100 aren't getting their discount. Fix it and prove it."*

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
| Claude Code 2.1.329, CLI | Works: tested end to end with `qed check` / `qed verify`, and without QEDCode installed |
| Claude Code 2.1.329, QEDCode MCP | Works: tested end to end with `mcp__qedcode__check` / `verify` |
| Antigravity (`agy` 1.5.13) | Works: 4 of 4 bug-zoo projects reached grade A, VERIFIED, with hidden tests passing, from prompts that don't mention QEDCode; 2 of 2 again with QEDCode reachable only over MCP |
| VS Code | Not tested (no VS Code on the test machine); install paths taken from the VS Code docs |
| Agensi, OpenCode, Cline, Cursor | Not tested |

The details and the test log are in [tests/compatibility.md](tests/compatibility.md). `qed solve`
was run end to end with QEDCode's scripted stand-in model. How it does with a **real** model is
measured by `tests/run_solve_smoke.py` (below), which hasn't yet been run on a machine with a model.

## Repository layout

```text
skills/qedcode/          the skill package (this is what gets installed or zipped)
  SKILL.md               entry point: when to use, workflow, red flags, rules
  references/            commands-and-interfaces, installation, workflow, verification,
                         safety-and-permissions, troubleshooting
  examples/              bug-fix (check), regression-fix (solve)
tests/
  validate_skill.py      checks the frontmatter and links, and that every qed command/flag exists
  check_contract.py      runs real qed check / verify: the grades, exit codes and JSON fields
                         the skill documents still hold (no model)
  run_solve_smoke.py     real-model qed solve test over QEDCode's bug zoo, with hidden tests
  run_ide_smoke.py       agent test inside Antigravity (agy): skill + MCP per workspace, then
                         qed verify and the hidden tests on what the agent did
  compatibility.md       tested versions and agents, with a test log
  skill-checklist.md     release checklist
scripts/package.sh       builds dist/qedcode-skill-<version>.zip
marketplace/             Agensi listing draft (copy, tags, reviewer notes)
.claude-plugin/          Claude Code plugin marketplace manifest
.github/workflows/       sync-with-qedcode: validate + contract test against QEDCode main,
                         on every push and once a week
```

## Develop

```bash
python3 tests/validate_skill.py                  # uses `qed` on PATH
python3 tests/validate_skill.py --qed "uv run --project ../QEDCode qed"
python3 tests/check_contract.py --zoo ../QEDCode/bugzoo   # real qed check/verify, no model
scripts/package.sh                               # validate + zip
```

### Antigravity agent test (needs `agy`, signed in: run `agy` once by itself)

```bash
python3 tests/run_ide_smoke.py --zoo ../QEDCode/bugzoo --only 002
python3 tests/run_ide_smoke.py --zoo ../QEDCode/bugzoo --only 002 010 --mcp-only   # MCP route only
```

The script puts the skill and the `qedcode` MCP server in each test workspace's `.agents/`
folder (your global Antigravity settings are untouched). It runs `agy -p` with the bug report,
then re-runs any receipt with `qed verify` and runs the hidden tests on what the agent did.

### Real-model test (needs `qed setup` done; takes minutes per project)

```bash
git clone https://github.com/AdityaTummuri/QEDCode            # for its bugzoo/ folder
python3 tests/run_solve_smoke.py --zoo QEDCode/bugzoo --report solve-report.md
python3 tests/run_solve_smoke.py --zoo QEDCode/bugzoo --only 001 002 --speed fast
```

The script copies each bug-zoo project into a temporary git repo and runs `qed solve` from its
plain-language task. It checks the receipt with `qed verify`, applies the result, and runs the
project's **hidden** tests, which QEDCode never saw. The result is a Markdown table for
[tests/compatibility.md](tests/compatibility.md). The bug zoo itself is never modified.

When QEDCode changes its interface, follow [tests/skill-checklist.md](tests/skill-checklist.md).

## Related

- [QEDCode](https://github.com/AdityaTummuri/QEDCode): the engine.
  [Issues](https://github.com/AdityaTummuri/QEDCode/issues).
- [QEDCode Benchy](https://github.com/AdityaTummuri/QEDCode-benchy): a separate project that
  benchmarks the same model with and without QEDCode (`qed benchy`).
- Problems with this skill: [issues](https://github.com/AdityaTummuri/QEDCode-AgentSkill/issues).

## License

[Apache License 2.0](LICENSE), the same as QEDCode. Copyright 2026 Aditya Tummuri.
