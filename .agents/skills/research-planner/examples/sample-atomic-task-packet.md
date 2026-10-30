# Sample Atomic Task Packet: TASK-002 (RateLimitService Implementation)

> **Context**: Demonstrates a complete, dispatch-ready task packet for a lower-tier AI model. Implements `RateLimitService.checkLimit` using the pre-compiled Redis Lua script.

---

## Task Metadata
- **Task ID**: `TASK-002`
- **Task Title**: Implement RateLimitService.checkLimit with Fail-Open Redis Logic
- **Target Execution Model**: Ollama Qwen2.5-Coder-7B / Flash-Lite / Copilot CLI
- **Target Permitted Write File**: `src/services/rate-limit.service.ts`
- **Action Type**: `CREATE_NEW_FILE`
- **Maximum Expected Diff**: `< 95 lines`

---

## 1. Single-Sentence Objective
Implement and export the `RateLimitService` class in `src/services/rate-limit.service.ts` that executes an atomic sliding-window check via `ioredis` and fails open with a fallback result if Redis throws an exception.

---

## 2. File Access Boundaries (Strict Whitelist)

### 2.1 Permitted Write Targets
- `src/services/rate-limit.service.ts` (ONLY this file)

### 2.2 Read-Only Reference Files
- `src/types/rate-limit.ts` (Lines 1–32) - Domain types and `RateLimitResult`
- `src/infrastructure/redis.ts` (Lines 1–20) - Redis client instance

### 2.3 Strictly Forbidden Files
- `src/types/rate-limit.ts` (DO NOT EDIT)
- `src/middleware/*`
- `package.json` or `tsconfig.json`

---

## 3. Required Verbatim Imports

```typescript
import { Redis } from 'ioredis';
import {
  RateLimitCheckParams,
  RateLimitResult,
  RateLimitSuccessResult,
  RateLimitExceededResult
} from '../types/rate-limit';
```

---

## 4. Step-by-Step Implementation Recipe

Follow these exact steps in order:

1. Define and export the class `RateLimitService`.
2. Add a `constructor(private readonly redis: Redis)` that stores the Redis client instance.
3. Define the public async method `checkLimit(params: RateLimitCheckParams): Promise<RateLimitResult>`.
4. Inside `checkLimit`:
   - Compute `key = 'rl:' + params.routeTier + ':' + params.identifier`.
   - Compute `nowMs = Date.now()`.
   - Compute `windowMs = params.config.windowSeconds * 1000`.
   - Compute `ttlSec = params.config.windowSeconds + 2`.
5. Wrap the Redis call in a `try / catch (error)` block:
   - In `try`:
     - Execute the Lua script using `await this.redis.eval(...)`:
       ```typescript
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
       ```
   - In `catch (err)`:
     - Log a warning using `console.warn('[RateLimitService] Redis check failed; failing open:', err);`
     - Fail open by returning:
       ```typescript
       return {
         allowed: true,
         limit: params.config.maxRequests,
         remaining: params.config.maxRequests,
         resetSeconds: 0
       };
       ```

---

## 5. Prohibited Patterns (Anti-Slop Ban)

- ❌ NO `TODO`, `FIXME`, or placeholder stubs.
- ❌ NO `any` types for function parameters or return types.
- ❌ DO NOT drop the `try / catch` fail-open fallback.
- ❌ DO NOT modify any file other than `src/services/rate-limit.service.ts`.

---

## 6. Deterministic Verification Command

Run this command in the terminal to verify compilation and unit tests:

```bash
# Run unit test targeting RateLimitService:
pnpm exec vitest run tests/unit/rate-limit.service.test.ts
```

### Expected Output:
- Exit Code: `0`
- Terminal includes: `1 passed`

---

## 7. Completion Report

Respond only with:
- Task ID: `TASK-002`
- Modified File: `src/services/rate-limit.service.ts`
- Exit Code: `0`
- Confirmation: All steps implemented with fail-open Redis logic; zero placeholders; tests pass.
