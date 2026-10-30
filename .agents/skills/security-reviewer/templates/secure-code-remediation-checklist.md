# Secure Code Remediation & Pre-Merge Gate Checklist

Use this checklist during PR review and before deploying code to staging or production environments.

---

## 1. Input Validation & Taint Sanitization
- [ ] **Strict Schema Validation**: All external inputs (body, query, headers, cookies) pass through schema validators (e.g. Zod, Pydantic, Joi) with unknown properties stripped (`.strict()`).
- [ ] **Parameterized Queries**: All database queries use prepared statements or ORM binding; zero raw string interpolation (`f"..."`, `+`, template literals).
- [ ] **Safe Path Resolution**: File paths are normalized and verified to remain strictly within intended base directories (`path.resolve()`, `os.path.abspath()`), avoiding Path Traversal (`../`).
- [ ] **Command Injection Safeguards**: System commands avoid shell invocation (`shell=False`, `execFile`) with arguments passed as discrete arrays.

---

## 2. Authentication & Session Security
- [ ] **Constant-Time Verification**: All secret tokens, HMACs, and signatures use constant-time comparisons (`crypto.timingSafeEqual`, `hmac.compare_digest`).
- [ ] **Memory-Hard Password Hashing**: Passwords hashed with Argon2id or bcrypt (work factor $\ge 12$).
- [ ] **Cryptographic Entropy**: All tokens, salts, and nonces generated using cryptographically secure PRNGs (`crypto.randomBytes`, `secrets.token_urlsafe`).
- [ ] **Cookie Hardening**: Authentication cookies configured with `HttpOnly`, `Secure`, `SameSite=Strict`, and `Path=/`.
- [ ] **JWT Restrictions**: JWT algorithms explicitly allowlisted (e.g. `algorithms: ['RS256']`), rejecting `alg: "none"`.

---

## 3. Access Control & Multi-Tenancy (BOLA/BFLA/BOPLA)
- [ ] **Tenant Scoping**: All database queries and updates include the authenticated caller's `tenant_id` or `user_id`.
- [ ] **Function-Level RBAC**: Privileged operations (create, update, delete, admin) protected by explicit route-level authorization guards.
- [ ] **Mass Assignment Prevention**: DTOs strictly define permissible update fields, preventing unauthorized modification of `role`, `tier`, or `is_verified`.

---

## 4. SSRF & Network Transport
- [ ] **Outbound URL Allowlisting**: User-supplied URLs validated against explicit scheme (`http`/`https`) and hostname allowlists.
- [ ] **Private IP Blocking**: DNS resolution verified to block loopback (`127.0.0.1`), link-local metadata (`169.254.169.254`), and RFC 1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- [ ] **Strict TLS Verification**: TLS certificate validation is enabled (`verify=True`, `NODE_TLS_REJECT_UNAUTHORIZED=1`).

---

## 5. Concurrency & Business Logic
- [ ] **Atomic Mutations**: Balance decrements, inventory reservations, and coupon redemptions executed in database transactions with row-level locks (`SELECT ... FOR UPDATE`) or atomic conditional queries (`UPDATE ... WHERE balance >= amount`).
- [ ] **State Machine Enforcement**: State transitions validate permitted predecessor states (e.g. `PENDING` $\rightarrow$ `PAID` $\rightarrow$ `SHIPPED`).

---

## 6. Cloud, Containers & Infrastructure
- [ ] **Non-Root Containers**: Dockerfiles define and switch to an unprivileged user (`USER appuser`).
- [ ] **Minimal Images**: Multi-stage Docker builds exclude compilers, build tools, and test artifacts.
- [ ] **Restricted Ingress**: Terraform/cloud security groups avoid open ingress (`0.0.0.0/0`) on sensitive database or management ports.
- [ ] **Least Privilege IAM**: Cloud IAM policies grant minimal required actions and resources without wildcards (`*`).

---

## 7. Supply Chain & Secrets
- [ ] **Zero Hardcoded Secrets**: No API keys, passwords, private keys, or tokens committed to source code or git history.
- [ ] **Committed Lockfiles**: Dependencies locked with verified lockfiles (`package-lock.json`, `poetry.lock`, etc.).
- [ ] **Automated CVE Scans**: Dependencies scanned against vulnerability databases with zero unresolved Critical or High CVEs.
