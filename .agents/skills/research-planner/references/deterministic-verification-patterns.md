# Deterministic Verification Patterns

> **Reference Purpose**: Engineering patterns for designing objective, unambiguous verification commands and automated gates that lower-tier models and orchestrators can execute to prove correctness with zero subjective human or AI judgment.

---

## 1. The Fallacy of AI Self-Assessment

When lower-tier or small-parameter AI models are asked: *"Did you complete the task and does it work?"*, their autoregressive generation almost invariably outputs:
> *"Yes, I have implemented all requirements and verified that the solution works properly."*

This is **pure token sequence completion**, not an empirical finding. The model has no internal runtime or compiler.
To guarantee code quality, every task must be accompanied by **deterministic, machine-executable verification commands**.

---

## 2. The 3-Tier Verification Gate

Every atomic task packet should specify verification across three distinct tiers:

```
Tier 1: Static Type & Syntax Gate (Does it compile?)
   │
   ▼
Tier 2: Targeted Unit Test Gate (Does the logic work?)
   │
   ▼
Tier 3: Anti-Slop & Scope Gate (Did it leave placeholders or touch forbidden files?)
```

---

### Tier 1: Static Type & Syntax Gate
Ensures syntax validity, correct imports, and strict type safety before running tests.

#### TypeScript / JavaScript:
```bash
# Typecheck without emitting JS files (fast, catches broken interfaces)
npx tsc --noEmit
```

#### Python:
```bash
# Strict typechecking on modified file
python -m mypy --strict src/services/token_service.py

# Syntax and basic linter check
python -m flake8 src/services/token_service.py
```

#### Go:
```bash
go vet ./...
go build ./...
```

#### Rust:
```bash
cargo check --quiet
```

---

### Tier 2: Targeted Unit Test Gate
**Never run the entire project's test suite for a micro-task.** Large test suites are slow, may have unrelated flakiness, and overwhelm small models with hundreds of lines of irrelevant logs.

Instead, craft a **surgical test command** targeting only the single test file or specific test case created or affected by the task:

#### Jest / Vitest (Node.js):
```bash
# Run ONLY the test file related to the task
npm test -- src/services/__tests__/token-validator.test.ts

# Or target a specific test case name:
npm test -- src/services/__tests__/token-validator.test.ts -t "valid token"
```

#### Pytest (Python):
```bash
# Run ONLY the targeted test file
pytest tests/unit/test_token_validator.py -v

# Or target a specific test function:
pytest tests/unit/test_token_validator.py::test_verify_token_expired -v
```

#### Go Test:
```bash
go test -v ./internal/auth/ -run TestTokenValidator
```

---

### Tier 3: Anti-Slop & Scope Gate
Ensures the model did not leave forbidden markers or modify out-of-scope files.

#### Automated Anti-Slop Scan (PowerShell):
```powershell
# Scan target file for forbidden placeholder tokens:
Select-String -Path "src/services/token-validator.ts" -Pattern "\b(TODO|FIXME|HACK|XXX)\b|@ts-ignore|as any"
# (Expectation: Output should be EMPTY)
```

#### Automated Anti-Slop Scan (Python / Shell):
```bash
# Run the skill's built-in audit script:
python .agents/skills/research-planner/scripts/validate_spec.py --mode audit --allowed-files src/services/token-validator.ts
```

#### Git Scope Check (Verify only authorized files were modified):
```bash
git status --porcelain
# (Expectation: Only authorized target files appear in output)
```

---

## 3. Formatting Verification Directives in Task Packets

When including verification commands in task packets, always use this explicit format:

```markdown
### Verification Command
Run the following command in your terminal:
```bash
[EXACT_SHELL_COMMAND]
```

### Acceptance Criteria:
- **Exit Code**: Must be `0` (Zero).
- **Required Output Pattern**: Must contain `[e.g., 'PASS src/services/__tests__/token.test.ts']`.
- **Prohibited Output**: Must NOT contain `FAIL`, `Error`, or `TODO`.
- **Action on Non-Zero Exit**: If the command fails, read the terminal error message, correct the mistake in the target file, and rerun the command until it passes.
```
