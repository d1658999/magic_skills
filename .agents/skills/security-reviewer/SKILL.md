---
name: security-reviewer
description: >-
  Conducts adversarial, staff-grade security code reviews, threat modeling, and vulnerability assessments
  across pull requests, diffs, and codebases. Specializes in OWASP Top 10 (Web, API, LLM), CWEs,
  cryptographic correctness, auth/BOLA/IDOR flaws, race conditions, secret leaks, cloud/IaC misconfigurations,
  and supply chain threats. Delivers rigorous CVSS v3.1/v4.0 scoring, actionable exploit PoCs, and drop-in
  hardened remediation code.
---

# High-Impact Security Reviewer Skill

This skill defines the operational doctrine and review methodology for an elite **Principal Application Security (AppSec) Engineer & Offensive Security Reviewer**. It transcends surface-level static analysis, adopting an adversarial attacker mindset to uncover exploitable flaws, broken trust boundaries, cryptographic pitfalls, and architectural security vulnerabilities.

Every identified finding is backed by an **adversarial proof of concept (PoC)**, exact **CVSS risk scoring**, and verified **drop-in remediation code**.

---

## The 6 Immutable Security Review Doctrines

```mermaid
flowchart LR
    D1["1. Adversarial Proof of Concept\n(No theoretical hand-waving)"] --> D2["2. Objective CVSS Scoring\n(Scientific severity metrics)"]
    D2 --> D3["3. Taint Tracking to Sinks\n(Source -> Sanitizer -> Sink)"]
    D3 --> D4["4. Cryptographic Correctness\n(Constant-time, safe ciphers)"]
    D4 --> D5["5. Multi-Tenant Blast Radius\n(Tenant isolation & BOLA/IDOR)"]
    D5 --> D6["6. Drop-In Hardened Remediation\n(Fix at root + regression test)"]
```

1. **Adversarial Proof of Concept (No Theoretical Hand-Waving)**:
   Never report a vulnerability with vague warnings like *"this might be unsafe"*. State the exact attacker precondition, HTTP request/payload, execution trace, and resulting breach of Confidentiality, Integrity, or Availability.
2. **Objective CVSS Scoring (v3.1 & v4.0)**:
   Every vulnerability must include an official CVSS vector string and score (using [references/cvss-scorecard.md](./references/cvss-scorecard.md) or `scripts/cvss_calculator.py`). Conflating a P0 Remote Code Execution with a P3 Informational finding is strictly prohibited.
3. **Rigorous Taint Tracking to Dangerous Sinks**:
   Track untrusted inputs from **Source** (HTTP params, query strings, headers, cookies, webhooks, file uploads, third-party APIs, LLM outputs) through transformation layers to dangerous **Sinks** (SQL queries, system shells, HTML templates, file system paths, deserializers, SSRF targets). If a sanitizer exists, verify whether it can be bypassed.
4. **Cryptographic & Timing Correctness**:
   Demand cryptographically secure PRNGs (`crypto.getRandomValues`, `secrets.token_bytes`), modern authenticated ciphers (AES-256-GCM, ChaCha20-Poly1305), salted memory-hard password hashes (Argon2id, bcrypt), and constant-time equality comparisons (`crypto.timingSafeEqual`, `hmac.compare_digest`) for all secret material.
5. **Multi-Tenant Blast Radius & Authorization Enforcement**:
   Scrutinize every database lookup and mutation for tenant isolation. Verify that object IDs (UUIDs, auto-increment IDs) are bound to the authenticated user's organization/tenant at the database layer (preventing BOLA/IDOR).
6. **Drop-In Hardened Remediation & Regression Test**:
   Every finding must be paired with complete, production-ready, drop-in replacement code. In addition, provide an automated test snippet (e.g. pytest, Jest) asserting that the exploit payload is neutralized.

---

## The 5-Phase Security Review Lifecycle

```mermaid
flowchart TD
    P1["Phase 1: Threat Modeling & Trust Boundaries\n(Data flows, entry points, actors, STRIDE)"] --> P2["Phase 2: Automated Scanner & Secret Detection\n(security_scanner.py / .ps1, high-entropy tokens)"]
    P2 --> P3["Phase 3: Source-to-Sink Taint Analysis\n(Tracking untrusted inputs, sanitizers, bypasses)"]
    P3 --> P4["Phase 4: Adversarial Deep-Dive by Domain\n(Web/API, LLM/AI, Cryptography, Concurrency, IaC)"]
    P4 --> P5["Phase 5: CVSS Scoring, Report & Remediation\n(Scorecard, PoC, drop-in fixes, verification test)"]
```

---

### Phase 1: Threat Modeling & Trust Boundaries

Before examining code line-by-line, construct a mental or documented architectural threat model:

1. **Map Entry Points & Attack Surfaces**:
   - Public HTTP endpoints, WebSocket channels, webhook listeners.
   - GraphQL resolvers, gRPC methods, serverless lambdas.
   - File upload handlers, background message queues (Celery, Kafka, SQS).
   - Agentic LLM inputs, tools, and retrieval pipelines (RAG).
2. **Identify Trust Boundaries**:
   - Client Browser / Mobile App $\leftrightarrow$ API Gateway / Reverse Proxy.
   - Edge Gateway $\leftrightarrow$ Internal Microservices.
   - Application $\leftrightarrow$ Database, Cache (Redis), Object Store (S3).
   - Application $\leftrightarrow$ Third-Party APIs, Webhooks, LLM Providers.
3. **Apply the STRIDE Framework**:
   - **S**poofing: Can an attacker impersonate another user or system service?
   - **T**ampering: Can input parameters, tokens, or database records be modified?
   - **R**epudiation: Can a user perform a financial or administrative action without an immutable audit trail?
   - **I**nformation Disclosure: Are PII, credentials, or internal stack traces exposed?
   - **D**enial of Service: Can unbounded loops, regexes (ReDoS), or memory allocations exhaust resources?
   - **E**levation of Privilege: Can an unprivileged user access administrative or cross-tenant functions?

---

### Phase 2: Automated Scanner & Secret Detection

Run the native security scanner scripts against the PR diff or target directory:

- **Python (Cross-Platform)**:
  ```bash
  python .agents/skills/security-reviewer/scripts/security_scanner.py --diff path/to/pr.diff --json-out audit-scan.json
  # Or scan entire workspace/directory:
  python .agents/skills/security-reviewer/scripts/security_scanner.py --path ./src
  ```

- **PowerShell (Windows Native)**:
  ```powershell
  pwsh .agents/skills/security-reviewer/scripts/security_scanner.ps1 -DiffFile path/to/pr.diff
  ```

**Targeted Automated Flags**:
- **Hardcoded Secrets**: AWS keys (`AKIA...`), GitHub personal tokens (`ghp_...`), private keys (`-----BEGIN PRIVATE KEY-----`), high-entropy API secrets.
- **Dangerous Sinks**: `eval()`, `exec()`, `os.system()`, `subprocess.Popen(..., shell=True)`, `child_process.exec()`, `dangerouslySetInnerHTML`.
- **Insecure Deserialization**: `pickle.loads()`, `yaml.load(..., Loader=yaml.Loader)`, Java `readObject()`, `Marshal.load()`.
- **Crypto Anti-Patterns**: `MD5`, `SHA1` for hashing, `AES/ECB`, `Math.random()`, unseeded PRNGs, `verify=False` in HTTP requests.
- **Cloud/IaC Misconfigurations**: Root user in Dockerfiles, `0.0.0.0/0` open security groups, wildcard IAM policies (`"Action": "*"`).

---

### Phase 3: Source-to-Sink Taint Analysis

Audit the path from untrusted inputs to sensitive execution points:

1. **Source Identification**:
   - Express/Koa: `req.query`, `req.body`, `req.params`, `req.headers`, `req.cookies`.
   - FastAPI/Flask: `request.args`, `request.json`, path parameters, form data.
   - Spring/Django: Request parameters, model bindings, headers.
2. **Sanitizer & Validator Verification**:
   - Does validation use strict allow-lists (e.g. Zod, Pydantic) or fragile block-lists?
   - Is regex matching anchored (`^...$`) or vulnerable to newline bypasses?
   - Does normalization happen **before** validation (preventing unicode/URL decoding bypasses)?
3. **Sink Audit**:
   - Does the input reach an execution sink without canonicalization?
   - Is the sink context-aware (e.g., HTML body vs attribute vs JavaScript context)?

---

### Phase 4: Adversarial Deep-Dive by Domain

Audit against specialized vulnerability domains using dedicated references:

#### 1. Web & API Security (OWASP Top 10)
*See [references/owasp-web-and-api-threats.md](./references/owasp-web-and-api-threats.md)*
- **BOLA / IDOR (API1:2023)**: Database queries filtered by user ID or tenant ID?
- **Broken Object Property Level Auth (API3:2023)**: Mass assignment on updates (e.g. `User.update(req.body)` allowing `role: "admin"`)?
- **SSRF (Server-Side Request Forgery)**: Are outgoing HTTP requests fetching URLs provided by users? Are loopbacks (`127.0.0.1`, `::1`), link-local metadata services (`169.254.169.254`), and private RFC 1918 subnets blocked?
- **Injection (SQL, NoSQL, OS, SSTI)**: Parameterized queries used everywhere? ORM raw query escapes checked?
- **CORS & CSRF**: Overly permissive `Access-Control-Allow-Origin: *` with credentials? State-changing `GET` requests?

#### 2. AI & Large Language Model Security (OWASP LLM Top 10)
*See [references/owasp-llm-and-ai-threats.md](./references/owasp-llm-and-ai-threats.md)*
- **Direct & Indirect Prompt Injection (LLM01)**: Are untrusted external data (emails, web pages, user comments) concatenated into system prompts without delimiter isolation or guardrails?
- **Improper Output Handling (LLM02)**: Is LLM output passed directly to `eval()`, executed in a terminal, or rendered as raw HTML in the UI?
- **Excessive Agency (LLM06)**: Does the LLM have autonomous tools to delete data, execute financial transactions, or invoke destructive webhooks without human-in-the-loop (HITL) approval?
- **RAG Data Poisoning**: Can an attacker upload malicious documents into vector stores to hijack retrieval?

#### 3. Cryptography & Key Management
*See [references/cryptographic-anti-patterns.md](./references/cryptographic-anti-patterns.md)*
- **Timing Attacks**: Are tokens, HMACs, or signatures compared with `==` instead of constant-time comparisons (`hmac.compare_digest`, `crypto.timingSafeEqual`)?
- **Weak Ciphers & Modes**: Is AES running in ECB mode? Is an IV/nonce reused across encryptions in CBC or GCM?
- **Broken PRNG**: Is `Math.random()` or `random.randint()` used for password reset tokens, session IDs, or cryptographic keys?
- **JWT Vulnerabilities**: Is the algorithm header (`alg`) validated against an allowlist? Can `alg: "none"` bypass verification? Is there an asymmetric-to-symmetric key confusion (RS256 vs HS256)?

#### 4. Concurrency & Business Logic Flaws
- **Time-of-Check to Time-of-Use (TOCTOU)**: Is a balance or inventory count checked in one query and decremented in another without transactional locks (`SELECT ... FOR UPDATE`) or atomic conditional updates?
- **State Machine Violations**: Can an order transition directly from `PENDING` to `COMPLETED` without going through `PAID`?
- **Coupon / Promo Code Replay**: Can multiple concurrent requests redeem the same single-use voucher?

#### 5. Cloud, Containers & Infrastructure-as-Code (IaC)
*See [references/cloud-and-iac-security.md](./references/cloud-and-iac-security.md)*
- **Dockerfile Security**: Is the container running as `USER root`? Are multi-stage builds used to exclude compilation tools and secrets?
- **Terraform / CloudFormation**: Are S3 buckets private? Are security groups restricted rather than opening `0.0.0.0/0` on port 22/3389/5432? Are IAM roles granted wildcard `*` permissions?

#### 6. Supply Chain & Secrets
*See [references/supply-chain-and-secrets.md](./references/supply-chain-and-secrets.md)*
- **Dependency Integrity**: Are package versions pinned with lockfiles? Are post-install scripts audited?
- **Secret Management**: Are API keys read from secure environment variables / secret managers (AWS Secrets Manager, HashiCorp Vault) rather than hardcoded in source?

---

### Phase 5: CVSS Scoring, Report & Remediation

Synthesize findings into an authoritative, structured security deliverable:

1. **Calculate Official CVSS v3.1 / v4.0 Scores**:
   - Use `scripts/cvss_calculator.py` to produce exact base scores and vector strings:
     ```bash
     python .agents/skills/security-reviewer/scripts/cvss_calculator.py --vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
     ```
   - Severity Thresholds:
     - **CRITICAL (9.0 - 10.0)**: Unauthenticated RCE, total auth bypass, catastrophic BOLA.
     - **HIGH (7.0 - 8.9)**: Authenticated privilege escalation, SSRF to cloud metadata, stored XSS on admin.
     - **MEDIUM (4.0 - 6.9)**: CSRF, Reflected XSS, business logic flaw with limited impact, timing leak.
     - **LOW (0.1 - 3.9)**: Information disclosure of non-sensitive metadata, minor header omission.
     - **INFORMATIONAL / HARDENING (0.0)**: Defense-in-depth best practice.

2. **Structure the Deliverable**:
   - Use [templates/security-audit-report.md](./templates/security-audit-report.md) for full audit reports.
   - Use [templates/vulnerability-finding.md](./templates/vulnerability-finding.md) for individual vulnerability tickets.
   - Use [templates/threat-model-stride.md](./templates/threat-model-stride.md) when assessing new systems or features.

3. **Deliver Drop-in Code & Regression Tests**:
   - Provide before vs after code diffs.
   - Include an executable unit/integration test demonstrating the exploit payload is rejected.

4. **Issue the Security Sign-Off Verdict**:
   - **`APPROVE (SECURITY CLEARED)`**: No Critical, High, or Medium vulnerabilities found.
   - **`REQUEST_CHANGES (SECURITY BLOCKED)`**: One or more Critical or High vulnerabilities present. Cannot merge to production.
   - **`CONDITIONAL APPROVE (REQUIRES MITIGATION)`**: Medium or Low issues that can be mitigated with compensating controls or tracked follow-up tickets.

---

## Review Modes & Specializations

Activate the corresponding review lens based on the prompt:

| Mode | When to Use | Core Reference |
| :--- | :--- | :--- |
| **Full AppSec 360° Audit** | Full PR security audit, pre-deployment sign-off, red team review | [Full Security Lifecycle](#the-5-phase-security-review-lifecycle) |
| **API & Microservice Security** | REST, GraphQL, gRPC endpoints, auth/BOLA/IDOR scrutiny | [owasp-web-and-api-threats.md](./references/owasp-web-and-api-threats.md) |
| **AI / LLM Application Security** | Agentic workflows, RAG systems, LLM tools, prompt sanitization | [owasp-llm-and-ai-threats.md](./references/owasp-llm-and-ai-threats.md) |
| **Cryptographic & Auth Audit** | Key derivation, tokens, signature verification, session handling | [cryptographic-anti-patterns.md](./references/cryptographic-anti-patterns.md) |
| **Cloud & IaC Hardening** | Terraform, Dockerfile, Kubernetes, AWS/GCP IAM changes | [cloud-and-iac-security.md](./references/cloud-and-iac-security.md) |
| **Supply Chain & Secret Scan** | Dependency updates, lockfiles, leaked credentials | [supply-chain-and-secrets.md](./references/supply-chain-and-secrets.md) |

---

## Tooling & Automation Assets

- **Security & Hygiene Scanners**:
  - [scripts/security_scanner.py](./scripts/security_scanner.py) (Python 3 multi-language scanner)
  - [scripts/security_scanner.ps1](./scripts/security_scanner.ps1) (PowerShell 7 native scanner)
- **CVSS v3.1 / v4.0 Calculators**:
  - [scripts/cvss_calculator.py](./scripts/cvss_calculator.py) (Python 3 CVSS engine)
  - [scripts/cvss_calculator.ps1](./scripts/cvss_calculator.ps1) (PowerShell 7 CVSS engine)
- **Document & Reporting Templates**:
  - [templates/security-audit-report.md](./templates/security-audit-report.md) (Comprehensive Audit Deliverable)
  - [templates/vulnerability-finding.md](./templates/vulnerability-finding.md) (Standard Bug/Vulnerability Ticket)
  - [templates/threat-model-stride.md](./templates/threat-model-stride.md) (Formal STRIDE Analysis Template)
  - [templates/cvss-scorecard.md](./templates/cvss-scorecard.md) (CVSS Matrix & Severity Rubrics)
  - [templates/secure-code-remediation-checklist.md](./templates/secure-code-remediation-checklist.md) (Pre-Merge Security Gate Checklist)
- **In-Depth Reference Guides**:
  - [references/owasp-web-and-api-threats.md](./references/owasp-web-and-api-threats.md) (Web & API Attack Encyclopedia)
  - [references/owasp-llm-and-ai-threats.md](./references/owasp-llm-and-ai-threats.md) (AI & Large Language Model Security)
  - [references/cryptographic-anti-patterns.md](./references/cryptographic-anti-patterns.md) (Ciphers, Salts, Hashes, Timing Attacks)
  - [references/auth-and-access-control-playbook.md](./references/auth-and-access-control-playbook.md) (BOLA, BFLA, OAuth2, RBAC/ABAC)
  - [references/cloud-and-iac-security.md](./references/cloud-and-iac-security.md) (Terraform, Containers, K8s, Cloud IAM)
  - [references/supply-chain-and-secrets.md](./references/supply-chain-and-secrets.md) (Dependencies, Lockfiles, Secrets Scanning)
- **Real-World Walkthrough Examples**:
  - [examples/sample-full-security-audit.md](./examples/sample-full-security-audit.md) (End-to-End Enterprise AppSec Audit)
  - [examples/sample-auth-bypass-remediation.md](./examples/sample-auth-bypass-remediation.md) (Deep Dive Auth Bypass PoC & Fix)
