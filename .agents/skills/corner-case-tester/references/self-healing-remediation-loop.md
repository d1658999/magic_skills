# Self-Healing Red-to-Green Remediation Protocol

This reference defines the disciplined execution protocol for **Phase 4 (Autonomous Red-to-Green Remediation Loop)**. It explains how an AI agent safely, surgically, and iteratively repairs code or content until all adversarial corner-case tests pass, without causing collateral damage or introducing regressions.

---

## 1. The Red-to-Green Remediation State Machine

```
              ┌─────────────────────────────────┐
              │    1. Red State Detected        │
              │  (Test fails with stack trace)  │
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │    2. Root-Cause Isolation      │
              │ (Trace failure to exact source) │
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  3. Surgical Patch Formulation  │
              │   (Minimal diff, defensive guards│
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │     4. Apply Code Modification   │
              │      (Using edit_file/write)    │
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  5. Run Targeted Failing Test   │
              └────────────────┬────────────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                  (Fails)             (Passes)
                     │                   │
                     ▼                   ▼
           [Refine / Backtrack] ┌─────────────────────────────────┐
             (Max 5 attempts)   │    6. Run Full Regression Suite │
                                └────────────────┬────────────────┘
                                                 │
                                       ┌─────────┴─────────┐
                                       │                   │
                                    (Fails)             (Passes)
                                       │                   │
                                       ▼                   ▼
                             [Regression Detected:   ┌───────────────┐
                              Revert & Re-engineer]  │ 7. Green State│
                                                     │   Confirmed   │
                                                     └───────────────┘
```

---

## 2. Root-Cause Isolation Heuristics

When a corner-case test fails, the agent must not blindly tweak code. Diagnose the exact mechanical failure category:

### Failure Categories & Immediate Diagnostics:

1. **Unchecked Null / None Dereference**:
   - *Symptom*: `TypeError: Cannot read properties of undefined` or `AttributeError: 'NoneType' object has no attribute`.
   - *Remedy*: Insert early guard clause / optional chaining / default fallback at the entry point.
2. **Missing Boundary Guard**:
   - *Symptom*: `IndexError: list index out of range` or negative balance allowed.
   - *Remedy*: Validate numeric range immediately (`if amount <= 0: raise ValueError(...)`).
3. **Floating Point Rounding Drift**:
   - *Symptom*: `AssertionError: Decimal('10.000000000000002') != Decimal('10.00')`.
   - *Remedy*: Standardize on integer cents or explicit Decimal quantization (`quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)`).
4. **Race Condition / Non-Atomic Mutation**:
   - *Symptom*: Expected balance 0, but got -100 under concurrent threads.
   - *Remedy*: Add thread mutex lock (`threading.Lock()`), atomic compare-and-swap, or database row locking (`SELECT ... FOR UPDATE`).
5. **Unhandled State Machine Transition**:
   - *Symptom*: Method executed while object is in `TERMINATED` or `PENDING` state.
   - *Remedy*: Validate state transitions with explicit state lookup map and raise `IllegalStateError`.
6. **Encoding / Multi-Byte Truncation**:
   - *Symptom*: Corrupt string or split emoji surrogate pair.
   - *Remedy*: Use Unicode-aware string length functions or grapheme cluster splitters.

---

## 3. The 4 Golden Rules of Surgical Code Remediation

### Rule 1: The Principle of Minimal Blast Radius
Never rewrite an entire module or overhaul an architecture during a remediation loop.
- **Good**: Adding 4 lines of input validation at the top of a function.
- **Bad**: Refactoring an entire class into a functional pipe-and-filter architecture.

### Rule 2: Defense at the Perimeter (Input Validation)
Catch bad inputs at the system boundary before they penetrate deep into business logic or database storage.
```python
# PREFERRED: Perimeter Guard
def process_order(user_id: str, items: list[Item], discount_code: Optional[str]) -> Order:
    if not items:
        raise EmptyOrderError("Order must contain at least one item")
    if any(item.quantity <= 0 for item in items):
        raise InvalidQuantityError("Item quantities must be positive integers")
    # ... proceed with clean business logic ...
```

### Rule 3: The Strict Reversion Invariant
If a code change passes the new corner-case test but breaks ANY existing unit or integration test:
1. Immediately revert the changes.
2. Analyze why the regression occurred (e.g., did an existing client depend on a loose validation behavior?).
3. Re-architect the patch so it satisfies BOTH the new corner case AND the legacy contract.

### Rule 4: Ban on Slop & Workarounds
Never "fix" an error by:
- Wrapping the entire function in an empty `try ... except Exception: return None`.
- Disabling typechecking annotations or adding `@ts-ignore` / `# type: ignore`.
- Hardcoding specific test parameter values (e.g., `if user_id == "test_corner_case_user": return True`).

---

## 4. Multi-Iteration Convergence Strategy

If a fix does not pass the test on the first try, follow this convergence ladder:

| Attempt | Strategy | Actions |
| :---: | :--- | :--- |
| **1** | **Direct Root-Cause Patch** | Fix the exact condition indicated by the test assertion failure. |
| **2** | **Boundary & Type Harmonization** | Address type casting, null fallbacks, or subtle boundary mismatches (`<` vs `<=`). |
| **3** | **State & Lifecycle Alignment** | Check if failure was caused by ordering, state initialization, or unhandled side-effects. |
| **4** | **Re-reading the Baseline Spec** | Re-read the original requirement. Ensure the test expectation itself was not over-constraining or conflicting with existing design. |
| **5** | **Escalation & Strategic Triage** | If the 5th attempt fails, STOP. Document the architectural impasse in the Executive Triage Report and request human architect alignment. |

---

## 5. Automated Verification Checklist

Before declaring the remediation loop complete, verify:

- [ ] Target corner-case test passes deterministically (run 3 times to ensure zero flakiness).
- [ ] 100% of existing baseline tests pass with zero failures and zero skipped tests.
- [ ] Linter and typechecker pass with zero new warnings or errors.
- [ ] `git diff` shows only changes in application/source files; ZERO modifications in test suites.
- [ ] Code modifications conform to repository style and naming conventions.
