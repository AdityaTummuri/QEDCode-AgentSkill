# Release checklist

Run before every release, and whenever QEDCode changes its CLI or MCP interface.

## Automated

- [ ] `python3 tests/validate_skill.py --qed "qed"` passes. It checks the frontmatter, the
      SKILL.md length and every link, and that every `qed <command>` / `--flag` in the package
      exists in the installed QEDCode
- [ ] `scripts/package.sh` builds `dist/qedcode-skill-<version>.zip`, and the ZIP contains only
      `qedcode/SKILL.md`, `qedcode/references/*` and `qedcode/examples/*`

## Against the QEDCode release

- [ ] `qed --version` matches the version named in SKILL.md and compatibility.md
- [ ] Read QEDCode's CHANGELOG since the last verified commit, especially changes to `cli.py`,
      `mcp_server.py`, `engine/api.py` and `models/schemas.py`
- [ ] Re-run the audit scenarios in compatibility.md (bug-zoo 001: correct, wrong, syntax error,
      weakened test, no changes, MCP without `.venv`)

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
- [ ] Record the run in compatibility.md
