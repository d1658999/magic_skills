# CORRECTION DIRECTIVE: [WP-ID] — Review Iteration [Attempt #]

## Audit Verdict: ❌ CHANGES REQUIRED

Your submission for Work Packet **[WP-ID]** was audited by the Lead Agent against the specification and quality standards. It did **not** pass review and is being reassigned to you for mandatory correction.

---

## 1. What Passed Review (DO NOT BREAK OR REWRITE)
The following parts of your implementation passed audit and must remain intact while you fix the defects below:
- `<File / function / test cases that are already correct>`

---

## 2. Blocking Defects to Fix Immediately

You **MUST** resolve every single defect listed below. Do not skip any item.

### Defect #1: `[Responsibility Violation | Spec Mismatch | Missing Edge Case | Code Quality / Slop | Failing Test]`
- **File & Lines**: `<absolute/path/to/file#LXX-LYY>`
- **What Is Wrong**:
  `<Exact explanation of the flaw, missing requirement, or error output>`
- **Required Fix**:
  `<Explicit step-by-step instructions or exact code replacement to fix the defect>`

### Defect #2: `[Category]`
- **File & Lines**: `<absolute/path/to/file#LXX-LYY>`
- **What Is Wrong**:
  `<Exact explanation of the flaw, missing requirement, or error output>`
- **Required Fix**:
  `<Explicit step-by-step instructions or exact code replacement to fix the defect>`

---

## 3. Strict Boundary & Quality Reminder
- **Allowed Files**: Only modify `<list of allowed files>`.
- **Zero Slop**: Do not introduce `TODO`, `FIXME`, type suppressions, or weakened test assertions.

---

## 4. Mandatory Re-Verification Before Replying

After applying all fixes above:
1. Run `<exact lint/typecheck command>` and confirm 0 errors.
2. Run `<exact unit test command>` and confirm all tests pass.
3. Reply with an updated **Completion Report** detailing:
   - Exact lines changed for each Defect (`#1..#N`)
   - Output of the verification commands
