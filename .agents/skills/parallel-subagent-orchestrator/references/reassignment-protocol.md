# Subagent Reassignment & Iterative Correction Protocol

When a subagent's work fails any check in the [Review & QA Rubric](./review-and-qa-rubric.md), the Original Agent **MUST NOT** accept the flawed output or silently lower the quality bar. Instead, reassign the task to correct every flaw until excellence is achieved.

---

## 1. Golden Rules of Reassignment

1. **Reuse the Existing Subagent First (`send_message`)**:
   - Subagents preserve their conversation history and file context.
   - Instead of spawning a brand-new subagent from scratch, send a **Correction Directive** to the existing subagent's `conversationId` using `send_message(Recipient=<conversationId>, Message=...)`.
   - *Exception*: If you are inside a `run_workflow` script, use a multi-turn called agent (`worker = agent(...)`; `await worker(...)`) so you can call `await worker(correction_prompt, schema)` in a loop!
2. **Never Send Vague Rejection Feedback**:
   - ❌ **Bad**: *"Your implementation has bugs and missed some edge cases. Please fix it."* (If the subagent wasn't smart enough to catch it the first time, vague feedback will fail again.)
   - ✅ **Good**: *"Review Round 1 Status: REJECTED (2 defects found). Defect 1: In `src/parser.ts` lines 44–49, `parseHeader()` throws `TypeError` when `rawHeader` is empty string `""` instead of returning `{ valid: false, reason: 'EMPTY_HEADER' }`. Replace lines 44–49 with an explicit check `if (!rawHeader.trim()) return { valid: false, reason: 'EMPTY_HEADER' };`..."*
3. **Batch All Findings Into One Correction Directive**:
   - Complete all 4 Review Gates before sending the subagent back to work. Give the subagent the **complete list** of defects in a single structured message so it can fix everything in one iteration.

---

## 2. The Reassignment Loop Workflow

```
Subagent Completes Turn
       │
       ▼
Lead Agent Runs 4-Gate Review
       │
       ├──► All 4 Gates PASS ──► Mark Subagent APPROVED
       │
       └──► Any Gate FAILS
               │
               ▼
       Increment Retry Counter (attempt = 1..3)
               │
               ├──► attempt <= 3:
               │      Send Correction Directive via `send_message`
               │      (or multi-turn workflow agent call)
               │      Wait for Subagent Completion -> Re-run 4-Gate Review
               │
               └──► attempt > 3 (Circuit Breaker Triggered):
                      Kill stuck subagent (`manage_subagents(Action="kill")`)
                      Escalate: Spawn fresh "pro" subagent with refined spec
                      OR apply surgical fix directly as Lead Agent
```

---

## 3. Writing a Surgical Correction Directive

Every reassignment message must follow [templates/correction-directive.md](../templates/correction-directive.md) and include:

1. **Review Verdict & Round Number**:
   - E.g., `REVIEW VERDICT: CHANGES REQUIRED (Iteration 1 of 3)`
2. **What Passed (Keep Intact)**:
   - Explicitly tell the subagent which files/functions passed review and **must not be broken or rewritten** while fixing the defects. (Subagents sometimes break working code when trying to fix one bug!)
3. **Numbered Defect List (Blocking Issues)**:
   For each defect:
   - **Category**: `[Responsibility Violation]` | `[Missing Spec Requirement]` | `[Bug / Edge Case]` | `[Code Quality / Anti-Slop]` | `[Test / Build Failure]`
   - **Location**: Exact file path and line range (`file.py:L72-L85`).
   - **Problem**: Exact description of what is wrong (include error tracebacks if a test/build failed).
   - **Required Fix**: Explicit, step-by-step instructions or exact code pattern to resolve the issue.
4. **Mandatory Re-Verification Steps**:
   - Exact commands the subagent must run after applying fixes before replying.

---

## 4. Handling Specific Failure Modes

### Failure Mode A: Out-of-Scope File Modification (Responsibility Violation)
- **Symptom**: Subagent edited a shared file or another subagent's file.
- **Action**:
  1. Inspect the out-of-scope diff.
  2. Restore the unauthorized file to its clean state (`git checkout -- <file>` or manual restore).
  3. In the Correction Directive, remind the subagent of its strict file boundary and instruct it how to achieve its goal within its allowed files (or note that the Lead Agent will handle shared wiring in Phase 5B).

### Failure Mode B: Stubs, Placeholders, or Shallow Implementation
- **Symptom**: Subagent left `// TODO: implement retry logic` or returned a hardcoded value.
- **Action**:
  1. Quote the exact placeholder lines.
  2. Provide the explicit algorithm for the missing logic in the Correction Directive so the subagent has no excuse to stub it again.

### Failure Mode C: Subagent Claims Tests Pass, But They Fail
- **Symptom**: Subagent either didn't run the test command or ran a filtered command that matched 0 tests.
- **Action**:
  1. Paste the actual failing output from your independent Gate 4 run into the Correction Directive.
  2. Instruct the subagent to fix the root cause in the implementation (and forbid deleting or weakening the test assertions to make the test pass!).
