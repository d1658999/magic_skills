# Requirements Research Dossier

> **Artifact Purpose**: Comprehensive synthesis of user intent, problem domain research, target codebase reconnaissance, negative constraints, and feasibility assessment produced during Phases 1 & 2 of the Research Planner lifecycle.

---

## 1. Executive Summary & Objective

- **Project / Goal Title**: [e.g., Migration of Session Auth to Stateless JWT with Refresh Tokens]
- **Target Execution Engine**: [e.g., Local Qwen2.5-Coder-7B / Flash-Lite / Copilot CLI / Autonomous Subagent]
- **Lead Planner**: [Agent Name / ID]
- **Date / Timestamp**: [YYYY-MM-DD]
- **Executive Mission Statement**:
  > [One concise paragraph explaining what needs to be accomplished, the high-level business/technical justification, and the definition of done.]

---

## 2. 360° Requirements Breakdown

### 2.1 Functional Requirements (Explicit "Must-Haves")
| ID | Requirement Statement | Input | Expected Output / Effect | Priority (P0/P1/P2) |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | [e.g., Validate incoming refresh token against Redis store] | `refreshToken: string` | Valid `SessionClaims` or throws `TokenExpiredError` | P0 |
| **FR-02** | [e.g., Issue dual tokens (access + refresh) upon valid credentials] | `UserCredentials` | `{ accessToken, refreshToken, expiresIn }` | P0 |
| **FR-03** | [e.g., Gracefully revoke user tokens on password reset] | `userId: string` | All user sessions invalidated in Redis | P1 |

### 2.2 Negative Requirements (Explicit "Must-NOTs" & Boundaries)
| ID | Prohibited Action / Constraint | Technical Reason / Risk | Enforcement Mechanism |
| :--- | :--- | :--- | :--- |
| **NR-01** | [e.g., Must NOT store plain JWT secrets in repository code] | Security / Credential leak risk | Environment variables only; automated regex check in CI |
| **NR-02** | [e.g., Must NOT break legacy `/api/v1/login` cookie response] | Backward compatibility for mobile v1 | Middleware must support dual emission of cookies and JSON headers |
| **NR-03** | [e.g., Must NOT introduce third-party crypto libraries beyond `jose` or Node native `crypto`] | Supply chain attack surface / bloat | Package lock audit |

### 2.3 Implicit Contracts & Invariants
- **Nullability & Empty States**: [e.g., Missing token in Authorization header must return 401 Unauthorized, never 500.]
- **Concurrency & Idempotency**: [e.g., Refresh token rotation must tolerate 15-second grace window for concurrent requests.]
- **Encoding & Payloads**: [e.g., UTF-8 only; payload must strictly not exceed 4KB.]
- **Performance Threshold**: [e.g., Token generation must complete in < 5ms (P99); verification in < 2ms.]

---

## 3. Ground-Truth Codebase Reconnaissance

### 3.1 Repository Architecture & Active Tech Stack
- **Language & Runtime**: [e.g., TypeScript 5.4 / Node.js v20.12.0 LTS (ESM)]
- **Framework & Libraries**: [e.g., Fastify v4.26, Prisma ORM v5.11, Zod v3.22]
- **Build / Packaging Tool**: [e.g., pnpm v9.0, tsc]
- **Active Test Framework**: [e.g., Vitest v1.4, supertest v6.3]

### 3.2 Key File Locations & Role Map
| File Path (Workspace Relative) | Role in Codebase | Read-Only or Modification Target |
| :--- | :--- | :--- |
| `src/core/auth/token-service.ts` | Existing legacy session service | Target for refactoring |
| `src/core/auth/interfaces.ts` | Shared authentication domain types | Target for new interface definitions |
| `src/routes/auth.routes.ts` | HTTP API routes | Target for endpoint wiring |
| `src/config/env.ts` | Validated environment schema | Target for JWT config keys |
| `tests/helpers/test-db.ts` | Test harness database setup | Read-only reference |

### 3.3 Harvested Code Conventions & Exemplars
> Provide 1–2 real snippets from the codebase that show the exact style (error handling, type validation, async/await patterns) that executor models must emulate.

```typescript
// Exemplar from src/core/users/user-service.ts
export async function findUserById(id: string): Promise<UserResult> {
  const user = await prisma.user.findUnique({ where: { id } });
  if (!user) {
    throw new NotFoundError(`User with id '${id}' does not exist.`);
  }
  return sanitizeUser(user);
}
```

### 3.4 Active Verification Commands
- **Linter**: `[e.g., pnpm run lint]`
- **Typecheck**: `[e.g., pnpm run typecheck --noEmit]`
- **Unit Tests**: `[e.g., pnpm test -- src/core/auth]`
- **Integration Tests**: `[e.g., pnpm test:e2e -- auth]`

---

## 4. Technical Feasibility & External Dependency Research

### 4.1 Dependency Audit & Version Locking
| Package Name | Installed Version | Target APIs to Use | Deprecated / Broken APIs to Avoid |
| :--- | :--- | :--- | :--- |
| `jose` | `^5.2.3` | `SignJWT`, `jwtVerify` | Do NOT use legacy `jsonwebtoken` (CommonJS / sync methods) |
| `ioredis` | `^5.3.2` | `client.set(key, val, 'EX', sec)` | Do NOT use deprecated callback syntax |

### 4.2 Platform & Sandbox Quirks
- **OS / Shell**: [e.g., Windows 11 with PowerShell 7 / Linux POSIX paths]
- **File System**: [e.g., Case-insensitive file paths on Windows; normalize to forward slashes in code]
- **Network Isolation**: [e.g., Execution sandbox has no external internet; all packages must be pre-installed or vendored]

---

## 5. Risk Register & Mitigation Strategy

| Risk ID | Potential Failure / Pitfall | Impact | Likelihood | Pre-Planned Mitigation in Spec |
| :--- | :--- | :--- | :--- | :--- |
| **R-01** | Low-tier model writes `any` for JWT payload | High | High | Pre-define strict `JWTPayload` interface in `interfaces.ts` before dispatch. |
| **R-02** | Refresh token race condition under high load | Med | Med | Implement atomic Lua script in Redis for token exchange. |
| **R-03** | Model forgets to export new functions | High | Med | Include index export verification command in the task packet. |
