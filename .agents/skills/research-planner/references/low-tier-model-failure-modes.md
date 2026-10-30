# Low-Tier Model Failure Modes & Defenses

> **Reference Purpose**: A taxonomy of the 10 most common cognitive failure modes observed in lower-tier, small-parameter (7B–14B), and literal AI models, alongside concrete spec-level defenses that the Research Planner must build into task packets.

---

## 1. The Cognitive Profile of Lower-Tier Models

Lower-tier models (such as Qwen2.5-Coder-7B, Llama-3.1-8B, DeepSeek-Coder-6.7B, Gemini Flash-Lite, Claude Haiku, and GPT-4o-mini) are engineered for speed, low latency, and cost efficiency. However, their reduced parameter counts and architectural simplifications result in distinct cognitive weaknesses:
- **Shallow Reasoning Depth**: They excel at single-step syntax completion but struggle with multi-tier causal reasoning.
- **Narrow Effective Attention Window**: Even if a model accepts a 32k or 128k context window, its *effective retrieval and instruction-following window* degrades significantly past 2,000–4,000 tokens ("lost in the middle").
- **Optimism Bias / Slop Emission**: When unsure how to proceed, models prioritize generating syntactically pleasing text over functionally complete code, resulting in placeholders (`// TODO`), dummy returns, or mock stubs.

Understanding these failure modes allows the Research Planner to design prompts that make failure mathematically difficult.

---

## 2. Taxonomy of Failure Modes & Spec Countermeasures

### 1. API & Package Hallucination
- **Symptom**: The model imports non-existent methods (e.g., `import { verifyJwtSync } from 'jose'`) or packages not installed in `package.json`.
- **Root Cause**: Training data contains mixed versions of libraries; the model chooses the highest-probability token sequence without checking local dependencies.
- **Spec Defense**:
  - Research Planner must inspect `package.json` / `pyproject.toml` during Phase 2.
  - Provide verbatim import blocks at the top of the task packet.
  - Include an explicit negative instruction: *"Do NOT import any library not listed in the Verbatim Imports section."*

### 2. Placeholder Slop & Stubbing
- **Symptom**: Emits `// TODO: implement validation logic`, `# pass`, or returns static values (`return true;`).
- **Root Cause**: The model encounters high cognitive load or token budgets and takes the path of least resistance.
- **Spec Defense**:
  - Break tasks into micro-steps so no single function requires more than 30 lines of logic.
  - Provide the exact algorithmic steps in pseudo-code.
  - Embed the **Anti-Slop Ban** in the prompt, reinforced by an automated scanner script (`validate_spec.py`).

### 3. Context Collapse in Large Files
- **Symptom**: When instructed to edit a 500-line file, the model truncates the file, forgets existing exports, or alters unrelated functions.
- **Root Cause**: The model cannot hold the entire file's AST in its active attention heads while generating new code.
- **Spec Defense**:
  - Never ask a model to rewrite an entire file.
  - Provide surgical insertion anchors (line numbers and 3–5 anchor lines).
  - Use file-splitting techniques or append-only architectures where possible.

### 4. Scope Creep & Gratuitous Refactoring
- **Symptom**: While implementing a simple utility, the model reformats imports, changes variable names in unrelated methods, or updates project formatting.
- **Root Cause**: The model seeks stylistic consistency across all text in its output buffer.
- **Spec Defense**:
  - Enforce a strict **File Whitelist**.
  - Explicitly forbid modifying lines outside the assigned anchor range: *"Do NOT reformat or edit any code outside lines 42–65."*

### 5. Type Suppression (`as any`, `@ts-ignore`)
- **Symptom**: When faced with a TypeScript compiler error, the model casts the variable to `any` or adds `// @ts-ignore`.
- **Root Cause**: The model is optimized to satisfy linter/compiler exit codes with minimal token usage.
- **Spec Defense**:
  - Pre-define all complex types and domain DTOs in a shared `types.ts` file *before* dispatching the task.
  - Ban `@ts-ignore` and `any` in prompt rules; require `npx tsc --noEmit` as an automated gate.

### 6. Silent Error Swallowing
- **Symptom**: The model wraps code in `try { ... } catch (e) {}` and returns `null` or logs a generic message without re-throwing.
- **Root Cause**: Training examples often contain defensive boilerplate that prioritizes "not crashing" over correctness.
- **Spec Defense**:
  - Provide an **Exhaustive Error Matrix** in the spec.
  - State the exact error class to instantiate and throw for each failure branch.

### 7. Off-By-One & Edge-Case Blindness
- **Symptom**: Forgets boundary conditions (e.g., `<` vs `<=`, empty array, null/undefined, whitespace-only strings).
- **Root Cause**: Models prioritize the "happy path" which dominates their pre-training corpora.
- **Spec Defense**:
  - List all edge cases as explicit checklist items in the implementation recipe.
  - Provide unit tests that specifically assert behavior on `""`, `null`, `0`, and boundary timestamps.

### 8. Fragile Multi-Step Reasoning
- **Symptom**: When given a prompt with 5 conditional decisions ("If X do Y, unless Z, then if W..."), the model mixes up branch conditions.
- **Root Cause**: Feed-forward transformer architectures lack internal scratchpads for complex branching unless broken down into sequential chain-of-thought tokens.
- **Spec Defense**:
  - Flatten branching into a linear state machine.
  - Use guard clauses (`if (!condition) return;`) instead of deeply nested `if/else` ladders.

### 9. Self-Defeating / Trivial Unit Tests
- **Symptom**: When asked to write tests, the model mocks the subject under test or writes trivial assertions (`expect(true).toBe(true)`).
- **Root Cause**: The model is rewarded for producing tests that pass, not tests that find bugs.
- **Spec Defense**:
  - The Research Planner (or high-reasoning model) should pre-author the test file or provide the exact test cases.
  - The low-tier executor only implements the production code needed to turn the pre-written tests green (Test-Driven Development).

### 10. Infinite Hallucination Loops on Compiler Errors
- **Symptom**: When a build fails, the model tries random syntax changes that introduce new errors rather than diagnosing root cause.
- **Root Cause**: Small models lack debugging methodology; they react to error messages with local pattern matching.
- **Spec Defense**:
  - Limit automated retry loops to a maximum of 2 attempts.
  - On second failure, reassign to a higher-tier model or escalate to the human user.
