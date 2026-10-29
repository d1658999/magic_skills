# Zero-Assumption Specification Writing Guide

When delegating tasks to subagents, **you must assume the subagent has zero prior context, limited reasoning initiative, and a tendency to take shortcuts if instructions are vague.**

A vague prompt forces the subagent to guess. When 4 parallel subagents guess independently, they invent 4 incompatible architectures. Your job as the Lead Orchestrator Agent is to eliminate all guessing before spawning a single subagent.

---

## 1. The "Smart Planner, Literal Worker" Principle

| Dimension | ❌ Bad (High-Assumption) Prompt | ✅ Good (Zero-Assumption) Spec |
| :--- | :--- | :--- |
| **Target Files** | "Add a rate limiter middleware to the API." | "Create `src/middleware/rateLimiter.ts` and export `createRateLimiter(config: RateLimitConfig)`." |
| **Data Contracts** | "Return an error when rate limit is exceeded." | "When count > `config.maxRequests`, return HTTP `429` with JSON body `{\"error\": \"RATE_LIMIT_EXCEEDED\", \"retryAfterMs\": <remainingMs>}` and header `Retry-After: <ceil(remainingMs/1000)>`." |
| **Dependencies** | "Use the existing cache utility." | "Import `TTLCache` from `src/utils/cache.ts` (see lines 12–48). Instantiate with `new TTLCache<string, WindowEntry>(config.windowMs)`." |
| **Scope Lock** | (Not mentioned—subagent randomly edits `src/server.ts` and breaks another subagent's work) | "**ALLOWED FILES**: `src/middleware/rateLimiter.ts`, `tests/middleware/rateLimiter.test.ts`. **FORBIDDEN**: Do NOT modify `src/server.ts` or `package.json`. Integration happens in Phase 5." |
| **Edge Cases** | "Handle edge cases properly." | "1) If `req.ip` is undefined, fallback to `req.headers['x-forwarded-for']` (first comma-separated token trimmed), else `'unknown'`. 2) If `config.maxRequests <= 0`, throw `RangeError('maxRequests must be > 0')` at initialization." |

---

## 2. Mandatory Pre-Planning Reconnaissance Checklist

Before writing any subagent spec, the Original Agent **must** complete these steps itself:

1. **Read Shared Types & Schemas**: Inspect the exact files defining models, interfaces, database schemas, or API payloads.
2. **Lock Shared Interfaces First**:
   - If Subagent 1 builds a Backend Service and Subagent 2 builds a Frontend Client or Consumer, **do not let them invent the interface independently**.
   - Either:
     - **(Preferred)** Create the shared types/interfaces file (`src/types/shared.ts`) yourself *before* spawning Subagents 1 and 2, OR
     - Embed the exact, character-for-character interface definition in both subagents' Work Packets.
3. **Partition File Ownership (Zero Overlap Rule)**:
   - Draw a File Ownership Matrix across all planned subagents.
   - **Rule**: No two concurrently running subagents in an `"inherit"` workspace may have write access to the same file (including `index.ts` barrel files, router registries, or `package.json`).
   - **Barrel/Registry File Pattern**: Have parallel subagents create their individual module files (`src/handlers/auth.ts`, `src/handlers/billing.ts`), and have the **Original Agent** wire them into `src/handlers/index.ts` or `src/router.ts` during Phase 5B after reviewing their work.

---

## 3. Anatomy of a Bulletproof Work Packet

Every subagent prompt must include these 8 sections:

### Section 1: Mission & Context Summary
- 2–3 sentences explaining what the overall project is doing and how this specific task fits in.

### Section 2: Strict Responsibility & File Boundary Lock
- **Write-Permitted Files**: Explicit list of files the subagent must create or edit.
- **Read-Only Reference Files**: Explicit list of existing files the subagent must read first to copy coding style, imports, and conventions.
- **Forbidden Files / Actions**: Explicit list of files the subagent must **not** edit, plus forbidden actions (e.g., "Do not install new npm packages", "Do not modify database migrations", "Do not run `git commit`").

### Section 3: Exact Signatures & Data Contracts
- Provide exact TypeScript/Python/Go/Rust type definitions, class names, method signatures, and export names.
- Never allow the subagent to rename exported symbols.

### Section 4: Step-by-Step Implementation Blueprint
Break the implementation into numbered, deterministic steps:
1. What imports to include.
2. What constants/helpers to define.
3. Exact business logic for each function (inputs -> validation -> transformation -> output).
4. How errors must be constructed, logged, and thrown/returned.

### Section 5: Exhaustive Edge-Case Matrix
Explicitly list boundary conditions the subagent might overlook:
- Empty arrays/strings, `null`/`undefined`/`None` values
- Zero, negative numbers, `NaN`, or overflow values
- Concurrent access / race conditions / idempotency
- Network/IO timeouts and partial failures
- Resource cleanup (`finally` blocks, closing handles/streams)

### Section 6: Unit Test Specification
Do not just say "Write unit tests." Specify the exact test cases required:
- Happy path test cases (with concrete sample inputs and expected outputs)
- Boundary and edge-case test cases
- Error/rejection test cases

### Section 7: Anti-Slop & Quality Rules
Explicitly prohibit common subagent failure modes:
- Zero `TODO`, `FIXME`, `HACK`, or `pass` placeholders
- Zero hardcoded dummy data where real logic is required
- Zero type suppression (`as any`, `@ts-ignore`, `# type: ignore`)
- Preserve all unrelated comments and docstrings in existing files

### Section 8: Self-Check & Deliverable Format
Give the subagent the exact command(s) to run before finishing, and require a structured completion report containing:
1. Every file created or modified
2. Verification command executed and its exact exit code / output summary
3. Confirmation that all edge cases and unit tests in the spec are implemented
4. Confirmation that no files outside the allowed list were modified
