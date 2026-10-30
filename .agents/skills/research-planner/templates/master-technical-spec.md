# Master Technical Specification (Zero-Inference Spec)

> **Artifact Purpose**: Complete, frozen architectural and implementation specification produced during Phase 3 of the Research Planner lifecycle. Contains 100% of the types, interfaces, state flows, edge-case tables, and step-by-step logic required so that low-tier executor models have zero architectural decisions to make.

---

## 1. System Architecture & Component Map

### 1.1 Structural Diagram
```
[Client / API Caller]
        │
        ▼ (HTTPS Request)
[Route Controller] (src/routes/...)
        │
        ▼ (Validated DTO)
[Service Layer] (src/services/...) ◄──► [Domain Types] (src/types/...)
        │
        ├──► [Data Access / Repository] (src/repositories/...)
        │           │
        │           ▼
        │      [Database / Cache]
        │
        └──► [External Client / Helper] (src/clients/...)
```

### 1.2 Module Directory & File Manifest
| Target Path | Action | Single Responsibility |
| :--- | :--- | :--- |
| `src/types/auth.ts` | `CREATE` | Frozen interfaces, DTOs, and error types |
| `src/services/token.service.ts` | `CREATE` | Pure algorithmic token generation & validation |
| `src/repositories/token.repo.ts` | `CREATE` | Redis-backed token storage & revocation |
| `src/routes/auth.controller.ts` | `MODIFY` | Wire new token service into HTTP request handlers |

---

## 2. Frozen Data Contracts & Interfaces

> [!IMPORTANT]
> The executor model MUST NOT alter, rename, or omit any fields in these definitions. Copy them verbatim into the target files.

### 2.1 Domain Models & Interfaces
```typescript
// TARGET FILE: src/types/auth.ts

export interface UserSessionClaims {
  readonly sub: string;           // Unique user UUID
  readonly email: string;         // Normalized email address
  readonly role: 'user' | 'admin';// User authorization role
  readonly jti: string;           // Unique token identifier (UUID v4)
  readonly exp: number;          // Unix epoch expiration in seconds
  readonly iat: number;          // Unix epoch issue timestamp in seconds
}

export interface TokenPairResult {
  readonly accessToken: string;
  readonly refreshToken: string;
  readonly expiresInSeconds: number;
  readonly tokenType: 'Bearer';
}

export interface TokenValidationSuccess {
  readonly isValid: true;
  readonly claims: UserSessionClaims;
}

export interface TokenValidationFailure {
  readonly isValid: false;
  readonly reason: 'EXPIRED' | 'INVALID_SIGNATURE' | 'REVOKED' | 'MALFORMED';
  readonly errorMessage: string;
}

export type TokenValidationResult = TokenValidationSuccess | TokenValidationFailure;
```

### 2.2 Input DTO Validation Schemas
```typescript
// Zod / JSON Schema definition if applicable
import { z } from 'zod';

export const RefreshTokenRequestSchema = z.object({
  refreshToken: z.string().min(1, 'Refresh token cannot be empty'),
});

export type RefreshTokenRequest = z.infer<typeof RefreshTokenRequestSchema>;
```

---

## 3. Algorithmic State Machines & Logic Workflows

### 3.1 Token Refresh State Transition
```
State: IDLE
  │
  ├── Request received: { refreshToken }
  ▼
State: PARSE_INPUT
  ├── [If missing/empty] ───────────────► RETURN HTTP 400 Bad Request
  └── [If valid string format] ────────► State: VERIFY_SIGNATURE
                                                │
  ┌─────────────────────────────────────────────┘
  ▼
State: VERIFY_SIGNATURE
  ├── [Signature invalid / malformed] ──► RETURN HTTP 401 Unauthorized ("MALFORMED")
  ├── [Token expired (iat/exp)] ────────► RETURN HTTP 401 Unauthorized ("EXPIRED")
  └── [Cryptographically valid] ───────► State: CHECK_REVOCATION_STORE
                                                │
  ┌─────────────────────────────────────────────┘
  ▼
State: CHECK_REVOCATION_STORE
  ├── [Key 'blacklist:<jti>' exists] ───► RETURN HTTP 401 Unauthorized ("REVOKED")
  └── [Not blacklisted] ────────────────► State: ROTATE_TOKENS
                                                │
  ┌─────────────────────────────────────────────┘
  ▼
State: ROTATE_TOKENS
  ├── Atomically blacklist old jti in Redis (TTL = remaining exp)
  ├── Issue new accessToken (TTL = 900s)
  ├── Issue new refreshToken (TTL = 604800s)
  └── RETURN HTTP 200 OK with TokenPairResult
```

### 3.2 Detailed Step-by-Step Execution Recipes
> Low-tier models cannot deduce nuanced algorithmic sequences. Write out the exact numbered steps:

#### Method: `TokenService.generateTokenPair(claims: Omit<UserSessionClaims, 'jti' | 'iat' | 'exp'>): Promise<TokenPairResult>`
1. Generate a new cryptographically secure UUID v4 string for `jti` using `crypto.randomUUID()`.
2. Compute `iat = Math.floor(Date.now() / 1000)`.
3. Compute `exp = iat + 900` (15 minutes).
4. Sign `accessToken` with `JWT_SECRET` using `HS256` algorithm.
5. Generate a secondary secure random token for `refreshToken` using `crypto.randomBytes(32).toString('hex')`.
6. Store `refreshToken` in Redis store with key `refresh:<refreshToken>` mapped to `claims.sub` and TTL of 7 days.
7. Return `{ accessToken, refreshToken, expiresInSeconds: 900, tokenType: 'Bearer' }`.

---

## 4. Exhaustive Error & Edge Case Matrix

| Condition | Triggering Input / Event | Exact Error Class / Status | Required Error Message / Response Body |
| :--- | :--- | :--- | :--- |
| **Missing Header** | No `Authorization` header provided | `UnauthorizedError` / 401 | `{"error": "MISSING_AUTH_HEADER", "message": "Authorization header is required"}` |
| **Malformed Prefix** | Header is `Token abc` instead of `Bearer abc` | `UnauthorizedError` / 401 | `{"error": "INVALID_AUTH_FORMAT", "message": "Authorization format must be Bearer <token>"}` |
| **Expired Token** | `exp < current_timestamp` | `TokenExpiredError` / 401 | `{"error": "TOKEN_EXPIRED", "message": "Access token has expired"}` |
| **Tampered Signature** | Hash mismatch in JWT | `JsonWebTokenError` / 401 | `{"error": "INVALID_TOKEN", "message": "Token signature is invalid"}` |
| **Database Downtime** | Redis connection drops during check | `ServiceUnavailableError` / 503 | `{"error": "AUTH_STORE_UNAVAILABLE", "message": "Authentication service temporarily degraded"}` |

---

## 5. Anti-Slop Constraints & Codebase Quality Invariants

The executor model MUST strictly observe the following rules:

1. **Zero Placeholders**: Any occurrence of `// TODO`, `/* FIXME */`, `# pass`, `throw new Error("unimplemented")`, or placeholder data will trigger an automatic rejection.
2. **Strict Typing**:
   - TypeScript: Never use `any`, `unknown` (unless immediately refined with type guards), or `@ts-ignore`.
   - Python: All functions must have complete `type annotations` and satisfy `mypy --strict`.
3. **No Silent Error Swallowing**: Empty `catch {}` or `except Exception: pass` blocks are strictly forbidden. All errors must be handled, wrapped, or re-thrown.
4. **Scope Isolation**: Do NOT touch any file not explicitly listed in the task packet. Do not reformat unrelated functions or update project dependencies.

---

## 6. Verification & Test Plan

### 6.1 Required Unit Tests
- `src/services/__tests__/token.service.test.ts`:
  - `test('generateTokenPair returns valid tokens with correct expiration')`
  - `test('validateToken returns isValid=true for valid unexpired token')`
  - `test('validateToken returns isValid=false with reason=EXPIRED when exp is in past')`
  - `test('validateToken returns isValid=false with reason=MALFORMED on garbage input')`

### 6.2 Deterministic Verification Commands
```bash
# 1. Typecheck the entire project
npx tsc --noEmit

# 2. Run the isolated test file
npm test -- src/services/__tests__/token.service.test.ts

# 3. Check for forbidden placeholders
pwsh .agents/skills/research-planner/scripts/validate_spec.ps1 -AuditTarget src/services/token.service.ts
```
