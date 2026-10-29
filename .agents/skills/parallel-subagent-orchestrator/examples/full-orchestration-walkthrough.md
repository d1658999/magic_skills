# Full Orchestration Walkthrough: Parallel Order Processing Pipeline

This walkthrough demonstrates the complete **5-Phase Orchestration Lifecycle** on a realistic feature request:

> **User Request**: *"Build an order processing pipeline with three components: (1) an Order Validator, (2) a Discount Calculator, and (3) an Inventory Reservation Service, then wire them into `OrderProcessor.ts` with full unit and integration tests."*

---

## Phase 1: Reconnaissance & Shared Contract Lock

Before spawning any subagents, the Lead Agent inspects the workspace and creates the shared contract file `src/orders/types.ts` itself so that all 3 subagents code against the **exact same types**:

```ts
// src/orders/types.ts (Created by Lead Agent in Phase 1)
export interface LineItem {
  sku: string;
  quantity: number;
  unitPriceCents: number;
}

export interface OrderInput {
  orderId: string;
  customerId: string;
  items: LineItem[];
  couponCode?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export interface DiscountResult {
  subtotalCents: number;
  discountCents: number;
  finalTotalCents: number;
  appliedCoupon: string | null;
}

export interface ReservationResult {
  reserved: boolean;
  reservationId: string | null;
  failedSkus: string[];
}
```

---

## Phase 2: Master Plan & Zero-Assumption Work Packets

The Lead Agent partitions the work with **zero file overlap**:

| Work Packet ID | Subagent Role | Allowed Write Files (Exclusive) | Forbidden Files |
| :--- | :--- | :--- | :--- |
| `WP-1` | Order Validator Worker | `src/orders/validator.ts`, `tests/orders/validator.test.ts` | `src/orders/types.ts`, `src/orders/OrderProcessor.ts` |
| `WP-2` | Discount Calculator Worker | `src/orders/discount.ts`, `tests/orders/discount.test.ts` | `src/orders/types.ts`, `src/orders/OrderProcessor.ts` |
| `WP-3` | Inventory Service Worker | `src/orders/inventory.ts`, `tests/orders/inventory.test.ts` | `src/orders/types.ts`, `src/orders/OrderProcessor.ts` |
| `INTEGRATION` | **Lead Agent** | `src/orders/OrderProcessor.ts`, `tests/orders/OrderProcessor.test.ts` | — |

### Excerpt of `WP-2` Zero-Assumption Spec Sent to Subagent 2:
- **Exact Signature**: `export function calculateDiscount(items: LineItem[], couponCode?: string): DiscountResult`
- **Algorithm**:
  1. `subtotalCents = sum(item.quantity * item.unitPriceCents)`.
  2. Normalize `couponCode`: trim whitespace and uppercase (`couponCode?.trim().toUpperCase()`).
  3. Coupon rules:
     - `"SAVE10"`: `10%` off subtotal using integer floor (`Math.floor(subtotalCents * 0.10)`).
     - `"FLAT500"`: `500` cents off, only if `subtotalCents >= 2000`; otherwise `discountCents = 0` and `appliedCoupon = null`.
     - Unknown or empty coupon: `discountCents = 0`, `appliedCoupon = null`.
  4. Clamp `finalTotalCents = Math.max(0, subtotalCents - discountCents)`.
- **Edge Cases**:
  - `items` is empty `[]` -> `subtotalCents: 0, discountCents: 0, finalTotalCents: 0, appliedCoupon: null`.
  - `"save10 "` (lowercase + trailing space) -> must match `"SAVE10"`.

---

## Phase 3: Parallel Subagent Spawn

The Lead Agent invokes all 3 subagents in **one turn**:
- `invoke_subagent(TypeName="self", Role="WP-1: Order Validator", Prompt="<WP-1 Spec>")` -> returns `conv-wp1`
- `invoke_subagent(TypeName="self", Role="WP-2: Discount Calculator", Prompt="<WP-2 Spec>")` -> returns `conv-wp2`
- `invoke_subagent(TypeName="self", Role="WP-3: Inventory Service", Prompt="<WP-3 Spec>")` -> returns `conv-wp3`

---

## Phase 4: Mandatory 4-Gate Review (Catching Real Subagent Failures)

When all 3 subagents report completion, the Lead Agent audits every file and runs `validate_work_packet.py --mode audit`:

### Audit of `WP-1` (`conv-wp1`): ✅ APPROVED
- **Gate 1 (Scope)**: Only `src/orders/validator.ts` and `tests/orders/validator.test.ts` touched.
- **Gate 2 (Spec)**: All validation rules and edge cases implemented; zero `TODO`s.
- **Gate 3 (Quality)**: Clean, idiomatic TypeScript.
- **Gate 4 (Verification)**: `npx vitest run tests/orders/validator.test.ts` -> 7/7 tests pass.

### Audit of `WP-2` (`conv-wp2`): ❌ REJECTED (Failed Gate 2 & Gate 3)
Upon reading `src/orders/discount.ts`, the Lead Agent discovers two defects despite the subagent claiming success:
1. Line 18: The subagent did `Math.round(subtotalCents * 0.10)` instead of `Math.floor(subtotalCents * 0.10)` specified in Step 3.
2. Line 24: The subagent did not normalize `couponCode` with `.trim().toUpperCase()`, so `"save10 "` fails.

### Audit of `WP-3` (`conv-wp3`): ❌ REJECTED (Failed Gate 1 & Gate 2)
Upon checking `git status --short` and reading `src/orders/inventory.ts`:
1. **Responsibility Violation (Gate 1)**: Subagent modified `src/orders/types.ts` (a forbidden file!) to add an extra field.
2. **Anti-Slop Violation (Gate 2)**: Line 41 of `src/orders/inventory.ts` contains `// TODO: rollback partial stock reservation on multi-SKU failure`.

---

## Phase 5A: Surgical Reassignment Loop (`send_message`)

The Lead Agent first reverts `src/orders/types.ts` (`git checkout -- src/orders/types.ts`), then sends targeted Correction Directives to `conv-wp2` and `conv-wp3` in parallel:

### Correction Directive Sent to `conv-wp2`:
```markdown
# CORRECTION DIRECTIVE: WP-2 — Review Iteration #1
## Audit Verdict: ❌ CHANGES REQUIRED

### Defect #1: `[Spec Mismatch]`
- **File & Lines**: `src/orders/discount.ts#L18`
- **What Is Wrong**: Used `Math.round(subtotalCents * 0.10)` instead of `Math.floor(subtotalCents * 0.10)`.
- **Required Fix**: Change `Math.round` to `Math.floor`.

### Defect #2: `[Missing Edge Case]`
- **File & Lines**: `src/orders/discount.ts#L12-L26`
- **What Is Wrong**: `couponCode` is not normalized with `.trim().toUpperCase()`, causing lowercase or whitespace-padded codes like `"save10 "` to fail.
- **Required Fix**: Normalize `const normalized = couponCode?.trim().toUpperCase() ?? "";` at the start of `calculateDiscount()` and add the missing unit test in `tests/orders/discount.test.ts`.
```

### Correction Directive Sent to `conv-wp3`:
```markdown
# CORRECTION DIRECTIVE: WP-3 — Review Iteration #1
## Audit Verdict: ❌ CHANGES REQUIRED

### Defect #1: `[Responsibility Violation]`
- **File**: `src/orders/types.ts`
- **What Is Wrong**: You modified `src/orders/types.ts`, which is strictly forbidden in Section 2.
- **Required Fix**: `src/orders/types.ts` has been restored. Keep all internal state types inside `src/orders/inventory.ts`.

### Defect #2: `[Code Quality / Slop]`
- **File & Lines**: `src/orders/inventory.ts#L41-L45`
- **What Is Wrong**: Left a `// TODO: rollback partial stock reservation` placeholder instead of implementing two-phase check-then-decrement logic.
- **Required Fix**: First loop over all `items` to verify sufficient stock for every SKU and collect `failedSkus`. Only decrement stock in a second loop when `failedSkus.length === 0`. Add a unit test verifying stock is unchanged when the 2nd SKU in a 2-SKU order has insufficient stock.
```

### Re-Audit After Reassignment:
- Both `conv-wp2` and `conv-wp3` reply with fixed implementations.
- Lead Agent re-reads `src/orders/discount.ts` and `src/orders/inventory.ts` and re-runs Gate 1–4 checks.
- Both now pass **100%** of checks -> Marked `APPROVED ✅`.

---

## Phase 5B: Holistic Integration & Final Goal Check

With `WP-1`, `WP-2`, and `WP-3` all `APPROVED`, the Lead Agent creates `src/orders/OrderProcessor.ts` and `tests/orders/OrderProcessor.test.ts`, runs the full test suite (`npx vitest run`), and delivers the verified solution to the user.
