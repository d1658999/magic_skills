# Sample Master Technical Specification: API Rate Limiting Subsystem

> **Context**: Demonstrates a complete, frozen zero-inference technical specification produced during Phase 3 of the Research Planner lifecycle.

---

## 1. System Architecture & Component Map

### 1.1 Structural Diagram
```
Incoming HTTP Request
        │
        ▼
[Fastify onRequest Hook] (src/middleware/rate-limiter.ts)
        │
        ├── Extract Client IP / User ID & Route Limit Config
        │
        ▼
[RateLimitService] (src/services/rate-limit.service.ts)
        │
        ▼ (Execute Atomic Lua Script via ioredis)
[Redis Cluster: ZSET 'rl:{key}']
        │
        ├── Prune timestamps older than (now - windowMs)
        ├── Count cardinality
        └── If count < max: Add current timestamp, expire = windowSec + 1
        │
        ▼
Return RateLimitResult { allowed: boolean, remaining: number, resetSec: number }
        │
        ├── [If allowed == true]  ──► Set headers & call next handler
        └── [If allowed == false] ──► Set headers & throw HTTP 429 Too Many Requests
```

---

## 2. Frozen Data Contracts & Interfaces

```typescript
// TARGET FILE: src/types/rate-limit.ts

export interface RateLimitTierConfig {
  readonly maxRequests: number;      // Maximum requests permitted in window
  readonly windowSeconds: number;     // Sliding window size in seconds
}

export interface RateLimitCheckParams {
  readonly identifier: string;       // Normalized IP or user UUID
  readonly routeTier: string;        // 'auth' | 'public' | 'internal'
  readonly config: RateLimitTierConfig;
}

export interface RateLimitSuccessResult {
  readonly allowed: true;
  readonly limit: number;
  readonly remaining: number;
  readonly resetSeconds: number;
}

export interface RateLimitExceededResult {
  readonly allowed: false;
  readonly limit: number;
  readonly remaining: 0;
  readonly resetSeconds: number;
}

export type RateLimitResult = RateLimitSuccessResult | RateLimitExceededResult;
```

---

## 3. Algorithmic State Flow & Lua Script Specification (Atomic Redis Execution)

```lua
-- File: src/scripts/sliding-window.lua
-- KEYS[1]: Rate limit key, e.g. "rl:auth:192.168.1.1"
-- ARGV[1]: Current Unix timestamp in milliseconds
-- ARGV[2]: Window size in milliseconds
-- ARGV[3]: Maximum permitted requests in window
-- ARGV[4]: Key TTL in seconds (windowSeconds + 2)

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
```

---

## 4. Exhaustive Error & Edge Case Matrix

| Condition | Cause | Expected Action | Emitted Response / Status |
| :--- | :--- | :--- | :--- |
| **Normal Request** | Current hits < limit | Set `X-RateLimit-*` headers; proceed | HTTP 200 (or route handler output) |
| **Quota Exceeded** | Current hits >= limit | Set `Retry-After: {resetSec}` header; halt | HTTP 429 `{"error": "TOO_MANY_REQUESTS", "message": "Rate limit exceeded. Try again in X seconds."}` |
| **Missing IP Address** | Request from proxy without `x-forwarded-for` | Fallback to `req.socket.remoteAddress` or `'unknown-client'` | Process with `'public'` fallback bucket |
| **Redis Unreachable** | Redis timeout or ECONNREFUSED | Catch error, log structured warning `[RateLimiter] Redis failure; failing open`, allow request | Headers omitted or set to `X-RateLimit-Status: bypassed`; proceed with request |

---

## 5. Anti-Slop & Quality Constraints

1. **Zero Placeholders**: Do NOT leave `// TODO: connect redis` or mock returns.
2. **Fail-Open Requirement**: Wrapping the Redis call in a `try/catch` that logs and returns `{ allowed: true, limit: config.maxRequests, remaining: config.maxRequests, resetSeconds: 0 }` is mandatory.
3. **No `@ts-ignore`**: Use proper typing for Fastify request decorators.

---

## 6. Verification & Test Suite

```bash
# 1. Typecheck:
pnpm exec tsc --noEmit

# 2. Unit Test:
pnpm exec vitest run tests/unit/rate-limiter.test.ts

# 3. Anti-Slop Audit:
python .agents/skills/research-planner/scripts/validate_spec.py --mode audit --allowed-files src/types/rate-limit.ts src/services/rate-limit.service.ts
```
