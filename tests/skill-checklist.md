# Release checklist

Run before every release, and whenever QEDCode changes its CLI or MCP interface.

## Automated

- [ ] `python3 tests/validate_skill.py --qed "qed"` passes. It checks the frontmatter, the
      SKILL.md length and every link, and that every `qed <command>` / `--flag` in the package
      exists in the installed QEDCode
- [ ] `python3 tests/check_contract.py --zoo <QEDCode>/bugzoo` passes (real `qed check` and
      `qed verify`: grades, exit codes and JSON fields as documented)
- [ ] The `sync-with-qedcode` workflow is green on `main` (it also runs weekly against QEDCode main)
- [ ] `scripts/package.sh` builds `dist/qedcode-skill-<version>.zip`, and the ZIP contains only
      `qedcode/SKILL.md`, `qedcode/references/*` and `qedcode/examples/*`

## Against the QEDCode release

- [ ] `qed --version` matches the version named in SKILL.md and compatibility.md
- [ ] Read QEDCode's CHANGELOG since the last verified commit, especially changes to `cli.py`,
      `mcp_server.py`, `engine/api.py` and `models/schemas.py`
- [ ] Re-run the audit scenarios in compatibility.md (bug-zoo 001: correct, wrong, syntax error,
      weakened test, no changes, MCP without `.venv`)

## With a real model (a computer where `qed setup` is done)

- [ ] `python3 tests/run_solve_smoke.py --zoo <QEDCode>/bugzoo --report solve-report.md` and paste
      the table into compatibility.md. Watch the hidden-tests column: it's the independent check
- [ ] Repeat with `--speed fast` and `--speed sure` if timing matters

## With a real agent (fresh session, skill installed, prompt doesn't mention QEDCode)

- [ ] The agent recognises the skill as relevant to a bug report in a Python project with tests
- [ ] It checks that `qed` is available, and doesn't install or set anything up unasked
- [ ] It notes pre-existing uncommitted changes and doesn't stash, reset or commit them
- [ ] It uses only real commands and flags
- [ ] It adds the regression test in a new test file and reaches grade A where possible
- [ ] It reads the diff and the summary line, not just the exit code
- [ ] It doesn't `qed apply` a solve result, or pass `--yes`, `--allow-risky` or `apply=true`,
      without consent
- [ ] Its final report includes grade, summary, files, tests, receipt and "not proven" items, and
      hides no failures
- [ ] With `qed` missing from PATH, it explains the dependency and continues normally
- [ ] Over MCP only (`claude -p ... --mcp-config <file> --strict-mcp-config`, no `Bash(qed:*)`),
      it passes `project_dir` and reaches the same result
- [ ] Record the run in compatibility.md

## In an IDE

- [ ] Antigravity (`agy` CLI, signed in): `python3 tests/run_ide_smoke.py --zoo <QEDCode>/bugzoo
      --only 001 002 007 010`, then the same with `--mcp-only`. The hidden-tests column must pass
- [ ] With a model set up (`qed setup`, local or cloud): `tests/run_solve_smoke.py`, and one
      Antigravity run where the prompt asks the agent to let QEDCode generate the fix (`solve`)
- [ ] VS Code: `qed connect vscode`, skill in `.github/skills/qedcode`; in Agent mode the
      `qedcode` tools are listed, and a bug report leads to `check` with grade A
