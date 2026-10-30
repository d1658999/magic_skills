# Application Security Audit Report

**Target / Repository**: `[TARGET_NAME_OR_REPO]`  
**Assessment Scope**: `[PR #123 / Branch / Full Codebase / Architecture]`  
**Lead Security Reviewer**: Security Reviewer Agent (Principal AppSec)  
**Date**: `[YYYY-MM-DD]`  
**Overall Security Verdict**: `[SECURITY CLEARED (APPROVE) | SECURITY BLOCKED (REQUEST_CHANGES) | CONDITIONAL APPROVE]`  

---

## 1. Executive Summary

`[Provide an authoritative 2-4 sentence summary of the security assessment: Scope evaluated, primary threat models analyzed, critical findings identified, and the residual risk posture.]`

---

## 2. Risk & Vulnerability Matrix

| Severity | Count | Blocking Status | Action Required |
| :--- | :---: | :---: | :--- |
| 🚨 **CRITICAL** | `[0]` | **BLOCKING** | Immediate fix required prior to deployment. |
| ⚠️ **HIGH** | `[0]` | **BLOCKING** | Fix required prior to production merge. |
| 🔶 **MEDIUM** | `[0]` | Non-Blocking | Address in current sprint or file tracked security ticket. |
| 🔷 **LOW** | `[0]` | Non-Blocking | Hardening recommendation for technical hygiene. |
| ℹ️ **INFORMATIONAL**| `[0]` | Non-Blocking | Defense-in-depth observation. |

---

## 3. High-Priority Findings & Remediation

<!-- Repeat for each Critical / High finding -->

### 🚨 Finding 1: `[Title of Vulnerability]`
- **Classification**: `[CWE-XXX / OWASP Category]`
- **CVSS v3.1 Score**: `[e.g. 9.8 (CRITICAL) - CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H]`
- **Vulnerable Component**: `[path/to/file.ext#L12-L28]`
- **Attack Vector & Preconditions**:
  `[Explain how an attacker reaches this code, what permissions they need, and how they exploit it.]`
- **Proof of Concept (PoC)**:
  ```http
  POST /api/v1/resource HTTP/1.1
  Host: target.example.com
  Content-Type: application/json

  {
    "input": "exploit_payload_here"
  }
  ```
- **Blast Radius & Impact**:
  `[Confidentiality breach, database compromise, tenant data leakage, financial loss.]`
- **Hardened Drop-In Solution**:
  ```diff
  - // Vulnerable code
  + // Production-ready hardened fix
  ```
- **Automated Verification Test**:
  ```python
  def test_vulnerability_is_neutralized():
      # Test payload assertion
      pass
  ```

---

## 4. Medium & Low Security Findings

<!-- Repeat for Medium / Low findings -->

### 🔶 Finding 2: `[Title]`
- **Classification**: `[CWE / OWASP]`
- **CVSS v3.1 Score**: `[e.g. 5.3 (MEDIUM)]`
- **Location**: `[path/to/file.ext#L45]`
- **Summary**: `[Brief explanation]`
- **Remediation**:
  ```diff
  - old
  + new
  ```

---

## 5. Architectural Threat Model & Attack Surface Map

- **Trust Boundaries Crossings**: `[Describe key boundary crossings inspected]`
- **Authentication & Tenant Isolation**: `[Findings on RBAC, session integrity, multi-tenancy]`
- **Data Protection**: `[Encryption at rest, TLS in transit, secret management]`

---

## 6. Official AppSec Sign-Off

- **Audit Status**: `[APPROVED / REJECTED / CONDITIONALLY APPROVED]`
- **Sign-Off Conditions**: `[Conditions that must be met before production release]`
- **Assessor**: AppSec Reviewer Agent
