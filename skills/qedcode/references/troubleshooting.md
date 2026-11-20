# Troubleshooting

| Symptom | Cause | What to do |
| --- | --- | --- |
| `qed: command not found` | Not installed, or the uv tool dir isn't on PATH | Tell the user (installation.md). After installing: `uv tool update-shell`, new terminal |
| No `mcp__qedcode__*` tools | MCP server not registered, or the session started before it was | Use the CLI instead, or ask the user to run `qed connect` and restart the session |
| Antigravity / VS Code shows no `qedcode` tools, or the server fails to start | Not registered, or the IDE (started from the Dock or Start menu) can't find `qed` on its PATH | The user runs `qed connect antigravity` / `qed connect vscode`, which write the absolute path of `qed`. Then refresh MCP Servers (Antigravity) or reload the window (VS Code) |
| `solve` in an IDE: `No cloud model is set` or a provider key error | Cloud mode not set up, or the key exists only as a shell variable the IDE can't see | The user runs `qed setup`, chooses cloud and saves the key (system keychain). `check`/`verify` need no model meanwhile |
| **Grade C · "tests could not run: ..."** (`8824706`: "no tests ran") in a project that has tests | The interpreter QEDCode chose has no pytest. It picks `.venv/`, `venv/`, `VIRTUAL_ENV`, then `python3` on PATH. Common over MCP, where no virtualenv is inherited | Read `notes` ("Using the detected Python (...)"; MCP returns them from `005c8d2` on, otherwise run `qed check --json` from the CLI). With the user's OK, create `<project>/.venv` with the project's deps and pytest (`uv sync`, or `uv venv && uv pip install pytest ...`), then check again |
| `pytest is not installed in <python>` | Same as above | Same. QEDCode's interactive UI offers to install pytest, but an agent run won't |
| Node tests report the runner is missing | `node_modules` not installed | The user runs `npm install` / `pnpm install` / `yarn install`. QEDCode never installs Node packages |
| `This folder is not a git repository` | No git | Don't run `git init` on the user's project without asking |
| `This repository has no commits yet` | Empty repo | Ask the user to make a first commit |
| `Your files are identical to HEAD, so there is nothing to check` (exit 2) | No uncommitted changes | Make the change first, or `qed check --base <older ref>` |
| `solve` exits 2 with `The llama.cpp engine ... is not installed` / `... is not downloaded` / `No cloud model is set` | No model configured | Fall back to writing the fix yourself plus `qed check`. Tell the user that `qed setup` enables `solve` |
| `status: "busy"` / `Another QEDCode task is already running` | One job per project | Wait, or poll `status` with the given `job_id`. A stale lock is taken over automatically once its process has gone |
| MCP `solve` returns `running` and the agent times out | Solves take minutes | Poll `status(job_id)`. The user can raise `MCP_TOOL_TIMEOUT` |
| `qed verify` → `NOT VERIFIED` | Code, base commit or tests changed since the receipt was written | Report the listed mismatches. Don't edit the receipt |
| `qed verify` → `not safe to run here` | The receipt asks for a command other than this project's test command | Only re-run receipts QEDCode wrote in this project |
| `apply`/`undo` → refused | A file it would touch changed since the snapshot | Tell the user. Don't force it. Re-run `solve` on the current code if needed |
| `Something went wrong inside QEDCode` (exit 3) | Internal error | Report it; details are in `~/.qedcode/logs/qedcode.log`. Suggest `qed doctor` |
| A test hangs | Slow or blocking test | The user can lower `test_timeout_seconds` in `.qed/project.toml` |
| Leftovers after a crash | Stale worktrees | `qed doctor` lists them. `git worktree prune` and deleting `.qed/worktrees/` is safe when no job is running |

For anything else, run `qed doctor`. It is read-only and prints a fix for each problem.
