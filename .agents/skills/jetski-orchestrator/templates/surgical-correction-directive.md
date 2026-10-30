# SURGICAL CORRECTION DIRECTIVE: <WP-ID> — Attempt <X> of 3

> **Dispatch Mechanism**: `send_message(Recipient="<worker-conversation-id>", Message="...")`  
> **Iteration Counter**: `Attempt <X> of 3 — Circuit Breaker & 2-Strike Fast Escalation Warning`  
> **2-Strike Fast Escalation Rule for Lower-Tier Models**:  
> - If a `flash` / `flash_lite` or literal subagent fails on **Attempt 2** after receiving the literal `Target` / `Replacement` patch blocks below, the Lead Orchestrator will **NOT** waste a 3rd turn arguing with the subagent.  
> - Instead, the Lead Orchestrator immediately terminates the subagent via `manage_subagents(Action="kill")` and either **bisects the Work Packet (<50 LOC)** or **promotes the replacement subagent to `Model: "inherit"` / `"pro"`**.  
> **Audit Verdict**: `CHANGES_REQUIRED — APPLY MECHANICAL PATCHES BELOW IMMEDIATELY`  

---

## 1. Gate Pass/Fail Status Summary for `<WP-ID>`

| Gate # | Verification Gate | Status | Summary of Audit Result |
| :---: | :--- | :---: | :--- |
| **Gate 1** | Scope & Disjoint File Lock | `<PASS / FAIL>` | `<Zero unauthorized files touched / Out-of-scope edit detected>` |
| **Gate 2** | Spec Fidelity & Anti-Slop | `<PASS / FAIL>` | `<Signatures verified; zero unfinished markers or suppressions>` |
| **Gate 3** | 4-Pillar RTM Verification | `<PASS / FAIL>` | `<Acceptance criteria status>` |
| **Gate 4** | 10D Adversarial & Anti-Cheat | `<PASS / FAIL>` | `<Corner-case dimension status>` |
| **Gate 5** | Staff Code Quality (8-Dim) | `<PASS / FAIL>` | `<Score: XX.X/100; Blocking defect count>` |
| **Gate 6** | Principal AppSec (STRIDE/CVSS) | `<PASS / FAIL>` | `<CVSS findings summary>` |

---

## 2. What Passed (Must Remain Intact — Do Not Break Passing Code)

The following components, methods, and unit tests in your Work Packet passed audit and **MUST NOT** be broken, deleted, or refactored away while you apply the mechanical patches below:
- `<path/to/file#L1-L35>`: `<Exact class/function signatures and configuration validation>`
- `<path/to/test_file#L1-L90>`: `<Existing passing unit test cases TC-001 through TC-004>`

---

## 3. Numbered Blocking Defects (Zero-Reasoning Mechanical Remediation)

Do **not** guess, improvise, or rewrite surrounding code. For each defect below, invoke `edit_file` using the exact `Target` and `Replacement` blocks provided.

### Defect #1: `[Gate <6> — <CVSS 7.4 High (SEC-001)>]: <Defect Title>`
- **Violated Gate**: `<Gate 6: AppSec Cryptographic Correctness>`
- **File & Line Anchor**: `<path/to/file#L38-L46>`
- **Failure Mode / Test Traceback / Exploit Vector**:
  ```text
  <Exact test failure traceback from WP-Corner OR exact exploit vector from Auditor-4C showing why the current implementation fails.>
  ```

### Exact Mechanical Patch (Use `edit_file` Directly)
- **`Path`**: `<absolute/path/to/file>`
- **`Target` (Copy verbatim into `edit_file` `Target` argument)**:
  ```typescript
  if (computedHex !== request.signatureHex) {
    throw new SignatureVerificationError("Cryptographic signature verification failed.");
  }
  ```
- **`Replacement` (Copy verbatim into `edit_file` `Replacement` argument)**:
  ```typescript
  const expectedBuffer = Buffer.from(computedHex, "hex");
  const providedBuffer = Buffer.from(request.signatureHex, "hex");
  if (
    expectedBuffer.length === 0 ||
    expectedBuffer.length !== providedBuffer.length ||
    !crypto.timingSafeEqual(expectedBuffer, providedBuffer)
  ) {
    throw new SignatureVerificationError("Cryptographic signature verification failed.");
  }
  ```

---

### Defect #2: `[Gate <4 & 5> — <BLOCKER (BLK-001 / CC-005)>]: <Defect Title>`
- **Violated Gate**: `<Gate 4: 10-Dimension Adversarial Corner Cases (DIM-5 Concurrency) & Gate 5: Staff Concurrency>`
- **File & Line Anchor**: `<path/to/file#L54-L68>`
- **Failure Mode / Test Traceback / Exploit Vector**:
  ```text
  <Exact error output or race condition reproduction trace from CC-005>
  ```

### Exact Mechanical Patch (Use `edit_file` Directly)
- **`Path`**: `<absolute/path/to/file>`
- **`Target` (Copy verbatim into `edit_file` `Target` argument)**:
  ```typescript
  const existing = this.records.get(compositeKey);
  if (existing && existing.status === "COMPLETED") {
    return existing;
  }
  ```
- **`Replacement` (Copy verbatim into `edit_file` `Replacement` argument)**:
  ```typescript
  const existing = this.records.get(compositeKey);
  if (existing) {
    if (existing.payloadHash !== payloadHash) {
      throw new IdempotencyConflictError("Idempotency key already bound to a different payload.");
    }
    if (existing.status === "PROCESSING") {
      throw new ConcurrentExecutionError("Request with this idempotency key is currently in flight.");
    }
    return existing;
  }
  this.records.set(compositeKey, {
    tenantId,
    idempotencyKey,
    payloadHash,
    status: "PROCESSING",
    responseCode: null,
    responseBody: null,
    expiresAtSec,
  });
  ```

---

## 4. Red-Green-Refactor & Anti-Cheat Mandate

1. **Mechanical Patch First**: Apply each `Target` $\rightarrow$ `Replacement` block above using `edit_file`, then immediately run the verification test suite to confirm the failing test transitions from `FAIL` (Red) to `PASS` (Green).
2. **Strict Anti-Cheat Prohibition**:
   - You are **STRICTLY FORBIDDEN** from deleting, skipping, or commenting out any test case.
   - You are **STRICTLY FORBIDDEN** from weakening test assertions, adding hardcoded test-input checks (`if (input === "test_...")`), or mocking out the target method under test.
   - You are **STRICTLY FORBIDDEN** from modifying any file outside your original `ALLOWED TO CREATE OR MODIFY` boundary:
     - `<allowed_implementation_file>`
     - `<allowed_unit_test_file>`

---

## 5. Mandatory Re-Verification Commands Before Replying

Execute all commands below and verify exit code `0` before replying via `send_message`:

```pwsh
# 1. Typecheck & Lint Verification
<exact-typecheck-and-lint-command>

# 2. Scoped Unit Test + Regression Suite Execution
<exact-unit-test-command>

# 3. Disjoint Scope Verification
git status --short
```

Reply via `send_message(Recipient="<lead-orchestrator-id>", Message="...")` with:
1. Confirmation that each `Exact Mechanical Patch` (`Defect #1..#N`) was applied via `edit_file`.
2. Exact stdout/exit code from the re-verification commands above.
3. Updated JSON completion telemetry block with `"attempt": <X>` and `"tests_failed": 0`.
