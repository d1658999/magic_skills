# Subagent Review & Responsibility Audit Scorecard

- **Work Packet ID**: `[WP-ID]`
- **Subagent `conversationId`**: `[conv-id]`
- **Review Iteration**: `[Attempt #1 / #2 / #3]`
- **Files Audited**:
  - `[absolute/path/to/file1]`
  - `[absolute/path/to/test_file1]`

---

## Gate 1: Responsibility & Boundary Check
- [ ] **Exclusive File Scope**: Subagent modified ONLY files listed in `ALLOWED to Create or Modify`.
- [ ] **Zero Collateral Damage**: Shared configs, router files, and other subagents' files are untouched.
- [ ] **Full Responsibility Ownership**: All assigned deliverables exist and no core work was deferred.
- **Gate 1 Result**: `[PASS / FAIL]`

## Gate 2: Spec Compliance & Anti-Slop Check
- [ ] **Full File Inspection**: Lead Agent read every line of all created/modified files via `read_file`.
- [ ] **Exact Contract Match**: All exported names, parameter types, and return types match Section 3 of the Work Packet.
- [ ] **Algorithmic Fidelity**: All numbered steps in Section 4 are implemented accurately.
- [ ] **Edge-Case Coverage**: Every scenario in Section 5 (Edge-Case Matrix) is handled in code.
- [ ] **Zero Slop / Placeholders**: Confirmed zero `TODO`, `FIXME`, `HACK`, stubs, hardcoded mocks, or type suppressions (`any`, `@ts-ignore`, `# noqa`).
- **Gate 2 Result**: `[PASS / FAIL]`

## Gate 3: Code Quality & Craftsmanship Check
- [ ] **Idiomatic Style**: Matches codebase conventions, naming, and formatting.
- [ ] **Logic Soundness**: No off-by-one errors, race conditions, resource leaks, or unhandled errors.
- [ ] **Test Quality**: Unit tests assert real behavior (no fake assertions or skipped tests) and cover all cases from Section 6.
- [ ] **Documentation Integrity**: Existing comments preserved; public symbols documented clearly.
- **Gate 3 Result**: `[PASS / FAIL]`

## Gate 4: Independent Verification Check
- [ ] **Static Analysis**: Lead Agent ran `<lint/typecheck command>` -> Exit Code `0`.
- [ ] **Unit Tests**: Lead Agent ran `<test command>` -> Exit Code `0` (`<N>` tests passed, `0` skipped).
- **Gate 4 Result**: `[PASS / FAIL]`

---

## Final Audit Verdict
- **Overall Status**: `[APPROVED ✅ | REASSIGNED ❌]`
- **Action Taken**:
  - If `APPROVED`: Mark `[WP-ID]` complete in Master Tracker.
  - If `REASSIGNED`: Send Correction Directive to `[conv-id]` via `send_message` with the blocking defects below.

### Blocking Defects (If `REASSIGNED`)
1. **`[Category]`** in `[file:line]`: `<Exact description of defect and required fix>`
2. **`[Category]`** in `[file:line]`: `<Exact description of defect and required fix>`
