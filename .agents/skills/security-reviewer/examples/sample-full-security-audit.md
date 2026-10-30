# Real-World Security Audit Walkthrough

**PR**: #412: "Implement Customer Data Export API & Outbound Webhook Dispatcher"  
**Target Repository**: `acme/enterprise-saas-platform`  
**Reviewer**: Security Reviewer Agent (Principal AppSec)  
**Verdict**: **`REQUEST_CHANGES (SECURITY BLOCKED)`** — Contains 1 Critical BOLA vulnerability and 1 High SSRF vulnerability.

---

## 1. Executive Summary

This pull request introduces two core features: a CSV/JSON customer data export endpoint (`/api/v1/exports/:id`) and a customizable outbound webhook notification service.

While the core functionality works, an adversarial application security audit uncovered two severe security vulnerabilities:
1. **Critical BOLA / IDOR**: The export retrieval endpoint accepts arbitrary IDs without enforcing multi-tenant organization boundaries, allowing any authenticated user to download full sensitive records belonging to competing tenants.
2. **High-Severity SSRF**: The webhook registration endpoint allows users to specify arbitrary callback URLs. Outbound HTTP requests are dispatched without private network filtering, exposing internal cloud metadata services (`http://169.254.169.254`) and internal microservices.

Merge is **BLOCKED** until the provided drop-in fixes and verification tests are integrated.

---

## 2. Security Audit Scorecard

| Category | Finding Summary | Status |
| :--- | :--- | :---: |
| **Authentication & RBAC** | Valid JWT required, but missing object-level tenant scoping | ⚠️ **FAIL** |
| **Data Protection & Multi-Tenancy** | Critical BOLA exposing cross-tenant PII and financial records | 🚨 **CRITICAL** |
| **Network & Transport (SSRF)** | Outbound webhook requests vulnerable to cloud metadata SSRF | ⚠️ **FAIL** |
| **Cryptography & Timing** | Webhook HMAC verification uses timing-vulnerable string equality | 🔶 **WARN** |
| **Error Handling & Leakage** | Database stack trace returned in HTTP 500 error body | 🔷 **WARN** |

---

## 3. High-Priority Vulnerability Findings

### 🚨 Finding 1: Broken Object Level Authorization (BOLA/IDOR) in Export Retrieval

- **CWE Identification**: CWE-639 (Authorization Bypass Through User-Controlled Key)
- **OWASP Classification**: API1:2023 - Broken Object Level Authorization
- **CVSS v3.1 Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N`
- **CVSS Base Score**: **8.1 (HIGH)** / Business Risk: **CRITICAL** (Cross-Tenant Data Breach)
- **Location**: `src/controllers/exportController.ts#L42-L55`

#### Vulnerability Mechanism:
The export download controller retrieves an export job using only `req.params.id`. It fails to verify whether the export was created by or belongs to the requesting tenant organization (`req.user.organizationId`).

#### Adversarial Proof of Concept (PoC):
```http
GET /api/v1/exports/exp_tenantB_98472948 HTTP/1.1
Host: saas.acme.com
Authorization: Bearer <Tenant_A_User_JWT>
```

**Result**: Server responds with HTTP 200 and downloads a 50MB CSV containing Tenant B's customer names, emails, addresses, and order histories.

#### Hardened Drop-In Solution:
```diff
--- a/src/controllers/exportController.ts
+++ b/src/controllers/exportController.ts
@@ -42,7 +42,10 @@ export async function getExportJob(req: Request, res: Response) {
   const { id } = req.params;

-  const exportJob = await prisma.exportJob.findUnique({
-    where: { id }
-  });
+  // Enforce organization boundary at database query layer
+  const exportJob = await prisma.exportJob.findFirst({
+    where: {
+      id,
+      organizationId: req.user.organizationId // Multi-tenant boundary guard
+    }
+  });

   if (!exportJob) {
-    return res.status(404).json({ error: "Export not found" });
+    // Return generic 404 to avoid leaking existence of another tenant's export
+    return res.status(404).json({ error: "Export job not found or access denied" });
   }

   return res.json(exportJob);
 }
```

#### Automated Verification Test:
```typescript
it('SECURITY: should reject cross-tenant export access with 404', async () => {
  // Tenant B owns export
  const tenantBExport = await createMockExport({ orgId: 'org_tenant_b' });

  // Tenant A attempts to fetch Tenant B's export
  const response = await request(app)
    .get(`/api/v1/exports/${tenantBExport.id}`)
    .set('Authorization', `Bearer ${tenantAToken}`);

  expect(response.status).toBe(404);
  expect(response.body.exportJob).toBeUndefined();
});
```

---

### ⚠️ Finding 2: Server-Side Request Forgery (SSRF) in Outbound Webhooks

- **CWE Identification**: CWE-918 (Server-Side Request Forgery)
- **OWASP Classification**: OWASP 2021-A10: Server-Side Request Forgery
- **CVSS v3.1 Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N`
- **CVSS Base Score**: **8.6 (HIGH)**
- **Location**: `src/services/webhookDispatcher.ts#L28-L39`

#### Vulnerability Mechanism:
Users can register arbitrary URLs for webhook delivery. When events trigger, `axios.post(webhook.url, payload)` executes directly from the application cluster without validating the resolved IP address.

#### Adversarial Proof of Concept (PoC):
An attacker registers webhook URL:
```text
http://169.254.169.254/latest/meta-data/iam/security-credentials/production-backend-role
```
When a test ping or customer event fires, the backend queries AWS EC2 Instance Metadata and reflects temporary AWS STS keys back to the attacker's logs or dashboard error trace.

#### Hardened Drop-In Solution:
```diff
--- a/src/services/webhookDispatcher.ts
+++ b/src/services/webhookDispatcher.ts
@@ -1,5 +1,6 @@
 import axios from 'axios';
+import { isSafePublicUrl } from '../utils/ssrfValidator';

 export async function dispatchWebhook(url: string, payload: any) {
+  const isSafe = await isSafePublicUrl(url);
+  if (!isSafe) {
+    throw new Error('Invalid webhook destination: Private or restricted IP addresses are forbidden.');
+  }
+
   return await axios.post(url, payload, {
     timeout: 5000,
+    maxRedirects: 0, // Prevent redirect bypass to internal loopback
     headers: { 'Content-Type': 'application/json' }
   });
 }
```

---

### 🔶 Finding 3: Timing Attack on Webhook Signature Verification

- **CWE Identification**: CWE-208 (Observable Timing Discrepancy)
- **CVSS v3.1 Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N`
- **CVSS Base Score**: **5.9 (MEDIUM)**
- **Location**: `src/middleware/verifyWebhookSignature.ts#L22`

#### Hardened Drop-In Solution:
```diff
--- a/src/middleware/verifyWebhookSignature.ts
+++ b/src/middleware/verifyWebhookSignature.ts
@@ -1,4 +1,5 @@
+import crypto from 'crypto';

 export function verifySignature(expectedSig: string, clientSig: string): boolean {
-  return expectedSig === clientSig; // Vulnerable to timing attack
+  const expectedBuffer = Buffer.from(expectedSig, 'hex');
+  const clientBuffer = Buffer.from(clientSig, 'hex');
+  if (expectedBuffer.length !== clientBuffer.length) return false;
+  return crypto.timingSafeEqual(expectedBuffer, clientBuffer);
 }
```

---

## 4. Final Verdict & Sign-Off Conditions

- **Verdict**: **`REQUEST_CHANGES (SECURITY BLOCKED)`**
- **Requirements for Approval**:
  1. Commit the tenant scoping fix in `exportController.ts`.
  2. Implement SSRF IP validation and `maxRedirects: 0` in `webhookDispatcher.ts`.
  3. Replace string equality with `crypto.timingSafeEqual` in signature middleware.
  4. Ensure regression tests pass.
