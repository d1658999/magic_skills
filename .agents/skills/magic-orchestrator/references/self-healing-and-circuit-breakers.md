# Self-Healing Loops & Circuit Breakers Reference Manual

This document details the autonomous error recovery, self-healing remediation loops, and safety circuit breakers enforced by the **Magic Orchestrator**.

---

## 1. The Autonomous Self-Healing Lifecycle

When a defect, failing test, or council audit violation occurs, the system does not stop or wait for manual human intervention. Instead, it enters the **Autonomous Self-Healing Loop**:

```mermaid
flowchart TD
    D["Defect / Failing Test Detected"] --> T["Step 1: Author Reproducible Failing Test (RED)"]
    T --> AC1["Anti-Cheat Check: Verify Test Genuinely Fails"]
    AC1 --> M["Step 2: Apply Surgical Minimal Fix to Code (GREEN)"]
    M --> AC2["Anti-Cheat Check: Verify Zero Test Tampering"]
    AC2 --> R["Step 3: Run Full Regression Suite"]
    R -->|Pass & Clean| G["Approved (GREEN & REFACTORED)"]
    R -->|Fail or Regressed| CB{"Retry Count < 3?"}
    CB -->|Yes| M
    CB -->|No (Circuit Breaker Tripped)| ESC["Escalate to Lead Architect (AGY Pro Tier)"]
```

---

## 2. The 3 Immutable Self-Healing Invariants

1. **The Test-First Imperative (No Fix Without Red Test)**:
   - Never modify production code to fix a bug without first authoring an automated, deterministic test that reproduces the bug and fails (RED).
   - The test must fail due to the defect, not due to compilation errors or syntax crashes.

2. **The Anti-Cheat Invariant (Zero Test Tampering)**:
   - A test suite must never be "made to pass" by:
     - Deleting or commenting out assertions.
     - Relaxing assertion thresholds (e.g., changing `toBe(100)` to `toBeGreaterThan(0)`).
     - Poisoning test mocks or fixtures to return artificial success flags.
     - Hardcoding input-specific return values inside production code.
   - The remediation runner executes `git diff` on test paths. Any unauthorized modification to existing test cases causes an immediate **ANTI-CHEAT VIOLATION** rejection.

3. **The Zero-Regression Guarantee**:
   - Healing a corner case or fixing a security defect must not break any existing functionality.
   - The entire baseline regression test suite must run and pass alongside the newly added tests.

---

## 3. Surgical Reassignment Protocols

### Protocol A: GitHub Copilot CLI Session Resumption
When an output from a Copilot CLI worker (`collama`, `ollama-copilot`, `ollama-copilot_2`) fails council review:
1. Extract the session ID from the command output:
   `Resume copilot --resume=9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d`
2. Re-dispatch using `-ResumeSessionId` and `-CorrectionFeedback`:
   ```powershell
   pwsh .agents/skills/magic-orchestrator/scripts/magic_orchestrator.ps1 -DispatchCopilot `
     -Engine ollama-copilot `
     -ResumeSessionId "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d" `
     -SpecContextPath "./openspec/changes/feature-x" `
     -CorrectionFeedback "COUNCIL AUDIT FAILED [Gate 2: Spec Compliance]: Task 1.1 returned a stub function for calculateTotal(). Implement complete logic according to spec.md lines 45-60. No placeholders permitted."
   ```

### Protocol B: Antigravity Subagent Correction via `send_message`
When an AGY subagent's work packet fails:
1. Do **NOT** kill the subagent or start a fresh one immediately (which discards context).
2. Call `send_message(Recipient=<conversationId>, Message=<directive>)` using `templates/correction-directive.md`.
3. The directive must contain:
   - **Failed Gate**: (e.g., Gate 1 Scope Boundary or Gate 5 Concurrency).
   - **Exact Defect Location**: File path and line numbers (`src/auth/token.ts:L42-L58`).
   - **Current vs. Required Behavior**: Concrete explanation of what went wrong and expected state.
   - **Drop-In Fix Guidance**: Verified architectural code snippet.
   - **Re-Verification Command**: Shell command to run before reporting back.

---

## 4. The 3-Strike Circuit Breaker

To prevent infinite loops, token exhaustion, or thrashing:

### The Rule of 3 Retries:
- Each subagent / task packet is granted a maximum of **3 correction attempts**.
- If a subagent fails Council Audit on the 3rd attempt, the **Circuit Breaker Trips**:

```
[Attempt 1: Fail] ──► Surgical Directive 1 ──► [Attempt 2: Fail] ──► Surgical Directive 2 ──► [Attempt 3: Fail]
                                                                                                    │
                                                                                        (CIRCUIT BREAKER TRIPPED)
                                                                                                    │
                                                                                                    ▼
                                                                                   [Lead Architect Escalation]
```

### Escalation Actions upon Circuit Breaker Trip:
1. **Terminate Worker**: Call `manage_subagents(Action="kill", ConversationIds=[<id>])`.
2. **Quarantine Changes**: Revert unverified changes in the defective module using `git checkout`.
3. **Escalate to Lead Architect (`pro` tier)**:
   - The Lead Architect inspects the failure telemetry, analyzes why the subagent failed, and decides between:
     - **Option 1 (Spec Refinement)**: The specification was ambiguous $\rightarrow$ Clarify spec and spawn a fresh `"pro"` subagent.
     - **Option 2 (Direct Lead Fix)**: The task requires staff-level architectural insight $\rightarrow$ The Lead Architect implements the fix directly and documents the rationale in the changelog.
