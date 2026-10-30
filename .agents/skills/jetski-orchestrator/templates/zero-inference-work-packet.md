# ZERO-INFERENCE WORK PACKET: <WP-ID> — <Task Title>
> **TOP BUN — SANDWICH PROMPT ARCHITECTURE (READ FIRST)**
> - **Single-Sentence Mission**: Implement `<exactMethodName>` in `<target/implementation/file>` between the pre-laid skeleton anchors so every row in the Concrete Input $\rightarrow$ Output Truth Table passes with exit code `0`.
> - **STRICT FILE WHITELIST BOX (`ONLY edit these files; zero codebase searching required`)**:
>   - `WRITE ALLOWED`: `<path/to/implementation_file>` (and `<path/to/unit_test_file>` if assigned)
>   - `ALL CONTEXT INLINED BELOW`: Do **NOT** grep or browse the repository. Every required import, type definition, and signature is inlined in Section 3.

---

## Section 1: Single-Sentence Objective & Mission

- **Single-Sentence Objective**: <Implement `<TargetClass>.<exactMethodName>` in `<path/to/implementation_file>` with 100% conformance to the inlined contracts in Section 3 and the Concrete Input $\rightarrow$ Output Truth Table in Section 4.>
- **Architectural Mission**: <Explain in 2 sentences how this isolated unit (<150 LOC, <=2 files) plugs into the Wave 3 parallel execution graph without requiring cross-repo inference.>

---

## Section 2: File Access Boundaries (Scope Lock)

### ALLOWED TO CREATE OR MODIFY (ONLY these exact files):
- `<absolute/or/repo-relative/path/to/implementation_file>`
- `<absolute/or/repo-relative/path/to/unit_test_file>`

### READ-ONLY REFERENCE FILES (Inlined in Section 3; DO NOT edit):
- `<path/to/frozen/shared/types.ts>` (Lines `<1>-<60>`: Inlined verbatim in Section 3.2 below — zero file reads required unless verifying line numbers)
- `<path/to/locked/red_test_file.ts>` (Pre-written Red test suite — **READ-ONLY**; never modify locked tests)

### STRICTLY FORBIDDEN / DO NOT TOUCH:
- Do **NOT** create, modify, rename, or delete any file outside `ALLOWED TO CREATE OR MODIFY`.
- Do **NOT** modify `<path/to/frozen/shared/types.ts>`, barrel `index.ts` files, router wiring, or `package.json` / lockfiles.
- Do **NOT** browse or search unrelated directories; rely strictly on the Inlined Ground-Truth Context Bundle in Section 3.
- Do **NOT** execute destructive VCS commands (`git reset`, `git checkout --`, `git clean`, `git commit`, `git push`).

---

## Section 3: Inlined Ground-Truth Context Bundle & Pre-Laid Skeleton Anchors

> **Anti-Hallucination Lock**: Do **NOT** invent imports, helper functions, or types not shown below. Copy the exact imports and implement only inside the `# === [ANCHOR: IMPLEMENT <fn> START] ===` markers.

### 3.1 Copy-Pasteable Pinned Imports
```typescript
import crypto from "node:crypto";
import {
  WebhookIngressRequest,
  SignatureVerificationError,
  ReplayWindowExpiredError,
} from "./types";
```

### 3.2 Inlined Referenced Types (Verbatim from `<path/to/frozen/shared/types.ts>`)
```typescript
// INLINED READ-ONLY CONTEXT — DO NOT RE-DECLARE OR MODIFY THIS FILE
export interface WebhookIngressRequest {
  readonly tenantId: string;
  readonly idempotencyKey: string;
  readonly signatureHex: string;
  readonly timestampSec: number;
  readonly rawBody: string;
}

export class SignatureVerificationError extends Error {
  public readonly statusCode = 401;
  constructor(message = "Cryptographic signature verification failed.") {
    super(message);
    this.name = "SignatureVerificationError";
  }
}

export class ReplayWindowExpiredError extends Error {
  public readonly statusCode = 401;
  constructor(message = "Request timestamp outside replay tolerance window.") {
    super(message);
    this.name = "ReplayWindowExpiredError";
  }
}
```

### 3.3 Pre-Laid Skeleton Anchor Markers in `<path/to/implementation_file>`
Replace **only** the code between the `START` and `END` anchor comments:

```typescript
export class SignatureVerifier {
  constructor(
    private readonly toleranceWindowSec: number = 300,
    private readonly clockSec: () => number = () => Math.floor(Date.now() / 1000)
  ) {}

  public verify(request: WebhookIngressRequest, tenantSecret: string): boolean {
    // # === [ANCHOR: IMPLEMENT verify START] ===
    throw new Error("ANCHOR_NOT_IMPLEMENTED");
    // # === [ANCHOR: IMPLEMENT verify END] ===
  }
}
```

---

## Section 4: Concrete Input -> Output Truth Table & Step-by-Step Implementation Recipe

### 4.1 Concrete Input $\rightarrow$ Output Truth Table (Few-Shot Ground Truth)
Your implementation **MUST** produce the exact output or exception shown for each literal input below (assuming `clockSec() === 1700000000`, `toleranceWindowSec === 300`, `tenantSecret === "sec_test_123"`):

| Case ID | Exact Input Literal (`request`, `tenantSecret`) | Exact Return Value or Exception Class + Message |
| :---: | :--- | :--- |
| `IO-01` | `{ tenantId: "t1", idempotencyKey: "k1", timestampSec: 1700000000, rawBody: "{\"amt\":100}", signatureHex: "<valid_hmac_sha256_of_1700000000.{\"amt\":100}>" }, "sec_test_123"` | Returns `true` |
| `IO-02` | `{ tenantId: "t1", idempotencyKey: "k1", timestampSec: 1699999700, rawBody: "{\"amt\":100}", signatureHex: "<valid_hmac_at_boundary_-300s>" }, "sec_test_123"` | Returns `true` (exact boundary `abs(now - ts) === 300` is valid) |
| `IO-03` | `{ tenantId: "t1", idempotencyKey: "k1", timestampSec: 1699999699, rawBody: "{\"amt\":100}", signatureHex: "<any>" }, "sec_test_123"` | Throws `ReplayWindowExpiredError("Request timestamp outside replay tolerance window.")` |
| `IO-04` | `{ tenantId: "t1", idempotencyKey: "k1", timestampSec: 0, rawBody: "{\"amt\":100}", signatureHex: "<any>" }, "sec_test_123"` | Throws `ReplayWindowExpiredError("Request timestamp outside replay tolerance window.")` |
| `IO-05` | `{ tenantId: "t1", idempotencyKey: "k1", timestampSec: 1700000000, rawBody: "{\"amt\":100}", signatureHex: "deadbeef" }, "sec_test_123"` | Throws `SignatureVerificationError("Cryptographic signature verification failed.")` |
| `IO-06` | `{ tenantId: "t1", idempotencyKey: "k1", timestampSec: 1700000000, rawBody: "{\"amt\":100}", signatureHex: "abc\u0000def" }, "sec_test_123"` | Throws `SignatureVerificationError("Cryptographic signature verification failed.")` |

### 4.2 Numbered Step-by-Step Implementation Recipe
Implement the body inside `# === [ANCHOR: IMPLEMENT verify START] ===` .. `# === [ANCHOR: IMPLEMENT verify END] ===` using these exact steps:

1. **Step 1 — Validate Non-Empty Secret & Inputs (Lines `18-24`)**:
   - Check that `tenantSecret`, `request.tenantId`, `request.signatureHex`, and `request.rawBody` are non-empty strings without null bytes (`\0`). If invalid, throw `new SignatureVerificationError("Cryptographic signature verification failed.")`.
2. **Step 2 — Enforce Numeric & Replay Window Bounds (Lines `25-33`)**:
   - Check `Number.isInteger(request.timestampSec) && request.timestampSec > 0`.
   - Compute `const skewSec = Math.abs(this.clockSec() - request.timestampSec)`.
   - If `!Number.isInteger(request.timestampSec) || request.timestampSec <= 0 || skewSec > this.toleranceWindowSec`, throw `new ReplayWindowExpiredError("Request timestamp outside replay tolerance window.")`.
3. **Step 3 — Compute Expected HMAC & Constant-Time Digest Comparison (Lines `34-50`)**:
   - Validate `/^[0-9a-fA-F]{64}$/.test(request.signatureHex)`. If false, throw `new SignatureVerificationError("Cryptographic signature verification failed.")`.
   - Compute `const expectedHex = crypto.createHmac("sha256", tenantSecret).update(`${request.timestampSec}.${request.rawBody}`).digest("hex")`.
   - Convert both hex strings to `Buffer` via `Buffer.from(..., "hex")` and compare with `crypto.timingSafeEqual`.

### 4.3 Canonical Exemplar Snippet
```typescript
const expectedBuffer = Buffer.from(expectedHex, "hex");
const providedBuffer = Buffer.from(request.signatureHex, "hex");

if (
  expectedBuffer.length === 0 ||
  expectedBuffer.length !== providedBuffer.length ||
  !crypto.timingSafeEqual(expectedBuffer, providedBuffer)
) {
  throw new SignatureVerificationError("Cryptographic signature verification failed.");
}
return true;
```

---

## Section 5: Exhaustive Edge-Case & Error Matrix

| Case ID | Input Condition / Boundary Trap | Expected Exception or Return Value | HTTP / Domain Code |
| :---: | :--- | :--- | :---: |
| `EC-01` | Empty string `""`, whitespace-only `"   "`, or missing `tenantSecret` / `signatureHex` | Throw `SignatureVerificationError` | `401` / `ERR_INVALID_SIGNATURE` |
| `EC-02` | `signatureHex` containing null byte `\x00`, non-hex chars, or odd length | Throw `SignatureVerificationError` without unhandled `RangeError` | `401` / `ERR_INVALID_SIGNATURE` |
| `EC-03` | `timestampSec` is `0`, `-1`, `NaN`, `Infinity`, or `abs(now - ts) > toleranceWindowSec` | Throw `ReplayWindowExpiredError` | `401` / `ERR_STALE_TIMESTAMP` |
| `EC-04` | Valid signature at exact boundary `abs(now - ts) === toleranceWindowSec` | Return `true` | `200` / `VALID_BOUNDARY` |
| `EC-05` | Valid 64-char hex string that does not match computed HMAC | Throw `SignatureVerificationError` via `timingSafeEqual` | `401` / `ERR_INVALID_SIGNATURE` |

---

## Section 6: Required Unit / Scenario Tests

In `<path/to/unit_test_file>`, ensure deterministic unit tests verify all 6 rows (`IO-01` through `IO-06`) from the Concrete Input $\rightarrow$ Output Truth Table:

1. **`test_verify_io01_valid_hmac_returns_true`**: Verifies `IO-01`.
2. **`test_verify_io02_exact_300s_boundary_returns_true`**: Verifies `IO-02`.
3. **`test_verify_io03_io04_expired_and_zero_timestamps_throw_401`**: Verifies `IO-03` and `IO-04`.
4. **`test_verify_io05_io06_invalid_hex_and_null_byte_throw_401`**: Verifies `IO-05` and `IO-06`.

---

## Section 7: Anti-Slop & Prohibited Patterns Mandate

Your deliverable will be scanned by `jetski_orchestrator.py audit-diff` and `jetski_orchestrator.py validate-spec --mode audit` during the Wave 4 Audit Council. Your Work Packet will be **AUTOMATICALLY REJECTED** if any of the following exist:
- **Zero Unfinished Work Markers**: Do NOT leave any unfinished-work comment markers (such as T-O-D-O, F-I-X-M-E, H-A-C-K, or X-X-X), `ANCHOR_NOT_IMPLEMENTED` throws, or ellipsis placeholders (`...`).
- **Zero Hardcoded Test Literals**: Never write conditional branches that check for specific test strings (e.g., `if (input === "test_1") return true`). Implement the real algorithm.
- **Zero Empty Catch Blocks or Type Suppressions**: Never use empty catch blocks, `any`, `as unknown as`, ts-ignore directives, ts-expect-error directives, python type-ignore comments, noqa comments, or eslint-disable comments.
- **Zero Test Tampering (Anti-Cheat)**: Never delete failing tests, weaken assertions, or modify read-only test suites.

---

## Section 8: Deterministic Verification Command & Completion Report Format

Execute these exact verification commands before replying:

```pwsh
# 1. Run Typecheck & Lint
<exact-typecheck-and-lint-command>

# 2. Run Scoped Unit Tests for <WP-ID>
<exact-unit-test-command-for-this-work-packet>

# 3. Verify Scope Lock (Confirm ONLY allowed files were created/modified)
git status --short
```

Reply to the caller via `send_message` with this exact structure:

```markdown
### Work Packet Completion Report: <WP-ID>

```json
{
  "work_packet_id": "<WP-ID>",
  "status": "COMPLETED",
  "files_created_or_modified": [
    "<path/to/implementation_file>",
    "<path/to/unit_test_file>"
  ],
  "out_of_scope_files_touched": [],
  "verification_exit_code": 0,
  "tests_passed": <N>,
  "tests_failed": 0,
  "anti_slop_clean": true
}
```
```

---

> ### BOTTOM BUN — FINAL 5 NON-NEGOTIABLE HARD RULES (READ BEFORE CALLING ANY TOOL)
> 1. **ONLY TOUCH ALLOWED FILES**: Edit **only** the files listed under `ALLOWED TO CREATE OR MODIFY` in Section 2. Touching any other file fails Gate 1 immediately.
> 2. **NEVER TOUCH LOCKED TEST FILES**: If a pre-written Red test suite is listed under `READ-ONLY REFERENCE FILES`, never edit, delete, or weaken its assertions.
> 3. **REPLACE ONLY THE TARGET SKELETON ANCHORS WITH ZERO PLACEHOLDERS**: Implement the complete logic between `# === [ANCHOR: IMPLEMENT <fn> START] ===` and `END` with zero unfinished markers or stub throws.
> 4. **NO HARDCODED TEST LITERALS**: Never branch on literal test inputs (`if (input === "test_...")`); implement the general algorithm from Section 4.2 so every row in Section 4.1's Truth Table passes naturally.
> 5. **RUN THE EXACT VERIFICATION COMMAND & CONFIRM EXIT CODE `0`**: Do not send your completion message until the Section 8 test command exits with code `0`.
