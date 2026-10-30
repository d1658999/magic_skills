# Surgical Correction Directive

> **From**: Lead Orchestrator & Audit Council  
> **To**: [Subagent ID / Conversation ID / Copilot Session UUID]  
> **Work Packet**: [WP-ID]  
> **Current Attempt**: [Attempt # / 3]  
> **Status**: REASSIGNED_FOR_CORRECTION  

---

## 1. Failed Council Gate(s)

Your deliverable failed the Council Audit on the following gate(s):

- [ ] **Gate 1: Scope & Boundary Violation** (Modified files outside allowed set)
- [ ] **Gate 2: Spec Compliance & Anti-Slop** (Contains TODOs, stubs, or missing methods)
- [ ] **Gate 3: Functional RTM Failure** (Failing functional requirement or missing alternate branch)
- [ ] **Gate 4: Adversarial Corner-Case Defect** (Crashes on boundary values or anti-cheat violation)
- [ ] **Gate 5: Staff Code Quality** (Concurrency race, resource leak, or performance regression)
- [ ] **Gate 6: AppSec / Vulnerability** (Security hazard, injection, or BOLA violation)

---

## 2. Exact Defect Diagnostics

### Defect 1: [Short Title]
- **Location**: `path/to/file.ts:L45-L62`
- **Observed Behavior**: [Explain what the code currently does that is wrong]
- **Required Invariant**: [Explain what the specification requires]
- **Exploit / Failure Trace**:
  ```
  [Insert terminal error, stack trace, or failing test output]
  ```

---

## 3. Drop-In Hardened Replacement Code

Replace the defective block with the following verified implementation:

```typescript
// DROP-IN REPLACEMENT: Replace path/to/file.ts lines 45-62 with:
export function safeMethod(param: ValidatedInput): SafeOutput {
  if (!param || typeof param.id !== "string" || param.id.trim() === "") {
    throw new InvalidParameterError("Parameter id must be a non-empty string");
  }
  // Robust implementation handling boundary values
  return executeSafeLogic(param);
}
```

---

## 4. Re-Verification & Anti-Cheat Mandate

Before reporting completion:
1. Do **NOT** modify or delete existing test assertions to bypass this check.
2. Run the exact verification command:
   ```bash
   [Exact Shell Verification Command]
   ```
3. Verify that the command exits with code `0`.
4. Reply with your updated Completion Report confirming:
   - Modified file paths.
   - Exact command output showing tests passed.
   - Confirmation of zero out-of-scope modifications.
