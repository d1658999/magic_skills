# Codebase Reconnaissance Playbook

> **Reference Purpose**: Systematic protocol for conducting deep, ground-truth investigation of an existing software repository before drafting specifications or task packets. Eliminates speculative assumptions.

---

## 1. The Reconnaissance Principle

**Never design in a vacuum.**
A specification written without inspecting the active codebase will invariably mandate incorrect import paths, conflict with existing naming patterns, use mismatched dependency versions, or require commands that fail in the user's shell environment.

The Research Planner **MUST** gather empirical evidence directly from the workspace files before writing a single task specification.

---

## 2. The 6-Step Reconnaissance Protocol

```
Step 1: Manifest & Tooling Discovery
   │
   ▼
Step 2: Architecture & Entry Point Mapping
   │
   ▼
Step 3: Type & Data Model Extraction
   │
   ▼
Step 4: Idiomatic Pattern Harvesting (Exemplars)
   │
   ▼
Step 5: Test Harness Verification (Dry Run)
   │
   ▼
Step 6: Environmental & Shell Constraints Check
```

---

### Step 1: Manifest & Dependency Lock Inspection
Examine the package or environment descriptor:
- **Node.js**: Read `package.json` and check `dependencies`, `devDependencies`, and `scripts`.
- **Python**: Read `pyproject.toml`, `requirements.txt`, or `setup.cfg`.
- **Go**: Read `go.mod`.
- **Rust**: Read `Cargo.toml`.

#### What to Extract:
1. Exact package names and major versions for relevant libraries (e.g., `fastify: 4.x`, `zod: 3.x`).
2. Module system: CommonJS (`require`) vs ESM (`import / export`).
3. Registered script commands: Check `scripts` for `build`, `lint`, `typecheck`, `test`.

---

### Step 2: Architecture & Entry Point Mapping
Locate where the application starts and how files are structured:
1. Locate the entry point (e.g., `src/index.ts`, `src/main.py`, `cmd/server/main.go`).
2. Map the directory hierarchy:
   - Where do domain types live? (`src/types/`, `src/models/`, `src/schemas/`)
   - Where do business services live? (`src/services/`, `src/core/`, `src/domain/`)
   - Where do controllers/routes live? (`src/routes/`, `src/controllers/`, `src/api/`)
   - Where do tests live? (Co-located `__tests__/` vs separate `tests/` directory)

---

### Step 3: Type & Data Model Extraction
Before asking any executor to write new functions, locate and read existing interfaces:
1. Open the primary type definition files.
2. Note how identifiers are formatted (`camelCase`, `snake_case`, `PascalCase`).
3. Note how errors and results are represented:
   - Does the codebase throw custom Error classes?
   - Or does it return Result tuples/objects (e.g., `{ ok: true, value } | { ok: false, error }`)?

---

### Step 4: Idiomatic Pattern Harvesting (Exemplars)
Find 1–2 mature, well-tested files in the project that represent the "gold standard" for:
1. **Error Handling**: How are exceptions caught, logged, and re-thrown or formatted for HTTP responses?
2. **Dependency Injection / Configuration**: How do services access configuration, database connections, or loggers?
3. **Async / Concurrency**: Are promises handled with `async/await`, explicit `.then()`, or reactive streams?

> **Action**: Copy a 15–25 line representative snippet from an exemplar file. You will paste this directly into the task packet's "Reference Exemplar" section.

---

### Step 5: Test Harness Verification (Live Dry Run)
Never specify a test command in a task packet without verifying it runs in the current environment:
1. Find an existing unit test file (e.g., `npm test -- path/to/existing.test.ts` or `pytest tests/test_health.py`).
2. Run the command using `run_command`.
3. Verify:
   - Does the test runner execute cleanly?
   - What is the exact command syntax needed to run a single test file or test case?
   - What does the success output look like?

---

### Step 6: Environmental & Shell Constraints Check
Determine the runtime environment of the workspace:
1. **Operating System**: Windows (PowerShell/cmd) vs Linux/macOS (bash/zsh).
   - On Windows: Use backslashes or normalized forward slashes in tools, avoid bash-specific commands like `export`, `cat`, or `grep`.
2. **Path Separators**: Ensure instructions tell executors whether paths should use `/` or `\`.
3. **Sandbox Restrictions**: Is network access disabled? If so, verify all necessary packages are already in `node_modules` or local virtualenv.

---

## 3. Reconnaissance Checklist for Planners

Before proceeding to Phase 3 (Architecture & Spec), check off all items:

- [ ] Read primary package manifest and verified exact library versions.
- [ ] Confirmed ESM vs CommonJS / module import style.
- [ ] Inspected existing domain types and error handling conventions.
- [ ] Identified and tested the exact single-test execution command.
- [ ] Located 1–2 gold-standard code exemplars to paste into task packets.
- [ ] Verified OS / shell compatibility (e.g., pwsh commands for Windows).
