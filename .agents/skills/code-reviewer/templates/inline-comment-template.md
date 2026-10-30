# Inline Code Review Comment Templates

Use these templates when submitting inline line-by-line review comments.

---

## 1. Blocker / Issue Template (Defect, Bug, Security, Race)

**`issue [blocking, {security|perf|arch|test}]:`** `{Concise Headline of the Defect}`

- **Problem**: {Explain what is happening and why the current code is vulnerable or incorrect.}
- **Failure Scenario**: {Provide a concrete runtime trigger or input that breaks the invariant, e.g.: "If caller passes an empty array, line 42 throws an unhandled NullPointerException."}
- **Proposed Solution**: {Explain the fix and supply the drop-in diff below.}

```suggestion
- {Original buggy code line(s)}
+ {Corrected, robust code line(s)}
```

---

## 2. Suggestion Template (Refactoring, Maintainability, Performance)

**`suggestion [non-blocking, {arch|perf|test}]:`** `{Concise Improvement Proposal}`

- **Rationale**: {Explain why this alternative is more maintainable, performant, or aligned with system conventions.}
- **Suggested Implementation**:

```suggestion
- {Original code}
+ {Optimized or simplified code}
```

---

## 3. Question Template (Clarification on Intent or Invariant)

**`question [blocking|non-blocking]:`** `{Clarification Question}`

- **Context**: {Explain what is ambiguous, e.g.: "Is `order.status` guaranteed to be non-terminal when this function executes, or should we guard against `CANCELLED` states?"}
- **Implication**: {Why this answer matters for correctness or architecture.}

---

## 4. Praise Template (Commendation for Great Craftsmanship)

**`praise:`** `{Positive Recognition}`

- **Callout**: {Highlight what makes this implementation stand out, e.g.: "Really appreciate the use of atomic compare-and-swap here—this neatly eliminates the race condition without the overhead of a heavyweight mutex lock."}

---

## 5. Nit Template (Minor Styling / Naming Polish)

**`nit [non-blocking]:`** `{Cosmetic suggestion}`

- **Note**: {e.g.: "Consider renaming `tmp` to `validatedHeaders` for clarity. Feel free to adopt or disregard."}
