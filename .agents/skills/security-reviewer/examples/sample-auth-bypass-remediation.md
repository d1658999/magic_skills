# Case Study: Authentication Bypass & Concurrency Race Remediation

This walkthrough details an adversarial security review of an authentication and billing subscription service that uncovered a composite **Authentication Bypass** and **Concurrency TOCTOU Race Condition**.

---

## 1. Vulnerability Overview

During a security review of `authService.ts` and `subscriptionController.ts`, two interlocking defects were discovered:

1. **JWT Algorithm Confusion (`alg: none`)**: The custom JWT validation helper decoded tokens without validating the signature algorithm header, accepting unverified tokens signed with `alg: "none"`.
2. **Double-Spend / Trial Replay Race Condition**: When a user activates a free trial promotion, the system checks whether the user already redeemed the trial in one database call, and writes the redemption in a subsequent call without database transactional locks.

---

## 2. Technical Breakdown & PoC

### Flaw 1: JWT Signature Verification Bypass
The developer wrote a custom token parser to extract claims:

```typescript
// INSECURE CODE IN PR:
export function authenticateToken(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: "No token provided" });

  const token = authHeader.split(' ')[1];
  // VULNERABLE: jwt.decode does NOT verify cryptographic signature!
  const decoded = jwt.decode(token) as any;

  if (!decoded || !decoded.userId) {
    return res.status(401).json({ error: "Invalid token" });
  }

  req.user = decoded;
  next();
}
```

#### Attacker Exploit (PoC):
An attacker creates an unsigned JWT payload:
- Header: `{"alg": "none", "typ": "JWT"}`
- Payload: `{"userId": "usr_superadmin", "role": "GLOBAL_ADMIN", "organizationId": "org_enterprise"}`
- Signature: (empty)

Token String:
```text
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VySWQiOiJ1c3Jfc3VwZXJhZG1pbiIsInJvbGUiOiJHTE9CQUxfQURNSU4iLCJvcmdhbml6YXRpb25JZCI6Im9yZ19lbnRlcnByaXNlIn0.
```

The attacker sends:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJub25l..." https://api.acme.com/admin/delete-database
```
**Impact**: Total unauthenticated takeover of arbitrary administrative accounts (CVSS 9.8 Critical).

---

### Flaw 2: TOCTOU Concurrency Race Condition in Promotion Redemption

```python
# INSECURE PYTHON ENDPOINT IN PR:
@router.post("/api/v1/promotions/redeem")
async def redeem_promo(promo_code: str, user=Depends(get_current_user), db=Depends(get_db)):
    # Step 1: Check if promo already claimed (Time of Check)
    existing_claim = await db.fetch_one(
        "SELECT id FROM promo_claims WHERE user_id = :uid AND code = :code",
        {"uid": user.id, "code": promo_code}
    )
    if existing_claim:
        raise HTTPException(status_code=400, detail="Promotion already claimed")

    # High-latency external credit check (creates 200ms race window)
    await external_billing_service.verify_credit(user.id)

    # Step 2: Insert claim (Time of Use)
    await db.execute(
        "INSERT INTO promo_claims (user_id, code, credit_amount) VALUES (:uid, :code, 100)",
        {"uid": user.id, "code": promo_code}
    )
    await db.execute(
        "UPDATE accounts SET balance = balance + 100 WHERE user_id = :uid",
        {"uid": user.id}
    )
    return {"status": "success", "credit_added": 100}
```

#### Attacker Exploit (PoC):
The attacker fires 20 parallel HTTP requests simultaneously using `asyncio` or `curl --parallel`.
Because the database check in Step 1 executes before any of the concurrent requests reach Step 2, all 20 requests observe `existing_claim = None`.
The attacker receives **\$2,000 in credit** instead of \$100.

---

## 3. Hardened Production-Ready Solutions

### Drop-In Solution for Flaw 1 (JWT Verification):
```typescript
import jwt from 'jsonwebtoken';

const JWT_PUBLIC_KEY = process.env.JWT_PUBLIC_KEY!;

export function authenticateToken(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: "Missing or malformed Authorization header" });
  }

  const token = authHeader.substring(7);

  try {
    // HARDENED: Rigorously verifies cryptographic signature against RS256 allowlist
    const verified = jwt.verify(token, JWT_PUBLIC_KEY, {
      algorithms: ['RS256'], // Explicit algorithm allowlist (blocks 'none' and HS256 confusion)
      issuer: 'https://auth.acme.com',
      audience: 'https://api.acme.com'
    }) as { userId: string; role: string; organizationId: string };

    req.user = verified;
    next();
  } catch (err: any) {
    return res.status(401).json({ error: "Invalid or expired authentication token" });
  }
}
```

### Drop-In Solution for Flaw 2 (Transactional Atomicity & Unique Constraint):
```python
# HARDENED PYTHON IMPLEMENTATION:
# 1. Database schema enforces unique index:
# CREATE UNIQUE INDEX idx_promo_user_code ON promo_claims (user_id, code);

@router.post("/api/v1/promotions/redeem")
async def redeem_promo(promo_code: str, user=Depends(get_current_user), db=Depends(get_db)):
    async with db.transaction(): # Atomic database transaction
        # Lock user account row during redemption
        account = await db.fetch_one(
            "SELECT id, balance FROM accounts WHERE user_id = :uid FOR UPDATE",
            {"uid": user.id}
        )

        try:
            # Atomic insert relying on database uniqueness constraint
            await db.execute(
                """
                INSERT INTO promo_claims (user_id, code, credit_amount, created_at)
                VALUES (:uid, :code, 100, NOW())
                """,
                {"uid": user.id, "code": promo_code}
            )
        except UniqueViolationError:
            # Database rejects duplicate simultaneous inserts
            raise HTTPException(status_code=400, detail="Promotion already claimed")

        # Credit updated within the same atomic transaction
        await db.execute(
            "UPDATE accounts SET balance = balance + 100 WHERE user_id = :uid",
            {"uid": user.id}
        )

    return {"status": "success", "credit_added": 100}
```

---

## 4. Verification Tests

```typescript
describe('Security Suite: JWT Signature Hardening', () => {
  it('REJECTS tokens with alg: none', () => {
    const maliciousToken = 'eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VySWQiOiJhZG1pbiJ9.';
    expect(() => {
      jwt.verify(maliciousToken, JWT_PUBLIC_KEY, { algorithms: ['RS256'] });
    }).toThrow();
  });
});
```
