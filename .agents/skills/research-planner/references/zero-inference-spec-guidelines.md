# Zero-Inference Specification Guidelines

> **Reference Purpose**: Practical guide for authoring technical specifications that leave zero degrees of architectural freedom, preventing hallucination, cognitive drift, and shortcut-taking by lower-tier AI models.

---

## 1. What is "Zero-Inference"?

In traditional software development, a senior engineer often gives a junior engineer high-level guidance: *"Add an authentication check here and handle errors gracefully."* The human junior engineer relies on institutional memory, common sense, and asking questions to fill in the blanks.

**Lower-tier AI models (7B–14B models, Flash-Lite, Haiku, Copilot CLI) possess neither institutional memory nor common sense.**
When an AI model encounters an ambiguity, it does not stop to reflect—it guesses. It generates plausible-looking code that often:
- Uses imaginary library methods.
- Invents new data structures that clash with existing code.
- Swallows exceptions silently.
- Inserts placeholder comments like `// TODO: add validation`.

A **Zero-Inference Specification** is written such that **any two independent AI models (or technicians) following the spec will produce functionally identical code**. Every choice—file location, function signature, parameter types, error handling, edge cases, and verification commands—is resolved up front by the Research Planner.

---

## 2. High-Inference (Bad) vs. Zero-Inference (Good) Phrasing

The following contrast matrix illustrates how vague prompts must be translated into deterministic instructions:

| High-Inference / Slop-Inducing (DO NOT USE) | Zero-Inference / Deterministic (MANDATORY) |
| :--- | :--- |
| *"Implement token verification with appropriate error handling."* | *"Implement `verifyToken(token: string): Promise<TokenResult>`. If `token` is empty, return `{ valid: false, error: 'EMPTY_TOKEN' }`. Call `jose.jwtVerify(token, key)`. Catch `JWTExpired` and return `{ valid: false, error: 'EXPIRED' }`. Catch all other errors and return `{ valid: false, error: 'INVALID' }`."* |
| *"Save the user session to the cache with a reasonable TTL."* | *"Call `redisClient.set(\`session:${sessionId}\`, JSON.stringify(sessionData), 'EX', 86400)`. Throw `StorageConnectionError` if `redisClient` rejects."* |
| *"Add authentication routes to the API."* | *"In `src/routes/auth.routes.ts`, register `POST /api/v1/auth/refresh` using Fastify schema `RefreshTokenSchema`. Route handler must invoke `authService.refreshToken(request.body.refreshToken)` and respond with HTTP 200 `{ accessToken, expiresIn: 900 }` on success or HTTP 401 on `AuthError`."* |
| *"Write unit tests covering edge cases."* | *"In `src/services/__tests__/token.test.ts`, write 3 test cases: 1) Valid token returns decoded claims; 2) Expired token returns error code 'EXPIRED'; 3) Garbage string returns error code 'INVALID'. Use fixture `TEST_JWT_SECRET = 'secret123'`."* |
| *"Refactor the file to follow project conventions."* | *"Replace lines 42–68 with the provided snippet below, keeping all import statements and existing export names unchanged."* |

---

## 3. The 6 Rules of Zero-Inference Authoring

### Rule 1: Ban Subjective Adjectives & Vague Directives
Never use the following words in instructions to lower-tier models:
- ❌ *Appropriate, reasonable, proper, elegant, clean, robust, graceful, optimal, standard.*
- **Instead**: Specify the exact numbers, types, status codes, algorithms, and timeouts.

### Rule 2: Concrete Types Over Open Shapes
Never leave types ambiguous:
- ❌ `data: any`, `payload: object`, `options?: Record<string, any>`
- **Instead**: Write out the full interface with all required and optional properties:
  ```typescript
  interface SessionPayload {
    userId: string;
    roles: Array<'admin' | 'member'>;
    issuedAtEpochSeconds: number;
  }
  ```

### Rule 3: Enumerate Every Branch Explicitly
Never leave fallthrough or default states unhandled:
- ❌ *"Handle success, and handle failure cases accordingly."*
- **Instead**: Enumerate all possible conditions in a table:
  1. Input is null -> Return Error A.
  2. Input matches regex -> Process Step 2.
  3. Input does not match regex -> Return Error B.
  4. Remote call times out (> 3000ms) -> Throw Error C.

### Rule 4: Pin Library APIs and Signatures Verbatim
Do not expect small models to remember API signatures across different library versions (e.g., `jose` v4 vs v5, `pnpm` vs `npm`, `Fastify` v3 vs v4):
- Provide the exact import statement: `import { SignJWT } from 'jose';`
- Provide the exact method call syntax and options.

### Rule 5: Anchor Modifications with Context Lines
Small models lose spatial orientation when editing large files:
- Specify the exact target line number.
- Provide 2–3 preceding lines of code (anchors) and 2–3 succeeding lines of code so the model can locate the exact insertion block.

### Rule 6: Mechanistic Pass/Fail Criteria
Never instruct a model: *"Test your code to make sure it works."*
- Provide the exact shell command: `npm test -- tests/auth/token.test.ts`
- State the required exit code: `0`
- State the expected output keyword: `PASS`
