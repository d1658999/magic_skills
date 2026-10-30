# Atomic Task Packet

> **Artifact Purpose**: Self-contained, zero-inference execution packet for a single atomic task. Tailored specifically for low-tier, small-parameter (7B–14B), or literal AI models. Contains 100% of required context, line anchors, logic recipes, and deterministic verification commands.

---

## Task Metadata
- **Task ID**: `TASK-[001]`
- **Task Title**: [e.g., Implement TokenValidator.verifyClaims Method]
- **Target Execution Model**: [e.g., Ollama Qwen2.5-Coder-7B / Flash-Lite / Copilot CLI]
- **Target File**: `[src/services/token-validator.ts]`
- **Action Type**: `[CREATE_NEW_FILE | MODIFY_EXISTING_FILE]`
- **Maximum Expected Diff**: `[< 80 lines]`

---

## 1. Single-Sentence Objective
> [State exactly what the model must accomplish in one concise sentence without jargon or ambiguity.]
> *Example: Implement the `verifyClaims` function in `src/services/token-validator.ts` that validates JWT signature and expiration, returning a typed `TokenValidationResult`.*

---

## 2. File Access Boundaries (Strict Whitelist)

### 2.1 Permitted Write Targets (Allowed to Create or Modify)
- `[src/services/token-validator.ts]` (ONLY this file)

### 2.2 Read-Only Reference Files (Inspect for patterns/types)
- `[src/types/auth.ts]` (Lines 1–45) - Shared domain interfaces
- `[src/config/jwt.config.ts]` (Lines 10–25) - Configuration accessor

### 2.3 Strictly Forbidden Files (Do NOT touch or modify)
- Any file in `src/routes/`
- Any file in `src/repositories/`
- `package.json`, `tsconfig.json`, or root configurations
- **Any file not explicitly listed in Section 2.1**

---

## 3. Code Location & Insertion Anchors (For Modifications)

> [!NOTE]
> If creating a new file, skip this section and provide full file content structure below.

- **Target File**: `src/services/token-validator.ts`
- **Insertion Point**: Immediately after line 42 (after `const JWT_SECRET = getJwtSecret();`)
- **Preceding Context Lines (Anchors)**:
  ```typescript
  // Line 40:
  import { getJwtSecret } from '../config/jwt.config';
  // Line 41:
  const JWT_SECRET = getJwtSecret();
  // Line 42:
  // --- INSERT FUNCTION HERE ---
  ```

---

## 4. Required Verbatim Imports & Types

Copy these exact import statements at the top of the file:
```typescript
import { jwtVerify, JWTPayload } from 'jose';
import { UserSessionClaims, TokenValidationResult } from '../types/auth';
import { getJwtSecret } from '../config/jwt.config';
```

---

## 5. Step-by-Step Implementation Recipe

Follow these exact steps in order. Do not skip or reorder:

1. Define and export the asynchronous function `verifyTokenClaims(rawToken: string): Promise<TokenValidationResult>`.
2. Check if `rawToken` is empty, undefined, or not a string. If so, return immediately:
   ```typescript
   return {
     isValid: false,
     reason: 'MALFORMED',
     errorMessage: 'Token string must not be empty.'
   };
   ```
3. Wrap the verification block in a `try / catch` structure.
4. Inside the `try` block:
   - Convert `getJwtSecret()` to a `Uint8Array` using `new TextEncoder().encode(getJwtSecret())`.
   - Call `await jwtVerify(rawToken, secretKey, { algorithms: ['HS256'] })`.
   - Extract the payload: `const payload = result.payload as unknown as UserSessionClaims`.
   - Validate that required claims exist: `payload.sub`, `payload.email`, and `payload.role`.
   - If valid, return:
     ```typescript
     return {
       isValid: true,
       claims: payload
     };
     ```
5. Inside the `catch (error: any)` block:
   - Check if `error?.code === 'ERR_JWT_EXPIRED'`:
     ```typescript
     return { isValid: false, reason: 'EXPIRED', errorMessage: 'The provided token has expired.' };
     ```
   - Check if `error?.code === 'ERR_JWS_SIGNATURE_VERIFICATION_FAILED'`:
     ```typescript
     return { isValid: false, reason: 'INVALID_SIGNATURE', errorMessage: 'Invalid token cryptographic signature.' };
     ```
   - For all other errors, return:
     ```typescript
     return { isValid: false, reason: 'MALFORMED', errorMessage: error?.message || 'Token verification failed.' };
     ```

---

## 6. Reference Exemplar (Follow This Exact Style)

```typescript
// Exemplar from src/services/user-validator.ts
export async function validateUserStatus(userId: string): Promise<ValidationResult> {
  if (!userId || typeof userId !== 'string') {
    return { isValid: false, reason: 'INVALID_INPUT', errorMessage: 'User ID is required' };
  }
  try {
    const user = await db.user.findUnique({ where: { id: userId } });
    if (!user) {
      return { isValid: false, reason: 'NOT_FOUND', errorMessage: 'User not found' };
    }
    return { isValid: true, data: user };
  } catch (err: any) {
    return { isValid: false, reason: 'DATABASE_ERROR', errorMessage: err.message };
  }
}
```

---

## 7. Prohibited Patterns (Anti-Slop Ban)

- ❌ **NO PLACEHOLDERS**: Do NOT write `// TODO`, `/* FIXME */`, `# pass`, or return dummy/mock data.
- ❌ **NO ANY CASTS**: Do NOT cast types to `any` (e.g. `(claims as any)`). Use the provided `UserSessionClaims` interface.
- ❌ **NO CONSOLE LOGGING IN PROD CODE**: Do NOT use `console.log` or `console.error`. Use the structured logger or return errors in the result object.
- ❌ **NO UNREQUESTED REFACTORING**: Do NOT touch other functions in `token-validator.ts`. Only add `verifyTokenClaims`.

---

## 8. Deterministic Verification Command

Execute this exact command in the terminal to verify your implementation:

```bash
# Verify TypeScript compiles with no errors:
npx tsc --noEmit

# Run the dedicated unit test for this function:
npm test -- src/services/__tests__/token-validator.test.ts
```

### Expected Output & Exit Code:
- **Exit Code**: `0`
- **Terminal Output Contains**: `PASS src/services/__tests__/token-validator.test.ts`
- **Failure Condition**: Any compiler error or failed test assertion means the task is incomplete. Fix the implementation until the command exits 0.

---

## 9. Completion Report Format

When you finish, reply with ONLY this format:

```markdown
### Task Completion Report: [TASK-ID]
- **Target File Modified**: `[path]`
- **Verification Command Executed**: `[exact command]`
- **Exit Code**: `[0]`
- **Summary of Changes**:
  - Implemented `verifyTokenClaims` according to the recipe.
  - Zero placeholder markers or `any` casts used.
  - Verified tests pass cleanly.
```
