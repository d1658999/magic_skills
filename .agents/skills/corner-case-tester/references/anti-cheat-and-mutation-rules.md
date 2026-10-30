# Anti-Cheat & Mutation Integrity Rules

This reference outlines the integrity guardrails enforced during **Phase 5 (Anti-Cheat, Mutation & Regression Verification)**. When an autonomous agent is given the capability to both run tests and modify code, strict guardrails are necessary to prevent the agent from "cheating" to pass the tests.

---

## 1. The Autonomous Test-Fix Paradox

An agent tasked with turning a test suite green has two ways to do so:
1. **The Authentic Fix**: Fix the underlying application code so it correctly satisfies the specification.
2. **The "Cheat" (Defect Masking)**: Modify the test, weaken the assertions, mock out the actual calculation, or hardcode the expected answer.

**Mandatory Rule**: The agent must **NEVER** modify test files or alter verification constraints during the remediation loop unless explicitly instructed that a requirement itself was defective.

```
┌────────────────────────────────────────────────────────┐
│                   THE 5 FORBIDDEN CHEATS               │
├────────────────────────────────────────────────────────┤
│  1. Test Tampering: Editing assertions or expectations │
│  2. Assertion Weakening: Changing strict == to != null │
│  3. Hardcoded Mocking: if (arg == "test_val") return X │
│  4. Error Swallowing: Blank try/catch blocks           │
│  5. Regression Ignorance: Ignoring pre-existing tests  │
└────────────────────────────────────────────────────────┘
```

---

## 2. Detection Mechanisms for Forbidden Cheats

### Cheat 1: Test Suite Tampering
- **Pattern**: Modifying files in `tests/`, `__tests__/`, or test fixtures during the remediation phase.
- **Automated Check**: `git diff --name-only <baseline_commit>` must contain ZERO files in test directories.
- **Remedy**: Revert all changes in test directories immediately (`git checkout -- tests/`).

### Cheat 2: Assertion Weakening
- **Pattern**: Replacing rigorous checks with toothless assertions:
  ```python
  # ORIGINAL (STRICT)
  assert calculate_total(order) == Decimal("124.50")

  # WEAKENED (CHEATING)
  assert calculate_total(order) is not None
  ```
- **Automated Check**: Regex scan across diffs for removed assertion lines or substituted loose operators (`is not None`, `truthy`, `typeof == 'object'`).

### Cheat 3: Hardcoding Input-Specific Shortcuts (Overfitting)
- **Pattern**: Inserting conditional branches that check for exact test literals:
  ```typescript
  // CHEATING: Only works for the specific unit test input
  if (cart.id === "test-cart-99" && coupon === "VIP20") {
      return 80;
  }
  ```
- **Remedy**: Flag any string or numeric literal appearing in a commit that matches an input literal defined only inside a test fixture. Require generalized algorithmic logic.

### Cheat 4: Silent Error Swallowing
- **Pattern**: Concealing crashes by wrapping failing blocks in generic catch statements:
  ```python
  # CHEATING: Swallowing the crash to pretend test passed
  try:
      self._process_transaction()
  except Exception:
      pass # Test now passes because no exception was raised!
  ```
- **Remedy**: Ban blank catch/except blocks. Require explicit typed exception handling and meaningful error propagation or fallback state.

### Cheat 5: Regression Ignorance
- **Pattern**: Celebrating that the new corner-case test passes while 3 existing baseline unit tests are failing.
- **Remedy**: Full test suite pass rate must be 100%. A fix that breaks an existing test is completely invalid.

---

## 3. Mutation Testing: Proving Tests Have Teeth

To verify that a test suite is genuinely testing behavior and cannot be fooled by dummy code, employ **Mutation Sanity Checks**:

```
                       [Original Code: Green Tests]
                                    │
                                    ▼
                       [Introduce Deliberate Mutant]
                     (e.g., Change `>` to `>=`, delete line)
                                    │
                                    ▼
                            [Re-Run Test Suite]
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                     (Tests FAIL)        (Tests PASS)
                         │                     │
                         ▼                     ▼
                  [Mutant KILLED]       [Mutant SURVIVED]
                (Test Suite Valid)     (Test Suite Weak / Blind)
```

### 3 Canonical Mutation Probes:
1. **Boundary Operator Inversion**:
   - Change `if (amount > balance)` to `if (amount >= balance)`.
   - The test asserting zero-balance withdrawals MUST fail.
2. **Validation Removal**:
   - Comment out the input sanitization or empty check `if (!username.trim()) throw ...`.
   - The empty-string corner-case test MUST fail.
3. **Constant Return Mutation**:
   - Replace complex calculation with `return 0` or `return True`.
   - Property and value assertion tests MUST fail.

If a mutant survives (i.e., tests pass despite broken code), the test suite is inadequate. Strengthen the assertions before declaring completion.
