# Installation (for the user to run)

QEDCode is a separate program. Don't install it, upgrade it or download models without the user's
explicit OK. Show them these commands and let them choose. The source of truth is the
[QEDCode README](https://github.com/AdityaTummuri/QEDCode#install).

## Requirements

| | Required | Notes |
| --- | --- | --- |
| git | yes | The project must be a git repository with at least one commit |
| Python 3.11+ | yes | `uv` manages it |
| [uv](https://docs.astral.sh/uv/) | yes | Installs `qed` as a command-line tool |
| Tests | recommended | pytest, `node --test`, Vitest or Jest. Without tests the best grade is C |
| Node.js 20+ | JS/TS projects only | 22.18+ to run `.ts` tests with the built-in runner. QEDCode never installs Node packages |
| A model | only for `qed solve` | Local (llama.cpp, Ollama, LM Studio; 3–6 GB) or cloud via LiteLLM. `qed check` needs none |
| Docker | optional | Only for the sealed test box (`qed sandbox setup`) |

## Install `qed`

Until a PyPI release exists, install from GitHub:

```bash
uv tool install git+https://github.com/AdityaTummuri/QEDCode
qed --version        # this skill was verified with 0.1.0
```

If `qed: command not found` appears, run `uv tool update-shell` and open a new terminal.

## Optional: set up a model (only needed for `qed solve`)

```bash
qed setup            # interactive: detects hardware, recommends a model, lists every download with its size, asks once
qed doctor           # read-only health check with a fix for each problem
```

`qed setup` is interactive, so the user must run it themselves. In Claude Code they can type
`! qed setup` to run it in the session.

## Optional: connect the MCP server to an agent

```bash
qed connect                              # shows what it will change and asks first
claude mcp add qedcode -- qed mcp        # Claude Code, by hand
```

Restart the agent session afterwards so it loads the `qedcode` tools.

## Make sure the project's tests can run

QEDCode runs tests with the project's own interpreter. It looks, in order, for `<project>/.venv`,
`<project>/venv`, an active `VIRTUAL_ENV`, then `python3`/`python` on PATH. If pytest isn't
installed in that interpreter, no tests run and grades drop to C. For uv projects, `uv sync` in the
project creates `.venv`. For JS/TS projects, run `npm install` (or pnpm/yarn) first.

## Remove

```bash
qed uninstall --all      # removes .qed/ here and ~/.qedcode (engines, models, logs, keys); asks first
uv tool uninstall qedcode
```
