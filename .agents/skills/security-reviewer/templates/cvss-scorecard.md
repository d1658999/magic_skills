# CVSS v3.1 Scoring Rubric & Benchmark Scorecard

This guide provides the official Common Vulnerability Scoring System (CVSS v3.1) metric definitions, qualitative ratings, and benchmark vectors for application security reviews.

---

## 1. Metric Breakdown & Definitions

Metric | Key | Values | Weight Impact
:--- | :--- | :--- | :---
**Attack Vector** | `AV` | **N**etwork (`0.85`), **A**djacent (`0.62`), **L**ocal (`0.55`), **P**hysical (`0.20`) | Remote network-exploitable flaws score highest.
**Attack Complexity** | `AC` | **L**ow (`0.77`), **H**igh (`0.44`) | Low means no specialized conditions/race windows required.
**Privileges Required** | `PR` | **N**one (`0.85`), **L**ow (`0.62`), **H**igh (`0.27`) | Unauthenticated attacks carry the highest severity.
**User Interaction** | `UI` | **N**one (`0.85`), **R**equired (`0.62`) | Attacks requiring no victim clicks/interaction score higher.
**Scope** | `S` | **U**nchanged (`U`), **C**hanged (`C`) | Changed means vulnerability impacts components outside security authority (e.g. host breakout, SSRF to cloud metadata).
**Confidentiality** | `C` | **H**igh (`0.56`), **L**ow (`0.22`), **N**one (`0.00`) | High = total loss of data confidentiality.
**Integrity** | `I` | **H**igh (`0.56`), **L**ow (`0.22`), **N**one (`0.00`) | High = complete loss of system or data integrity.
**Availability** | `A` | **H**igh (`0.56`), **L**ow (`0.22`), **N**one (`0.00`) | High = complete denial of service or resource shutdown.

---

## 2. Qualitative Severity Rating Scale

| Qualitative Rating | Score Range | PR Merge Policy | Typical SLA for Remediation |
| :--- | :---: | :--- | :--- |
| 🚨 **CRITICAL** | `9.0 - 10.0` | **MERGE BLOCKED**. Immediate escalation. | Within 24-48 Hours |
| ⚠️ **HIGH** | `7.0 - 8.9` | **MERGE BLOCKED**. Must resolve in PR. | Within 7 Days |
| 🔶 **MEDIUM** | `4.0 - 6.9` | CONDITIONAL. May file tracked Jira ticket. | Within 30 Days |
| 🔷 **LOW** | `0.1 - 3.9` | Non-blocking. Author's discretion. | Next scheduled maintenance |
| ℹ️ **NONE / INFO** | `0.0` | Non-blocking. Best practice guidance. | Backlog |

---

## 3. Common Vulnerability Vector Benchmarks

| Vulnerability Type | Canonical CVSS v3.1 Vector | Score | Severity |
| :--- | :--- | :---: | :---: |
| **Unauthenticated RCE** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` | **9.8** | 🚨 **CRITICAL** |
| **BOLA / IDOR (Tenant Breach)** | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N` | **8.1** | ⚠️ **HIGH** |
| **SSRF (to Cloud Metadata)** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N` | **8.6** | ⚠️ **HIGH** |
| **SQLi (Authenticated)** | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H` | **8.8** | ⚠️ **HIGH** |
| **Stored XSS (Admin Impact)** | `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N` | **9.0** | 🚨 **CRITICAL** |
| **Reflected XSS** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N` | **6.1** | 🔶 **MEDIUM** |
| **CSRF (State-Changing)** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N` | **6.5** | 🔶 **MEDIUM** |
| **Timing Attack on Signature** | `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N` | **5.9** | 🔶 **MEDIUM** |
| **Verbose Stack Trace Leak** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N` | **5.3** | 🔶 **MEDIUM** |

---

## 4. Quick Calculation Commands

- **Python 3**:
  ```bash
  python .agents/skills/security-reviewer/scripts/cvss_calculator.py --vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
  ```
- **PowerShell 7**:
  ```powershell
  pwsh .agents/skills/security-reviewer/scripts/cvss_calculator.ps1 -Vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
  ```
