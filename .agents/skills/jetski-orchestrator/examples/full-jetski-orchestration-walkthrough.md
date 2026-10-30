# End-to-End Walkthrough: Multi-Tenant Webhook & Payment Idempotency Service

This walkthrough demonstrates how the Lead Orchestrator in `jetski-cli` executes a complex engineering task—building and verifying a **Multi-Tenant Webhook & Payment Idempotency Service**—across all **6 Parallel Waves** with maximum subagent concurrency, deterministic CLI gating, and autonomous Red-Green self-healing.

---

## Task Prompt

> *"Build a production-grade Multi-Tenant Webhook & Payment Idempotency Service (`src/webhooks/`). Incoming webhooks must verify per-tenant HMAC-SHA256 signatures with a 300-second replay window, enforce strict `(tenant_id, idempotency_key)` deduplication with SHA-256 payload conflict detection (`409 Conflict`), prevent concurrent double-charging under parallel retries, and achieve >=90% 4-Pillar RTM coverage plus 10-Dimension adversarial verification."*

---

## Wave 1: Parallel 360° Reconnaissance & Threat Discovery (Turn 1)

Instead of reading files sequentially, the Lead Orchestrator defines the read-only recon personas (`recon-architect` and `rtm-and-corner-planner`) and emits **3 `invoke_subagent` calls in a single model turn**:

```json
[
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "recon-architect",
      "Role": "Recon-Codebase-AST",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Inspect repo structure, TypeScript/Python conventions, error base classes, and exact test runner commands for src/webhooks/. Reply via send_message."
    }
  },
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "rtm-and-corner-planner",
      "Role": "Recon-RTM-And-Corner-Cases",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Draft a >=90% 4-Pillar Bidirectional RTM (Happy 40%, Alternate 30%, Error 20%, E2E 10%) and a 10-Dimension Adversarial Corner-Case Matrix (DIM-1..DIM-10) for the Multi-Tenant Webhook & Payment Idempotency Service. Reply via send_message."
    }
  },
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "rtm-and-corner-planner",
      "Role": "Recon-AppSec-STRIDE",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Produce the STRIDE Threat Model and Source-to-Sink Taint Matrix for webhook HMAC verification, timestamp replay bounds, and multi-tenant idempotency storage. Reply via send_message."
    }
  }
]
```

**Turn Termination & Reactive Wakeup**: The Lead Orchestrator stops calling tools. When all 3 subagents reply via `send_message`, `jetski-cli` wakes the Lead Orchestrator with their full reconnaissance payloads.

---

## Wave 2: Master Dossier Synthesis & Zero-Inference Contract Lock (Turn 2)

Using the Wave 1 reports, the Lead Orchestrator locks the shared interfaces **before** spawning any worker subagents so workers never edit the same contract file:

1. **Pre-Creates Frozen Shared Contracts (`src/webhooks/types.ts`)**:
   ```typescript
   // src/webhooks/types.ts — Locked by Lead Orchestrator in Wave 2
   export type IdempotencyStatus = "PROCESSING" | "COMPLETED" | "FAILED_TERMINAL";

   export interface WebhookIngressRequest {
     readonly tenantId: string;
     readonly idempotencyKey: string;
     readonly signatureHex: string;
     readonly timestampSec: number;
     readonly rawBody: string;
   }

   export interface IdempotencyRecord {
     readonly tenantId: string;
     readonly idempotencyKey: string;
     readonly payloadHash: string;
     readonly status: IdempotencyStatus;
     readonly responseCode: number | null;
     readonly responseBody: string | null;
     readonly expiresAtSec: number;
   }

   export class SignatureVerificationError extends Error {
     public readonly statusCode = 401;
   }
   export class ReplayWindowExpiredError extends Error {
     public readonly statusCode = 401;
   }
   export class IdempotencyConflictError extends Error {
     public readonly statusCode = 409;
   }
   export class ConcurrentExecutionError extends Error {
     public readonly statusCode = 409;
   }
   ```

2. **Authors the Master Orchestration Dossier & 4 Disjoint Work Packets**:
   - `artifacts/master-orchestration-dossier.md` (with 20 Acceptance Criteria mapped across the 4 Pillars for **95.0% RTM coverage** and `CC-001..CC-010` across `DIM-1..DIM-10`).
   - `artifacts/packets/WP-1-signature-verifier.md` $\rightarrow$ exclusive write lock on `src/webhooks/signature-verifier.ts` and `tests/unit/signature-verifier.test.ts`.
   - `artifacts/packets/WP-2-idempotency-store.md` $\rightarrow$ exclusive write lock on `src/webhooks/idempotency-store.ts` and `tests/unit/idempotency-store.test.ts`.
   - `artifacts/packets/WP-Verify-rtm-suite.md` $\rightarrow$ exclusive write lock on `tests/acceptance/webhooks.rtm.test.ts`.
   - `artifacts/packets/WP-Corner-10d-suite.md` $\rightarrow$ exclusive write lock on `tests/adversarial/webhooks.corner.test.ts`.

3. **Runs Deterministic Packet & Disjoint Scope Validation**:
   ```pwsh
   python .agents/skills/jetski-orchestrator/scripts/jetski_orchestrator.py validate-packets --packet-dir artifacts/packets
   # Exit Code 0: All 4 packets have 8 required sections, 0 unfinished markers, and 100% disjoint write locks.
   ```

---

## Wave 3: Parallel Implementation & Test Construction Swarm (Turn 3)

The Lead Orchestrator spawns **all 4 Wave 3 subagents in parallel in a single turn** and records their `conversationId`s:

```json
[
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "zero-inference-worker",
      "Role": "WP-1: SignatureVerifier",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Execute artifacts/packets/WP-1-signature-verifier.md. Allowed writes: src/webhooks/signature-verifier.ts, tests/unit/signature-verifier.test.ts."
    }
  },
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "zero-inference-worker",
      "Role": "WP-2: IdempotencyStore",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Execute artifacts/packets/WP-2-idempotency-store.md. Allowed writes: src/webhooks/idempotency-store.ts, tests/unit/idempotency-store.test.ts."
    }
  },
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "verify-and-corner-tester",
      "Role": "WP-Verify: 4-Pillar Acceptance Suite",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Execute artifacts/packets/WP-Verify-rtm-suite.md. Implement TC-001..TC-019 (95% RTM coverage) in tests/acceptance/webhooks.rtm.test.ts."
    }
  },
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "verify-and-corner-tester",
      "Role": "WP-Corner: 10D Adversarial & Race Suite",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Execute artifacts/packets/WP-Corner-10d-suite.md. Implement CC-001..CC-010 across DIM-1..DIM-10 in tests/adversarial/webhooks.corner.test.ts."
    }
  }
]
```

**Saved Subagent Conversation IDs**:
- `WP-1` (`SignatureVerifier`): `conv-wp1-88a1`
- `WP-2` (`IdempotencyStore`): `conv-wp2-44b9`
- `WP-Verify` (`4-Pillar RTM`): `conv-wpv-19c2`
- `WP-Corner` (`10D Adversarial`): `conv-wpc-77d4`

---

## Wave 4: Parallel 6-Gate Council Audit (Turn 4)

Once all 4 Wave 3 subagents report completion, `WP-Corner` notes that `CC-005` (`test_dim5_parallel_race_atomic_cas`) caught a race condition under 20 concurrent promises. The Lead Orchestrator immediately launches the **3-Agent Audit Council in parallel**:

```json
[
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "staff-code-reviewer",
      "Role": "Auditor-4A: Scope, Slop, RTM & 10D Gatekeeper",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Audit Gates 1, 2, 3, and 4 across src/webhooks/ and tests/. Verify disjoint scope, anti-slop, >=90% RTM, 10D coverage, and Anti-Cheat test integrity."
    }
  },
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "staff-code-reviewer",
      "Role": "Auditor-4B: Staff 8-Dimension Reviewer",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Audit Gate 5 across src/webhooks/signature-verifier.ts and src/webhooks/idempotency-store.ts. Produce the 8-Dimension Weighted Scorecard and Conventional Comments with Drop-In Replacements."
    }
  },
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "principal-security-reviewer",
      "Role": "Auditor-4C: Principal AppSec & CVSS Auditor",
      "Model": "inherit",
      "Workspace": "inherit",
      "Prompt": "Audit Gate 6 (STRIDE, Taint Tracking, OWASP API Top 10, Cryptographic Correctness, CVSS v3.1) across src/webhooks/."
    }
  }
]
```

### Wave 4 Council Findings (Attempt 1 Verdict: `REJECTED_ENTER_WAVE_5_REMEDIATION`)
- **Gate 1 (Scope) & Gate 2 (Anti-Slop)**: `PASS` (100% disjoint files; `0` unfinished markers or suppressions).
- **Gate 3 (4-Pillar RTM)**: `PASS` (`19/20` ACs = **95.0% coverage** across Happy 40%, Alternate 30%, Error 20%, E2E 10%).
- **Gate 4 (10D Corner Cases) & Gate 5 (Staff Review)**: `FAIL` — `Auditor-4B` flags **`[BLOCKER]` (`BLK-001`)** in `src/webhooks/idempotency-store.ts#L54-L68`: non-atomic `get()` followed by `await handler()` before setting `PROCESSING` creates a **TOCTOU race condition** exposed by `CC-005` (`DIM-5`).
- **Gate 6 (AppSec & CVSS)**: `FAIL` — `Auditor-4C` flags **`SEC-001` (`CWE-208`, CVSS v3.1 `7.4 High`, `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N`)** in `src/webhooks/signature-verifier.ts#L41`: HMAC comparison used `computedHex === signatureHex` (or `==` instead of `hmac.compare_digest` / `crypto.timingSafeEqual`), leaking signature bytes via timing side-channel.

---

## Wave 5: Contextual `send_message` Self-Healing Loop (Turn 5)

Rather than spawning cold subagents that lose context, the Lead Orchestrator sends **parallel Surgical Correction Directives** via `send_message` to the existing `WP-1` and `WP-2` conversations:

```json
[
  {
    "tool": "send_message",
    "args": {
      "Recipient": "conv-wp1-88a1",
      "Message": "# SURGICAL CORRECTION DIRECTIVE: WP-1 — Attempt 2 of 3\n## Defect #1: [Gate 6 — CVSS 7.4 High (SEC-001)]\n- File: src/webhooks/signature-verifier.ts#L38-L46\n- Violation: Standard string equality (=== / ==) instead of constant-time digest comparison (crypto.timingSafeEqual / hmac.compare_digest).\n- Drop-In Replacement:\n```typescript\nconst expectedBuf = Buffer.from(computedHex, 'hex');\nconst providedBuf = Buffer.from(signatureHex, 'hex');\nif (expectedBuf.length === 0 || expectedBuf.length !== providedBuf.length || !crypto.timingSafeEqual(expectedBuf, providedBuf)) {\n  throw new SignatureVerificationError('Cryptographic signature verification failed.');\n}\n```\nRe-run unit tests and reply with updated completion report."
    }
  },
  {
    "tool": "send_message",
    "args": {
      "Recipient": "conv-wp2-44b9",
      "Message": "# SURGICAL CORRECTION DIRECTIVE: WP-2 — Attempt 2 of 3\n## Defect #1: [Gate 4 & Gate 5 — BLOCKER (BLK-001 TOCTOU Race)]\n- File: src/webhooks/idempotency-store.ts#L54-L68\n- Violation: Check-then-act race allows concurrent requests with identical (tenantId, idempotencyKey) to bypass lock in CC-005.\n- Drop-In Replacement: Synchronously transition ABSENT -> PROCESSING inside acquireOrReplay() before yielding to the async handler, and throw ConcurrentExecutionError (409) if status === 'PROCESSING'.\nRe-run unit tests and reply with updated completion report."
    }
  }
]
```

### Red-Green Self-Healing & Anti-Cheat Verification
1. Both `conv-wp1-88a1` and `conv-wp2-44b9` apply the surgical drop-in replacements and reply with `verification_exit_code: 0`.
2. The Lead Orchestrator messages `WP-Corner` (`conv-wpc-77d4`) to re-execute the 10-Dimension Adversarial Suite (`CC-001..CC-010`) and runs the Anti-Cheat and Anti-Slop checks:
   ```pwsh
   python .agents/skills/jetski-orchestrator/scripts/jetski_orchestrator.py audit-diff --path src/webhooks
   # Result: 0 slop violations, 0 deleted/weakened test assertions, 42/42 tests PASS.
   ```
3. Re-audit by `Auditor-4B` and `Auditor-4C` on **Attempt 2** returns:
   - **Gate 5 Score**: `94.0 / 100` (`0` Blockers, `0` Majors)
   - **Gate 6 AppSec**: `Max CVSS 0.0 (None)` (`SEC-001` verified remediated)

---

## Wave 6: Final Integration, 6-Gate Scorecard & Executive Sign-Off (Turn 6)

With all workers and test suites verified green, the Lead Orchestrator completes the final integration:

1. **Wires the Ingress Router (`src/webhooks/index.ts`)**: Connects `SignatureVerifier` and `IdempotencyStore` into `WebhookIngressRouter` and runs the full E2E acceptance + adversarial test suite (`42/42 passing`).
2. **Generates the Unified 6-Gate Council Scorecard**:
   ```pwsh
   python .agents/skills/jetski-orchestrator/scripts/jetski_orchestrator.py generate-council-scorecard `
     --rtm-coverage 95.0 `
     --review-score 94.0 --blockers 0 `
     --max-cvss 0.0 `
     --out artifacts/unified-6gate-scorecard.md
   ```
3. **Delivers the Executive Sign-Off Report (`artifacts/executive-signoff-report.md`)**:
   - **Readiness Verdict**: `PRODUCTION READY — ALL 6 GATES PASSED`
   - **Metrics**: `95.0%` 4-Pillar RTM Coverage | `10/10` Corner-Case Dimensions Passing | `94.0/100` Staff Score | `0.0` Max Unresolved CVSS | `2` Wave-5 Defects Self-Healed (`SEC-001`, `BLK-001`).
