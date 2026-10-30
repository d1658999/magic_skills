# Full Planning Walkthrough: From Vague Goal to Zero-Inference Execution

> **Case Study**: Demonstrates how a high-reasoning **Research Planner** agent converts an ambiguous user request into an airtight, zero-inference plan that a lower-tier (7B parameter) AI model executes without a single error or hallucination.

---

## 1. The Initial User Prompt

A developer submits the following request in chat:

> *"Hey, our Fastify API is getting hammered by bots on login. We need to add Redis rate limiting with sliding windows. Make sure small models or subagents write the code because I want to run this through Copilot CLI / local Ollama."*

---

## 2. Phase 1: 360° Requirements Deconstruction

The Research Planner identifies that the request is missing several critical architectural details:
1. **Ambiguity 1**: What happens if Redis goes down?
   - *Resolution*: Must fail-open to avoid taking down the entire API for legitimate users.
2. **Ambiguity 2**: What rate limit quotas should apply to which endpoints?
   - *Resolution*: Define distinct route tiers: `auth` (5 req/min) vs `public` (60 req/min).
3. **Ambiguity 3**: What headers and HTTP response codes should be returned?
   - *Resolution*: Enforce RFC 6585 standard (`HTTP 429 Too Many Requests`, `Retry-After`, `X-RateLimit-*`).
4. **Ambiguity 4**: What mechanism achieves atomic sliding windows in Redis without race conditions?
   - *Resolution*: A single Lua script using Redis Sorted Sets (`ZSET`).

The Planner creates the **Requirements Research Dossier** (`templates/requirements-research-dossier.md`).

---

## 3. Phase 2: Ground-Truth Codebase Reconnaissance

The Planner explores the target repository to verify existing tooling and avoid assumptions:

```bash
# 1. Inspect package.json
# Finds: "fastify": "^4.26.1", "ioredis": "^5.3.2", "vitest": "^1.4.0"

# 2. Check TypeScript configuration
# Finds: tsconfig.json has "strict": true, "moduleResolution": "NodeNext"

# 3. Test existing test runner
pnpm exec vitest run tests/health.test.ts
# Confirms: Vitest works cleanly and exits code 0.
```

The Planner records the exact commands and imports in the dossier.

---

## 4. Phase 3: Zero-Inference Architecture & Contract Freezing

The Planner locks down the contracts so the executor model makes zero design choices:
1. Creates `src/types/rate-limit.ts` contract containing `RateLimitResult`, `RateLimitCheckParams`, and `RateLimitTierConfig`.
2. Authors the exact Redis Lua script for the sliding-window logic.
3. Defines the exact Fastify `onRequest` hook structure.
4. Authors the **Master Technical Specification** (`templates/master-technical-spec.md`).

---

## 5. Phase 4: Atomic Task Decomposition & DAG Synthesis

The Planner decomposes the work into 3 atomic micro-tasks:

| Task ID | Permitted File | Objective | Dependencies | Concurrency |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-001` | `src/types/rate-limit.ts` | Define and export domain interfaces | None | Stage 0 (Sequential) |
| `TASK-002` | `src/services/rate-limit.service.ts` | Implement Redis Lua sliding-window logic | `TASK-001` | Stage 1 (Sequential) |
| `TASK-003` | `src/middleware/rate-limiter.ts` | Wire Fastify onRequest hook & headers | `TASK-001`, `TASK-002` | Stage 2 (Sequential) |

For each task, the Planner generates an **Atomic Task Packet** containing:
- Exact line anchors.
- Verbatim imports.
- Numbered procedural implementation recipes.
- Banned slop markers (`TODO`, `any`, etc.).
- Deterministic verification commands.

---

## 6. Pre-Execution Quality Audit (Self-Testing the Plan)

Before dispatching the task packets to the low-tier model, the Planner audits the spec using the built-in validator script:

```powershell
pwsh .agents/skills/research-planner/scripts/validate_spec.ps1 -Mode Spec -File examples/sample-atomic-task-packet.md
```

**Output**:
```
Auditing Atomic Task Packet document: examples/sample-atomic-task-packet.md
✅ SPECIFICATION PASSED ZERO-INFERENCE AUDIT.
   Document meets high-standard requirements for execution by low-tier models.
```

---

## 7. Execution by Low-Tier Model (Simulated Run)

The Planner (or Orchestrator) wraps `TASK-002` using the **Executor Prompt Template** and sends it to a 7B local model.

### Low-Tier Model Response:
```typescript
import { Redis } from 'ioredis';
import {
  RateLimitCheckParams,
  RateLimitResult,
  RateLimitSuccessResult,
  RateLimitExceededResult
} from '../types/rate-limit';

export class RateLimitService {
  constructor(private readonly redis: Redis) {}

  public async checkLimit(params: RateLimitCheckParams): Promise<RateLimitResult> {
    const key = `rl:${params.routeTier}:${params.identifier}`;
    const nowMs = Date.now();
    const windowMs = params.config.windowSeconds * 1000;
    const ttlSec = params.config.windowSeconds + 2;

    try {
      const rawResult = (await this.redis.eval(
        `
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])
        local ttl = tonumber(ARGV[4])
        local clearBefore = now - window
        redis.call('ZREMRANGEBYSCORE', key, '-inf', clearBefore)
        local currentCount = redis.call('ZCARD', key)
        if currentCount < limit then
          redis.call('ZADD', key, now, now)
          redis.call('EXPIRE', key, ttl)
          return { 1, limit - currentCount - 1 }
        else
          return { 0, 0 }
        end
        `,
        1,
        key,
        nowMs.toString(),
        windowMs.toString(),
        params.config.maxRequests.toString(),
        ttlSec.toString()
      )) as [number, number];

      const allowed = rawResult[0] === 1;
      const remaining = rawResult[1];
      const resetSeconds = params.config.windowSeconds;

      if (allowed) {
        return {
          allowed: true,
          limit: params.config.maxRequests,
          remaining: Math.max(0, remaining),
          resetSeconds
        };
      } else {
        return {
          allowed: false,
          limit: params.config.maxRequests,
          remaining: 0,
          resetSeconds
        };
      }
    } catch (err) {
      console.warn('[RateLimitService] Redis check failed; failing open:', err);
      return {
        allowed: true,
        limit: params.config.maxRequests,
        remaining: params.config.maxRequests,
        resetSeconds: 0
      };
    }
  }
}
```

---

## 8. Post-Execution Audit & Verification

The Planner runs the automated audit on the generated code:

```powershell
pwsh .agents/skills/research-planner/scripts/validate_spec.ps1 -Mode Audit -AllowedFiles src/services/rate-limit.service.ts
```

**Output**:
```
Auditing code files: src/services/rate-limit.service.ts
✅ CODE AUDIT PASSED: Zero anti-slop markers found.
```

Next, the unit tests are executed:
```bash
pnpm exec vitest run tests/unit/rate-limit.service.test.ts
# Exit Code: 0 (Tests: 3 passed, 3 total)
```

---

## 9. Conclusion & Key Takeaways

1. **Zero Hallucinations**: Because the exact Lua script, Redis command (`eval`), types, and error handling were provided in the task packet, the 7B model had zero opportunity to hallucinate obsolete or non-existent methods.
2. **Zero Slop**: Because the prompt explicitly banned `TODO` comments and provided complete algorithmic steps, the model generated 100% production-ready code.
3. **Flawless Integration**: Because contracts were frozen in Stage 0, `TASK-003` (Fastify hook) wired seamlessly into `RateLimitService` without a single type mismatch.
