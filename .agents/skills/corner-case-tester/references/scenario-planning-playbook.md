# Scenario Planning & Test Architecture Playbook

This reference establishes the methodology for transforming discovered corner cases into deterministic, executable test scenarios. It guides the agent through **Phase 2 (Adversarial Scenario Architecture & Test Synthesis)**.

---

## 1. Core Testing Methodologies for Corner Cases

To achieve total coverage without writing thousands of redundant tests, use these five formal testing methodologies:

```
┌────────────────────────────────────────────────────────┐
│             5 SCENARIO PLANNING METHODOLOGIES          │
├────────────────────────────────────────────────────────┤
│  1. Boundary Value Analysis (BVA)                      │
│     Test values right at, just below, and just above   │
│     every boundary threshold (min, min-1, max, max+1). │
│                                                        │
│  2. Equivalence Partitioning (EP)                      │
│     Divide input space into valid and invalid classes; │
│     test exactly one representative from each partition│
│                                                        │
│  3. Decision Table & Combinatorial Testing             │
│     Map complex boolean business rule combinations     │
│     into an orthogonal truth table.                    │
│                                                        │
│  4. State Transition & Path Inversion Testing          │
│     Test every illegal state transition and reverse    │
│     lifecycle sequence.                                │
│                                                        │
│  5. Property-Based & Invariant Testing                 │
│     Assert universal mathematical invariants across    │
│     hundreds of randomly generated payloads.           │
└────────────────────────────────────────────────────────┘
```

---

## 2. Boundary Value Analysis (BVA) Deep Dive

Boundary values represent the most fertile ground for off-by-one errors and integer overflows.

### The 3-Point Boundary Rule:
For every numerical or length constraint $[A, B]$, test 3 points around each boundary:
- Around minimum $A$: $A - 1$ (Invalid), $A$ (Valid Boundary), $A + 1$ (Valid Interior)
- Around maximum $B$: $B - 1$ (Valid Interior), $B$ (Valid Boundary), $B + 1$ (Invalid)
- Special points: $0$, $-1$, $+1$, `None` / `null`

```
  Invalid         Valid Minimum          Valid Interior          Valid Maximum         Invalid
────[A-1]──────────────[A]───────────────────[A+1]───────────────────[B-1]──────────────[B]─────────────[B+1]────▶
```

### Example: Pagination Limit Constraint ($1 \le limit \le 100$)
- Test Vector 1: `limit = 0` $\rightarrow$ Expect `ValidationError("limit must be between 1 and 100")`
- Test Vector 2: `limit = 1` $\rightarrow$ Expect `Success(count=1)`
- Test Vector 3: `limit = 2` $\rightarrow$ Expect `Success(count=2)`
- Test Vector 4: `limit = 99` $\rightarrow$ Expect `Success(count=99)`
- Test Vector 5: `limit = 100` $\rightarrow$ Expect `Success(count=100)`
- Test Vector 6: `limit = 101` $\rightarrow$ Expect `ValidationError("limit must be between 1 and 100")`
- Test Vector 7: `limit = -5` $\rightarrow$ Expect `ValidationError`
- Test Vector 8: `limit = None` $\rightarrow$ Expect Default applied (`limit=20`)

---

## 3. The Anatomy of a Bulletproof Test Scenario

Every corner-case scenario must be defined using the **Given-When-Then** specification structure:

### 1. Scenario Metadata:
- **Scenario ID**: Unique identifier (e.g., `SCEN-PAY-003`).
- **Target Component / Function**: Absolute file and function name.
- **Corner-Case Category**: One of the 10 dimensions.
- **Risk Level**: Critical / High / Medium / Low.

### 2. Given (Preconditions & State Setup):
- System state, database fixtures, mocked external APIs.
- Clock/time freezing (e.g., using `timecop`, `freezegun`, or custom fake timers).
- Concurrency workers initialized and waiting at a latch/barrier.

### 3. When (The Action / Adversarial Trigger):
- Exact input payload (numeric extreme, malformed UTF-8, empty list).
- Trigger mechanism (single call, parallel thread pool, simulated network drop).

### 4. Then (Strict Invariants & Assertions):
- **Return Value / Error**: Exact exception type, error code, and error message.
- **State Invariants**: Verifying database state was not corrupted, balances remain unchanged, locks were released.
- **Side-Effect Verification**: Verifying that zero unauthorized emails, webhooks, or charges were emitted.
- **Performance / Resource Bounds**: Execution completed within bounded memory and timeout (e.g., $< 200\text{ms}$).

---

## 4. Test Synthesis Patterns by Tech Stack

When synthesizing test suites, use the project's native framework with strict assertions:

### Pattern A: Python (`pytest`) with Parameterization & Hypothesis
```python
import pytest
from decimal import Decimal
from myapp.billing import process_discount, InvalidDiscountError

# 1. Parameterized Boundary Tests
@pytest.mark.parametrize("subtotal, discount, expected_total", [
    (Decimal("100.00"), Decimal("0.00"), Decimal("100.00")),   # Zero boundary
    (Decimal("100.00"), Decimal("100.00"), Decimal("0.00")),   # 100% boundary
    (Decimal("0.01"), Decimal("0.00"), Decimal("0.01")),       # Micro penny
])
def test_discount_valid_boundaries(subtotal, discount, expected_total):
    result = process_discount(subtotal, discount)
    assert result == expected_total

@pytest.mark.parametrize("subtotal, discount, error_match", [
    (Decimal("100.00"), Decimal("-10.00"), "Discount cannot be negative"),
    (Decimal("100.00"), Decimal("100.01"), "Discount cannot exceed subtotal"),
    (Decimal("-50.00"), Decimal("10.00"), "Subtotal cannot be negative"),
])
def test_discount_invalid_boundaries(subtotal, discount, error_match):
    with pytest.raises(InvalidDiscountError, match=error_match):
        process_discount(subtotal, discount)
```

### Pattern B: TypeScript / JavaScript (`Vitest` / `Jest`)
```typescript
import { describe, it, expect } from 'vitest';
import { parseUserPayload, ValidationError } from '../src/parser';

describe('Corner Cases: parseUserPayload', () => {
  it('rejects null and undefined payloads with explicit ValidationError', () => {
    expect(() => parseUserPayload(null as any)).toThrowError(ValidationError);
    expect(() => parseUserPayload(undefined as any)).toThrowError(ValidationError);
  });

  it('handles 4-byte astral Unicode emojis without truncation', () => {
    const user = parseUserPayload({ username: '👨‍👩‍👧‍👦_admin', age: 25 });
    expect(user.username).toBe('👨‍👩‍👧‍👦_admin');
    expect(user.username.length).toBeGreaterThan(0);
  });

  it('prevents prototype pollution via __proto__ or constructor keys', () => {
    const payload = JSON.parse('{"__proto__": {"polluted": true}, "username": "hacker"}');
    const user = parseUserPayload(payload);
    expect((({} as any).polluted)).toBeUndefined();
  });
});
```

### Pattern C: Concurrency Stress Test (Python `concurrent.futures`)
```python
import concurrent.futures
from myapp.wallet import Wallet

def test_concurrent_withdrawal_prevents_double_spend():
    wallet = Wallet(balance=100) # Only enough for 1 withdrawal
    successful_withdrawals = 0
    failed_withdrawals = 0

    def attempt_withdraw():
        return wallet.withdraw(amount=100)

    # Spawn 10 simultaneous threads hitting the wallet at the exact same moment
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(attempt_withdraw) for _ in range(10)]
        for f in concurrent.futures.as_completed(futures):
            try:
                if f.result() is True:
                    successful_withdrawals += 1
            except Exception:
                failed_withdrawals += 1

    # Invariants: Exactly one withdrawal succeeded; balance is zero, never negative!
    assert successful_withdrawals == 1
    assert failed_withdrawals == 9
    assert wallet.get_balance() == 0
```

---

## 5. Decision Tree for Test Scenario Placement

```
Does the corner case involve a single isolated function?
  ├── YES ──▶ Unit Test (Parameter / Boundary suite)
  └── NO
       ├── Does it involve timing, threading, or shared state?
       │    ├── YES ──▶ Concurrency Stress / Race Test (Parallel workers + Barrier)
       │    └── NO
       ├── Does it involve multiple services or external contracts?
       │    ├── YES ──▶ Integration Test (Mocked wire / Chaos fault injection)
       │    └── NO
       └── Does it involve an infinite input domain?
            └── YES ──▶ Property-Based Fuzz Test (Hypothesis / fast-check)
```
