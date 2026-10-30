# Real-World Code Review Walkthrough

This walkthrough demonstrates an end-to-end code review executed under the **High-Quality Code Reviewer** protocol.

---

## The Scenario

- **Pull Request**: #418: `Add Stripe Webhook Handler & Real-Time Inventory Allocation`
- **Author**: Backend Engineering Team
- **Stack**: TypeScript, Node.js, PostgreSQL (Prisma ORM), Express
- **Diff Summary**: 3 files modified (`src/controllers/webhook.ts`, `src/services/inventory.ts`, `tests/webhook.test.ts`), +142 lines, -18 lines.

---

## Phase 1: Context & Intent Reconnaissance

1. **Change Intent**: The PR adds an endpoint `POST /api/v1/webhooks/stripe` to handle `customer.subscription.created` events and automatically reserve product licenses/inventory for the customer.
2. **Blast Radius**:
   - Ingestion: External ingress from Stripe API.
   - Database: Modifies `subscriptions` and `inventory_allocations` tables.
   - Downstream: Dispatches email notification via background worker.
3. **Change Classification**: Feature & Billing/Inventory Integration (High Risk).

---

## Phase 2: Pre-Flight & Hygiene Audit

The reviewer runs the diff hygiene scanner:

```powershell
pwsh .agents/skills/code-reviewer/scripts/review_diff.ps1 -DiffFile pr_418.diff
```

**Scanner Output**:
```
==================================================
 🛡️ CODE REVIEW DIFF HYGIENE & PRE-FLIGHT AUDIT
==================================================
Files Modified     : 3
Lines Added        : 142 (+110 prod, +32 test)
Lines Deleted      : 18
Test-to-Code Ratio : 0.29 (Recommended: >= 0.50)
--------------------------------------------------
Findings: 0 Blocker(s), 0 Major(s), 2 Minor(s)
==================================================
[MINOR] src/controllers/webhook.ts:48 - Debug Print Leftover (console.log / print)
   Snippet: console.log("Received webhook payload:", req.body);
[MINOR] src/services/inventory.ts:12 - Unresolved Anti-Slop Marker (TODO / FIXME / XXX)
   Snippet: // TODO: add distributed lock if race condition occurs
```

**Hygiene Flags to Address**:
- Leftover `console.log` logging entire webhook payload (potential PII / card data exposure).
- `TODO` explicitly acknowledging a concurrency risk.
- Test ratio is 0.29, below the recommended 0.50 threshold.

---

## Phase 3: Architectural Soundness & API Contract Audit

1. **Idempotency**: Webhooks from Stripe can be delivered more than once (at-least-once delivery). If an event is re-delivered, will inventory be double-allocated or customer charged twice?
   - *Observation*: The code lacks an `event_id` deduplication check.
2. **Separation of Concerns**: The controller directly performs raw SQL queries and inventory calculations instead of delegating to domain services.

---

## Phase 4: Surgical Deep-Dive Analysis

### Defect 1: Cryptographic Timing Attack in Signature Verification
In `src/controllers/webhook.ts`:
```typescript
// Current Code in PR:
const signature = req.headers['stripe-signature'];
if (signature !== expectedSignature) {
  return res.status(400).send('Invalid signature');
}
```
- **Flaw**: Standard string equality `!==` terminates on first mismatched character, allowing timing side-channel attacks to forge webhook signatures.
- **Classification**: `[BLOCKER, security]`

### Defect 2: Race Condition in Inventory Allocation (TOCTOU)
In `src/services/inventory.ts`:
```typescript
// Current Code in PR:
const stock = await prisma.inventory.findUnique({ where: { productId } });
if (stock.available >= quantity) {
  await prisma.inventory.update({
    where: { productId },
    data: { available: stock.available - quantity }
  });
}
```
- **Flaw**: Classic Time-of-Check to Time-of-Use race condition. Two concurrent webhook deliveries or customer checkouts will both read `stock.available = 1`, and both succeed in deducting stock, resulting in negative inventory (-1).
- **Classification**: `[BLOCKER, concurrency]`

### Defect 3: Unhandled Async Promise & Missing Error Boundary
In `src/controllers/webhook.ts`:
```typescript
// Current Code in PR:
sendWelcomeEmail(customer.id); // Fire-and-forget without await or catch
```
- **Flaw**: If `sendWelcomeEmail` throws an unhandled rejection, Node.js may crash the entire container process depending on runtime flags.
- **Classification**: `[MAJOR, reliability]`

---

## Phase 5: Synthesis, Scoring & Verdict Delivery

### Evaluation Run:
```powershell
pwsh .agents/skills/code-reviewer/scripts/scorecard_evaluator.ps1 `
    -Blockers 2 -Majors 1 -Minors 2 `
    -Architecture 4 -Correctness 2 -Security 2 -Concurrency 2 `
    -Performance 4 -Reliability 3 -Testing 3 -Maintainability 4
```

**Evaluator Result**:
- Score: `0 / 100` (Penalized for 2 Blockers + 1 Major)
- Verdict: **`REQUEST_CHANGES`**

---

## Final Review Output (Presented to Author)

```markdown
# Pull Request Review: #418 - Stripe Webhook & Inventory Allocation

**Reviewer**: Code Reviewer Agent  
**Verdict**: ⚠️ **REQUEST_CHANGES**  
**Score**: `0 / 100` (Blocked on 2 Critical P0 Issues)  

---

### Executive Summary

Thank you for this PR! The integration structure and domain modeling are clean, and the separation into controller/service is well-conceived. However, there are two **Critical P0 Blockers** (a timing attack vulnerability in signature verification and a TOCTOU race condition in inventory deduction) and one **P1 Major issue** (unhandled async promise rejection) that must be resolved before this can safely merge into production.

---

### 🚨 Critical Blockers [P0]

#### 1. `src/controllers/webhook.ts#L24-L28`
**issue [blocking, security]:** Non-constant-time HMAC signature comparison exposes webhook to timing attacks.

- **Problem**: Comparing the Stripe signature using `!==` returns early upon the first differing byte.
- **Failure Scenario**: An attacker measuring nanosecond latency differences over multiple requests can iteratively reconstruct valid signatures.
- **Drop-In Solution**: Use Node's built-in `crypto.timingSafeEqual`:

```suggestion
- const signature = req.headers['stripe-signature'];
- if (signature !== expectedSignature) {
-   return res.status(400).send('Invalid signature');
- }
+ const signatureHeader = req.headers['stripe-signature'];
+ if (typeof signatureHeader !== 'string') {
+   return res.status(400).json({ error: 'Missing signature header' });
+ }
+ const sigBuffer = Buffer.from(signatureHeader, 'utf8');
+ const expectedBuffer = Buffer.from(expectedSignature, 'utf8');
+ if (sigBuffer.length !== expectedBuffer.length || !crypto.timingSafeEqual(sigBuffer, expectedBuffer)) {
+   return res.status(400).json({ error: 'Invalid webhook signature' });
+ }
```

---

#### 2. `src/services/inventory.ts#L42-L52`
**issue [blocking, concurrency]:** TOCTOU race condition leads to overselling and negative inventory.

- **Problem**: Reading `available` stock and deducting it in two non-atomic queries creates a concurrency window.
- **Failure Scenario**: When two concurrent purchase events for the last available item arrive simultaneously, both pass `stock.available >= quantity`, and both deduct, leaving `available = -1`.
- **Drop-In Solution**: Perform an atomic decrement with a conditional `WHERE` constraint:

```suggestion
- const stock = await prisma.inventory.findUnique({ where: { productId } });
- if (stock.available >= quantity) {
-   await prisma.inventory.update({
-     where: { productId },
-     data: { available: stock.available - quantity }
-   });
- } else {
-   throw new InsufficientStockError(productId);
- }
+ const updated = await prisma.inventory.updateMany({
+   where: {
+     productId,
+     available: { gte: quantity },
+   },
+   data: {
+     available: { decrement: quantity },
+   },
+ });
+ if (updated.count === 0) {
+   throw new InsufficientStockError(productId);
+ }
```

---

### ⚠️ Major Issues [P1]

#### 3. `src/controllers/webhook.ts#L64`
**issue [blocking, reliability]:** Unhandled async background promise can terminate process.

- **Problem**: `sendWelcomeEmail(customer.id)` is invoked without `await` or `.catch()`. If the email provider fails, an `UnhandledPromiseRejection` will destabilize the application.
- **Drop-In Solution**:

```suggestion
- sendWelcomeEmail(customer.id);
+ sendWelcomeEmail(customer.id).catch(err => {
+   logger.error('Failed to dispatch welcome email in background', {
+     customerId: customer.id,
+     err: err instanceof Error ? err.message : String(err),
+   });
+ });
```

---

### 💡 Minor Polish [P2] & Nits [P3]

1. **`src/controllers/webhook.ts#L48`** - **`nit [non-blocking]:`** Remove leftover `console.log("Received webhook payload:", req.body)` to prevent sensitive customer data from being written to application logs.
2. **`tests/webhook.test.ts`** - **`suggestion [non-blocking, test]:`** Add a test asserting that submitting the identical `stripe_event_id` twice returns `200 OK` without duplicating inventory deduction (idempotency verification).

---

### 🌟 Commendations & Praises

- **`src/services/inventory.ts#L1-L20`**: **`praise:`** Excellent dependency injection of the Prisma client and custom logger; makes unit testing straightforward and isolated.
```
