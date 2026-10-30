# End-to-End Walkthrough: Distributed Rate Limiting System

This walkthrough demonstrates how the **Magic Orchestrator** executes a real-world, complex engineering task from initial user prompt to final Git commit with zero human debugging.

---

## 0. The User Request

> **User**: *"Build a distributed token bucket rate limiter with Redis storage, multi-tenant tier limits (free, pro, enterprise), atomic concurrency protection, and Express.js middleware."*

---

## Stage 0: Ground-Truth Reconnaissance & Spec-Driven Architecture Lock

The Lead Architect (Antigravity top-tier model) runs the environment probe and inspects the codebase:

```powershell
pwsh .agents/skills/magic-orchestrator/scripts/magic_orchestrator.ps1 -CheckEnvironment
```

### 1. Codebase Reconnaissance
- Runtime: Node.js v20+, TypeScript 5.4.
- Active test runner: Vitest (`npm test`).
- Existing Redis connection pool: `src/lib/redis.ts`.

### 2. Contract Freezing (Zero-Inference Mandate)
The Lead Architect authors `docs/master-dossier.md` and freezes the core contracts:

```typescript
export interface RateLimitTier {
  readonly maxTokens: number;
  readonly refillRatePerSecond: number;
}

export interface RateLimitResult {
  readonly allowed: boolean;
  readonly remainingTokens: number;
  readonly resetTimestampMs: number;
  readonly retryAfterSeconds?: number;
}

export interface RateLimiterStorage {
  consumeTokens(
    tenantId: string,
    key: string,
    tier: RateLimitTier,
    cost?: number
  ): Promise<RateLimitResult>;
}
```

### 3. Error Taxonomy Frozen
- `ERR_RATE_LIMIT_EXCEEDED`: HTTP 429 with standard `Retry-After` header.
- `ERR_STORAGE_UNAVAILABLE`: HTTP 503 (Fail-Open or Fail-Closed based on tenant config).

---

## Stage 1: Atomic Work Packet Authoring & Boundary Scope Lock

The Lead Architect partitions the task into 4 atomic work packets with strictly disjoint write sets:

```
WP-1: Token Bucket Algorithm (src/limiter/bucket.ts) [~110 LOC]
WP-2: Redis Lua Atomic Storage (src/limiter/redisStore.ts) [~130 LOC]
WP-3: Express Middleware & Header Injector (src/middleware/rateLimit.ts) [~90 LOC]
WP-4: Broad-Spectrum & E2E Integration Suite (tests/limiter/limiter.test.ts) [~140 LOC]
```

Boundary Disjointness Verification:
```powershell
pwsh .agents/skills/magic-orchestrator/scripts/magic_orchestrator.ps1 -ValidatePackets -PacketDir ./packets
# Output: [+] SUCCESS: All work packets have strictly disjoint write sets. Zero collision risk.
```

---

## Stage 2: Hybrid Multi-Engine Parallel Dispatch

The Lead Architect dispatches the 4 work packets across the hybrid fleet:

```powershell
# Fleet A: Dispatch independent core modules to ollama-copilot & ollama-copilot_2
pwsh .agents/skills/magic-orchestrator/scripts/magic_orchestrator.ps1 -DispatchCopilot `
  -Engine ollama-copilot -MaxSubagents 2 `
  -Tasks "WP-1: Token Bucket Algorithm", "WP-2: Redis Lua Storage"

# Fleet B: Dispatch focused Middleware to collama (Clamped to 1 for TPM/RPM safety)
pwsh .agents/skills/magic-orchestrator/scripts/magic_orchestrator.ps1 -DispatchCopilot `
  -Engine collama -MaxSubagents 1 `
  -Tasks "WP-3: Express Middleware"
```

Simultaneously, `WP-4` (Test Architecture) is spawned via Antigravity native subagent (`invoke_subagent` with `Model: "pro"`).

---

## Stage 3: Broad-Spectrum Functional Verification (RTM $\ge 90\%$)

The test architect constructs the Requirements Traceability Matrix (`docs/rtm.md`):

- **Pillar 1: Golden Happy Paths ($40\%$)**: Valid requests consume tokens; headers injected; HTTP 200 returned.
- **Pillar 2: Alternate Valid Branches ($30\%$)**: Free vs Pro vs Enterprise tier limits; custom token costs; burst handling.
- **Pillar 3: Expected Error Flows ($20\%$)**: Token exhaustion returns HTTP 429 with `Retry-After`; invalid tenant returns 400.
- **Pillar 4: End-to-End Integrations ($10\%$)**: Multi-tenant concurrent traffic simulation with Redis cluster.

Coverage Audit Command:
```powershell
pwsh .agents/skills/magic-orchestrator/scripts/magic_orchestrator.ps1 -CalcCoverage -RtmFile ./docs/rtm.md -Threshold 90.0
```
**Output**:
```
[*] Total Requirements Identified: 8
[*] Total Automated Scenarios Mapped: 15
[*] Computed Scenario Coverage Ratio: 93.8%
[*] Status against 90.0% threshold: PASSED (APPROVED)
```

---

## Stage 4: Adversarial 10D Corner-Case Hunting & Self-Healing

The adversarial test suite executes tests across all 10 boundary dimensions:

### 1. Defect Discovered: DIM-5 (Concurrency Race Condition)
Under 1,000 simulated parallel requests, simple Redis `GET` then `SET` allowed 14 excess requests through (TOCTOU race).

### 2. Autonomous Red-Green-Refactor Healing Loop:
1. **RED**: Adversarial test `test_redis_atomic_race` confirms the TOCTOU failure under load.
2. **GREEN**: The remediation controller applies an atomic Lua script (`evalsha`) executing token consumption inside Redis single-threaded memory.
3. **Anti-Cheat Verification**: Confirmed zero modifications to test assertions.
4. **Result**: 1,000 concurrent requests processed; exactly 100 allowed, 900 rejected with HTTP 429. Zero leaks.

---

## Stage 5: Dual Council Review (Staff Quality + Offensive AppSec)

The Dual Council inspects the pull request diff:

```powershell
pwsh .agents/skills/magic-orchestrator/scripts/magic_orchestrator.ps1 -AuditSecurity -DiffFile ./pr.diff
pwsh .agents/skills/magic-orchestrator/scripts/magic_orchestrator.ps1 -AuditDiff -DiffFile ./pr.diff
```

### Council Evaluation:
1. **Gate 1 (Scope)**: Exactly 4 permitted files touched. 0 out-of-scope edits. `PASS`
2. **Gate 2 (Spec & Anti-Slop)**: 0 `TODO`s, 0 stubs, 0 swallowed exceptions. `PASS`
3. **Gate 3 (Functional RTM)**: 93.8% scenario coverage. `PASS`
4. **Gate 4 (10D Corner Cases)**: 10/10 dimensions passed. `PASS`
5. **Gate 5 (Staff Quality)**: Concurrency safe with Lua script; memory footprint bounded. `PASS`
6. **Gate 6 (AppSec)**: Redis key namespaced with tenant ID (`rl:{tenantId}:{key}`), preventing cross-tenant BOLA. CVSS: 0.0. `PASS`

Scorecard Generation:
```powershell
pwsh .agents/skills/magic-orchestrator/scripts/magic_orchestrator.ps1 -GenerateScorecard -OutScorecard ./council-scorecard.md
```

---

## Stage 6: Holistic Integration, Executive Sign-Off & Git Commit

1. **Holistic Smoke Test**:
   ```bash
   npm run typecheck && npm test
   # Vitest v1.6.0: 22 passed (100%), 0 failed
   ```
2. **Executive Sign-Off Dossier**: Author `docs/executive-signoff.md`.
3. **Git Version Control Commit**:
   ```bash
   git add .
   git commit -m "feat(rate-limiter): distributed atomic token bucket rate limiter [Magic-Orchestrator: 6-Gate Approved, RTM 93.8%, CVSS 0.0]"
   ```

**Deliverable concluded with 100% mathematical certainty and zero defects.**
