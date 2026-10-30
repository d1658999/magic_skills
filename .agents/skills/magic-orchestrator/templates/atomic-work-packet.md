# Work Packet: [WP-ID] - [Single Sentence Objective]

> **Parent Change / Spec**: [Path to Master Dossier or OpenSpec change]  
> **Assigned Engine**: [collama | ollama-copilot | ollama-copilot_2 | agy-subagent]  
> **Status**: READY_FOR_DISPATCH  

---

## 1. Strict Responsibility Boundary (Scope Lock)

You are an atomic code implementation technician. You must adhere strictly to these file boundaries:

- **ALLOWED TO CREATE OR MODIFY**:
  - `path/to/target/file1.ts`
  - `tests/path/to/target/file1.test.ts`
- **READ-ONLY REFERENCE FILES (Follow style & patterns, DO NOT EDIT)**:
  - `path/to/existing/exemplar.ts` (Lines 1–100)
  - `path/to/existing/types.ts`
- **STRICTLY FORBIDDEN (DO NOT TOUCH OR MODIFY)**:
  - Any file outside the above list.
  - Package manifests (`package.json`, `Cargo.toml`, `requirements.txt`).
  - Configuration files (`tsconfig.json`, `.env`, Dockerfile).

---

## 2. Technical Specification & Code Anchors

### 2.1 Interface & Types to Implement
```typescript
// EXACT signatures you must implement without modifications:
export interface TargetModule {
  executeAction(input: TargetInput): Promise<TargetResult>;
}
```

### 2.2 Algorithmic Logic (Step-by-Step)
1. Step 1: Validate `input` against boundary invariants. If invalid, throw `ValidationError`.
2. Step 2: Compute hash or transform using [Specific Function].
3. Step 3: Return immutable `TargetResult` object with computed metadata.

### 2.3 Required Error Handling & Edge Cases
- If input is `null`, `undefined`, or empty string `""`, throw `InvalidInputException("Input must not be empty")`.
- If numeric parameter is $\le 0$, return status code 400.
- All asynchronous calls must have timeout and error wrapping.

---

## 3. Anti-Slop & Quality Invariants

You are strictly forbidden from writing shortcut or placeholder code:
- **NO** `// TODO`, `/* FIXME */`, `HACK`, or `XXX`.
- **NO** placeholder stubs (`pass`, `unimplemented!()`, empty functions).
- **NO** swallowed exceptions (`catch (e) {}`).
- **NO** hardcoded mock data in production paths.
- **NO** disabling type-safety or lint rules (`any`, `@ts-ignore`, `noqa`).

---

## 4. Self-Verification Commands

Before marking this work packet complete, you **MUST** run these verification commands in the terminal and verify that they succeed:

```bash
# 1. Typecheck & Lint
npm run typecheck
npm run lint

# 2. Targeted Unit Test Execution
npm test -- tests/path/to/target/file1.test.ts
```

Expected Result: Exit code `0`, zero warnings, all unit tests passing.

---

## 5. Completion Report Format

When you finish, reply with this structured JSON block:

```json
{
  "task_id": "[WP-ID]",
  "files_created_or_modified": [
    "path/to/target/file1.ts",
    "tests/path/to/target/file1.test.ts"
  ],
  "verification_command_executed": "npm test -- tests/path/to/target/file1.test.ts",
  "verification_passed": true,
  "edge_cases_handled": [
    "Null and empty string validation",
    "Negative numeric bounds rejection"
  ],
  "implementation_summary": "Implemented TargetModule adhering strictly to spec with 100% unit test coverage."
}
```
