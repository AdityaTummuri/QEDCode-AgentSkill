# QEDCode Agent Skill — Project Plan

**Status:** Proposed  
**Project type:** Portable AI-agent skill / instruction package  
**Core engine:** [QEDCode](https://github.com/AdityaTummuri/QEDCode)  
**Proposed repository:** `QEDCode-Agent-Skill`  
**Related project:** QEDCode Benchy (separate benchmarking project)

---

## 1. Purpose

QEDCode Agent Skill makes it easier for compatible AI coding agents to discover, understand, and correctly use QEDCode.

It is an instruction package that teaches an agent:

- What QEDCode does.
- When QEDCode is useful.
- How to check whether QEDCode is installed and available.
- How to invoke its actual supported interfaces.
- How to inspect, validate, and explain QEDCode results.
- How to avoid unsafe or unnecessary operations.

**It is not a replacement for QEDCode.** It must not duplicate the engine, bundle a copy of its source code, or pretend to provide capabilities that QEDCode does not expose.

## 2. Repositories and responsibilities

### QEDCode — core engine

Repository: https://github.com/AdityaTummuri/QEDCode

Owns:

- Candidate generation and code-fix workflow.
- Safe-copy or isolated execution mechanisms.
- Verification and testing capabilities.
- CLI, TUI, MCP, and other supported interfaces.
- Core installation and release process.

### QEDCode Agent Skill — adoption layer

Owns:

- Portable skill instructions.
- Agent-facing usage guidance.
- Compatibility and installation documentation.
- Examples and troubleshooting.
- Packaging for skill distribution platforms.

### QEDCode Benchy — measurement layer

Owns:

- Baseline-versus-QEDCode benchmark runs.
- Independent evaluation.
- Local benchmark reports.
- Optional community result submissions.
- Public benchmark statistics.

Keep these repositories separate. Link between them, but avoid duplicated implementation or conflicting documentation.

---

## 3. Target users and environments

Target users are developers who already use AI coding agents and want those agents to make use of QEDCode.

Potential environments include:

- Claude Code and other environments that support compatible skill packages.
- Skill marketplaces and distribution platforms such as Agensi, subject to their current package requirements.
- Other compatible coding-agent tools as support is tested.

Do not claim universal compatibility. Maintain a compatibility table based on actual testing.

---

## 4. Core design principles

1. **Instruction-only package:** The skill explains how to use QEDCode; the engine remains installed separately.
2. **Grounded instructions:** Every command, flag, file path, and interface must be verified against the current QEDCode release.
3. **No invented capabilities:** Never document commands or behaviour that do not exist.
4. **User control:** Do not run destructive operations, overwrite files, or change project state without the permissions and confirmation required by the host agent and QEDCode.
5. **Safe execution:** Follow QEDCode's actual isolation and verification guarantees. Do not claim stronger guarantees than the implementation provides.
6. **Graceful fallback:** If QEDCode is unavailable or incompatible, explain that and continue with the agent's normal workflow where appropriate.
7. **Version awareness:** Document the minimum supported QEDCode version and update the skill when interfaces change.
8. **Small and maintainable:** Keep the main skill file concise; put detailed reference material in separate files.

---

## 5. Skill behaviour

The skill should guide an agent through this workflow.

### Step 1 — Understand the task

The agent identifies whether the task is suitable for QEDCode, such as:

- Debugging a reproducible bug.
- Finding and fixing a regression.
- Exploring candidate fixes for a failing test.
- Validating a proposed change.

The skill should also describe cases where QEDCode may not be appropriate, such as simple documentation edits or tasks outside its supported capabilities.

### Step 2 — Check availability

The agent checks whether QEDCode is installed and whether the available version and interface are supported.

If unavailable:

- Explain the missing dependency.
- Provide the documented installation route.
- Do not silently install software or change system configuration unless the user has authorized it.

### Step 3 — Inspect the project

The agent identifies the relevant repository, task context, tests, and constraints.

It should preserve existing user changes and follow the project's conventions.

### Step 4 — Invoke QEDCode

The skill tells the agent how to use QEDCode's real supported interface.

Before writing these instructions, inspect the QEDCode repository and verify:

- Actual command names and flags.
- Input and output formats.
- Supported operating systems and runtimes.
- CLI versus MCP behaviour.
- Error handling and exit codes.
- Safety, isolation, and file-modification behaviour.

Do not assume that a proposed command exists.

### Step 5 — Inspect and verify results

The agent should:

- Read the generated candidates and their explanations.
- Inspect the actual diff.
- Run relevant tests and checks.
- Check for regressions.
- Report failed or inconclusive verification honestly.
- Avoid claiming success merely because QEDCode generated a candidate.

### Step 6 — Report to the user

The agent gives a concise summary:

- What QEDCode was asked to do.
- Which candidate or change was selected.
- Which files changed.
- Which tests were run and their outcomes.
- What remains uncertain or unverified.

The agent must not hide failed tests or fabricate verification results.

---

## 6. Proposed repository structure

```text
QEDCode-Agent-Skill/
├── README.md
├── SKILL.md
├── LICENSE
├── CHANGELOG.md
├── references/
│   ├── installation.md
│   ├── workflow.md
│   ├── commands-and-interfaces.md
│   ├── safety-and-permissions.md
│   ├── verification.md
│   └── troubleshooting.md
├── examples/
│   ├── bug-fix.md
│   └── regression-fix.md
└── tests/
    ├── skill-checklist.md
    └── compatibility.md
```

This is a proposed layout. Follow the target platform's required skill-package format; do not add unnecessary files if the platform requires a smaller package.

### `SKILL.md`

The main entry point. Keep it concise and include:

- Skill name and short description in the format required by the target platform.
- When the skill should activate.
- A short QEDCode workflow.
- Safety and verification requirements.
- Links or references to supporting documentation.

### `README.md`

Explain:

- What the skill does.
- What QEDCode is.
- Requirements and installation.
- Supported agent environments.
- Usage examples.
- Links to the core engine and issue tracker.

### `references/`

Detailed guidance for installation, real commands, safety, verification, and troubleshooting.

### `examples/`

Short realistic examples showing how an agent should use QEDCode. Examples must be based on verified interfaces and must not imply guaranteed success.

---

## 7. Packaging and distribution

The skill should be easy to distribute without requiring users to clone or build the QEDCode engine from this repository.

Distribution process:

1. Keep the source package in the public GitHub repository.
2. Validate the skill's required file structure.
3. Test the package in each supported agent environment.
4. Build a ZIP or other package format required by the target marketplace.
5. Publish a versioned release.
6. Submit the package to Agensi or other compatible distribution platforms, following their current rules.
7. Keep the marketplace listing linked to the original QEDCode repository and clearly attribute the creator.

The skill package should contain instructions and references, not a bundled copy of QEDCode's engine.

Before publishing to any marketplace, verify its current requirements, supported file formats, licence rules, and restrictions.

---

## 8. Licensing and attribution

Choose a licence for the skill repository deliberately and ensure it is compatible with all included content and dependencies.

The skill is a separate instruction package. It should clearly state that QEDCode is a separate project and link to its repository.

Suggested attribution:

> QEDCode Agent Skill is an integration guide for [QEDCode](https://github.com/AdityaTummuri/QEDCode), an open-source coding engine created by Aditya Tummuri.

Do not imply that the skill is an official integration for a third-party agent platform unless that relationship has been established.

---

## 9. Quality and compatibility testing

Before release, test the skill with real supported agent environments.

Check that:

- The agent recognises when the skill is relevant.
- The instructions point to real QEDCode commands and interfaces.
- The agent can detect missing or incompatible QEDCode installations.
- It does not invent commands or flags.
- It preserves existing user changes.
- It inspects diffs before reporting completion.
- It runs appropriate verification.
- It reports failures and uncertainty honestly.
- It does not claim QEDCode guarantees that have not been tested.
- The package installs and loads correctly on each listed platform.

Maintain a compatibility table:

| Agent / platform | Tested version | Status | Notes |
|---|---|---|---|
| Claude Code | To be tested | Not tested | Verify skill loading and invocation |
| Agensi | To be tested | Not tested | Verify current ZIP/package requirements |
| Other compatible agents | To be tested | Not tested | Add only after successful testing |

---

## 10. Versioning and maintenance

Use versioned releases.

When QEDCode changes:

1. Review release notes and interface changes.
2. Check whether skill instructions are affected.
3. Update command and workflow references.
4. Run compatibility tests.
5. Update the compatibility table and changelog.
6. Publish a new skill release if needed.

Document the minimum supported QEDCode version. Avoid claiming compatibility with untested versions.

---

## 11. Implementation milestones

### Milestone 1 — Audit QEDCode

- Inspect the current repository and README.
- Identify actual supported commands and interfaces.
- Confirm installation and runtime requirements.
- Document safety and verification behaviour.
- Identify unsupported or unstable features.

**Deliverable:** Verified QEDCode interface and capability notes.

### Milestone 2 — Build the first skill

- Create `SKILL.md`.
- Add a concise README.
- Add installation, workflow, safety, and verification references.
- Add one bug-fix example.
- Ensure every instruction matches the audited engine.

**Deliverable:** Minimal usable skill package.

### Milestone 3 — Test with an actual coding agent

- Install the skill in a supported agent.
- Give it a real, controlled coding task.
- Observe whether it selects QEDCode appropriately.
- Check command accuracy, diff inspection, and verification.
- Fix confusing or incorrect instructions.

**Deliverable:** Tested skill version with recorded compatibility.

### Milestone 4 — Package and publish

- Validate package structure.
- Create a versioned ZIP/release.
- Publish the GitHub repository.
- Prepare the Agensi listing.
- Include creator attribution and the QEDCode repository link.
- Verify the published package can be installed and used.

**Deliverable:** Public skill package.

### Milestone 5 — Maintain adoption

- Track issues and compatibility reports.
- Update the skill alongside relevant QEDCode releases.
- Add tested agent integrations.
- Improve examples based on actual usage.
- Link users to QEDCode documentation and Benchy for evaluation.

**Deliverable:** Maintained, versioned integration package.

---

## 12. Non-negotiable rules

1. The skill must not duplicate QEDCode's engine.
2. The skill must not invent commands or capabilities.
3. It must not silently install software or make destructive changes.
4. It must preserve user changes and inspect generated diffs.
5. It must report verification outcomes honestly.
6. It must document compatibility only after testing.
7. It must link prominently to the original QEDCode repository.
8. It must remain independently versioned and distributable.
9. It must not claim endorsement by third-party platforms without authorization.

---

## 13. First thing to build

Start with the QEDCode audit—not the marketplace listing.

Inspect the actual QEDCode implementation and document its supported installation methods, commands, interfaces, outputs, and safety guarantees. Then write a small `SKILL.md` that teaches one compatible coding agent to use one verified QEDCode workflow correctly.

Prove that workflow works before expanding the skill to more agents or publishing it widely.
