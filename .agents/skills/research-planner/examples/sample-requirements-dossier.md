# Sample Requirements Research Dossier: API Rate Limiting Subsystem

> **Context**: Demonstrates a real-world, completed Requirements Research Dossier produced by the Research Planner before designing an API rate-limiting subsystem.

---

## 1. Executive Summary & Objective

- **Project / Goal Title**: High-Performance Sliding-Window API Rate Limiting with Redis
- **Target Execution Engine**: Local Ollama Qwen2.5-Coder-7B & Claude Haiku subagents
- **Lead Planner**: Research Planner Agent
- **Date / Timestamp**: 2026-10-30
- **Executive Mission Statement**:
  Implement an in-memory sliding-window log rate limiter using Redis for the Fastify REST API. The limiter must protect against DDoS and credential stuffing attacks on `/api/v1/auth/*` (5 req/min) and `/api/v1/users/*` (60 req/min), emit RFC 6585 headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`), and fail-open gracefully with structured error logging if Redis becomes unreachable.

---

## 2. 360° Requirements Breakdown

### 2.1 Functional Requirements (Explicit "Must-Haves")
| ID | Requirement Statement | Input | Expected Output / Effect | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Track request timestamps in Redis Sorted Set (`ZSET`) | `key: string, nowMs: number, windowMs: number` | Atomically prunes expired items and counts active hits | P0 |
| **FR-02** | Reject requests exceeding route tier limits with HTTP 429 | `IncomingMessage` | HTTP 429 Too Many Requests with RFC 6585 headers | P0 |
| **FR-03** | Provide route-level decorator for overriding default limits | `FastifyRouteConfig` | Custom `rateLimit: { max: number, windowSec: number }` | P1 |

### 2.2 Negative Requirements (Explicit "Must-NOTs" & Boundaries)
| ID | Prohibited Action / Constraint | Technical Reason | Enforcement Mechanism |
| :--- | :--- | :--- | :--- |
| **NR-01** | Must NOT block or drop traffic if Redis disconnects | High availability requirement: API must fail-open on cache failure | Try/catch around Redis calls with fallback to allow traffic |
| **NR-02** | Must NOT use multi-roundtrip Redis commands (`WATCH`/`MULTI`/`EXEC`) | Network latency overhead; race conditions under high concurrency | Single atomic Lua script executed via `EVAL` |
| **NR-03** | Must NOT add third-party plugins like `@fastify/rate-limit` | Custom enterprise token-bucket requirement; zero external npm bloat | Pure internal implementation with existing `ioredis` |

### 2.3 Implicit Contracts & Invariants
- **Key Partitioning**: Keys must be scoped as `rl:{tier}:{ip_address_or_user_id}`.
- **Header Standards**:
  - `X-RateLimit-Limit`: Maximum allowed requests in current window.
  - `X-RateLimit-Remaining`: Remaining quota in current window (minimum 0).
  - `Retry-After`: Seconds until quota resets when 429 is emitted.
- **Latency Budget**: Rate limit check must execute in < 2.0ms at P99.

---

## 3. Ground-Truth Codebase Reconnaissance

### 3.1 Repository Architecture & Active Tech Stack
- **Language & Runtime**: TypeScript 5.4 / Node.js v20.12 LTS (ESM)
- **Framework & Libraries**: Fastify v4.26, ioredis v5.3.2
- **Build & Test Tools**: pnpm 9.0, Vitest v1.4

### 3.2 Key File Locations
| File Path (Workspace Relative) | Role in Codebase | Action Target |
| :--- | :--- | :--- |
| `src/types/rate-limit.ts` | Shared rate limit interfaces | CREATE |
| `src/infrastructure/redis.ts` | Existing Redis singleton client | READ-ONLY REFERENCE |
| `src/middleware/rate-limiter.ts` | Fastify `onRequest` hook | CREATE |
| `src/scripts/sliding-window.lua` | Atomic Redis Lua script | CREATE |
| `tests/unit/rate-limiter.test.ts` | Unit test suite | CREATE |

### 3.3 Harvested Code Conventions & Exemplars
```typescript
// Exemplar from src/middleware/cors.ts
import { FastifyReply, FastifyRequest, HookHandlerDoneFunction } from 'fastify';

export function corsHook(req: FastifyRequest, reply: FastifyReply, done: HookHandlerDoneFunction): void {
  reply.header('Access-Control-Allow-Origin', '*');
  done();
}
```

### 3.4 Active Verification Commands
- **Typecheck**: `pnpm exec tsc --noEmit`
- **Targeted Test**: `pnpm exec vitest run tests/unit/rate-limiter.test.ts`
- **Lint**: `pnpm exec eslint src/middleware/rate-limiter.ts`

---

## 4. Technical Feasibility & External Dependency Research

### 4.1 Dependency Audit & Version Locking
- `ioredis` is installed at `^5.3.2`.
- `ioredis.defineCommand` is the recommended method for caching pre-compiled Lua scripts on the Redis server (`EVALSHA` optimization).

---

## 5. Risk Register & Mitigation Strategy

| Risk ID | Potential Failure | Impact | Mitigation in Spec |
| :--- | :--- | :--- | :--- |
| **R-01** | Redis memory leak from unbounded ZSET keys | High | Include explicit `EXPIRE key windowSeconds` inside the Lua script. |
| **R-02** | Weak model forgets to call Fastify `done()` callback | High | Use async/await Fastify hook signature instead of done callback. |
