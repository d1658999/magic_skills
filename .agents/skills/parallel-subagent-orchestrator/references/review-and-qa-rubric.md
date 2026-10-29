# Mandatory Review & Quality Assurance Rubric

After subagents finish their tasks, **the Original Agent is 100% accountable for the final quality.** You must never trust a subagent's self-report at face value. Subagents frequently claim success even when they:
- Implemented only 70% of the spec and left `// TODO` for the rest
- Edited files outside their responsibility boundary
- Broke existing tests or mocked out the functionality under test
- Ignored edge cases or error handling

Every subagent deliverable **MUST** pass all 4 Gates below before being marked `APPROVED`.

---

## Gate 1: Responsibility & Scope Boundary Verification

**Goal**: Confirm the subagent did its exact job—no more, no less—without stepping on other tasks.

1. **Inspect Modified Files**:
   - Check the workspace state (`git status --short`, `git diff --name-only`, or directory listing) against the subagent's `Allowed to Create/Modify` list.
   - **Immediate Fail Condition**: The subagent modified any file in the `Forbidden` list or touched another subagent's files.
   - **Remediation**: Revert unauthorized edits immediately and reassign the subagent (or fix the boundary violation).
2. **Verify Responsibility Completeness**:
   - Check every deliverable file listed in the Work Packet.
   - Did the subagent create all required files (including test files)?
   - Did the subagent fulfill the core responsibility of its task rather than pushing complex logic to the caller?

---

## Gate 2: Spec Compliance & Anti-Slop Inspection

**Goal**: Confirm every detail of the specification was implemented faithfully with zero placeholders or shortcuts.

1. **Read Every Line of New/Changed Code**:
   - Use `read_file` on every file created or modified by the subagent. **Never approve a file without reading it.**
2. **Signature & Contract Match**:
   - Compare exported function/class/type names, parameter orders, parameter types, and return types against Section 3 of the Work Packet.
   - Even a minor naming mismatch (e.g., `userId` vs `user_id`, or default export vs named export) will break integration with parallel tasks.
3. **Edge-Case & Error-Handling Check**:
   - Walk through each item in Section 5 (Edge-Case Matrix) of the Work Packet and locate the exact lines of code that handle it.
4. **Anti-Slop Scan (Zero Tolerance)**:
   - Scan all target files (or run [scripts/validate_work_packet.py](../scripts/validate_work_packet.py)) for:
     - `TODO`, `FIXME`, `XXX`, `HACK`, `placeholder`, `not implemented`
     - Empty catch blocks (`catch (e) {}`, `except Exception: pass`)
     - Type evasions (`any`, `@ts-ignore`, `@ts-expect-error`, `# type: ignore`, `unsafe` without justification)
     - Fake tests (e.g., `expect(true).toBe(true)`, tests with no assertions, or tests that mock the exact function they are supposed to test)

---

## Gate 3: Code Quality & Engineering Excellence Audit

**Goal**: Ensure the code reads as if written by a principal engineer on the team.

1. **Architectural & Idiomatic Fit**:
   - Does the code follow the exact conventions, naming style, and directory structure of the surrounding codebase?
   - Are imports clean, sorted, and free of unused dependencies?
2. **Logic & Correctness Deep-Dive**:
   - Trace the execution flow with sample inputs:
     - Normal input
     - Empty/zero input
     - Malformed/error input
   - Check for off-by-one errors, mutation of shared input objects, unhandled promise rejections, memory/resource leaks, and security issues (injection, unvalidated input, hardcoded secrets).
3. **Documentation Integrity**:
   - Were existing comments and docstrings preserved?
   - Do new public functions/classes have clear, accurate docstrings/comments explaining parameters, return values, and error conditions?

---

## Gate 4: Independent Verification Execution

**Goal**: Prove empirically that the deliverable builds, passes static analysis, and passes all tests.

1. **Run Verification Commands Directly**:
   - Execute the linter, type-checker, and unit test suite for the subagent's module via `run_command`.
   - Do **not** skip this step just because the subagent pasted test output in its message—another parallel subagent may have finished afterward, or the subagent may have run the wrong command.
2. **Verify Test Coverage of Spec**:
   - Check that the test runner actually executed the new test cases and that none are marked `.skip` or `xit`.

---

## Scoring & Decision Rule

Use [templates/review-scorecard.md](../templates/review-scorecard.md) to evaluate the subagent:

- **PASS (`APPROVED`)**: Passes Gate 1, Gate 2, Gate 3, and Gate 4 with **zero** defects.
- **FAIL (`REASSIGNED`)**: Any gate has one or more defects, missing edge cases, scope violations, or quality issues. Proceed immediately to the [Reassignment Protocol](./reassignment-protocol.md).
