# Jetski Orchestrator (`jetski-orchestrator`)

> **Unified 5-in-1 Multi-Agent Engineering & Parallel Subagent Orchestration Skill for `jetski-cli`**  
> **Fused Skills**: `research-planner` + `verify-tester` + `corner-case-tester` + `code-reviewer` + `security-reviewer` + `parallel-subagent-orchestrator`  
> **Native Primitives**: `define_subagent`, `invoke_subagent`, `send_message`, `manage_subagents`, `run_workflow` (`parallel`, `pipeline`, `phase`, `advanced`)  

---

## Executive Overview

`jetski-orchestrator` consolidates five specialized engineering skills into a single, cohesive **6-Wave Parallel Subagent Orchestration System** tailored specifically for **Jetski CLI (`jetski-cli`)**.

### Why `jetski-orchestrator` Exists
Executing complex engineering tasks sequentially in a single agent session is slow and prone to context degradation. Conversely, spawning uncoordinated subagents without frozen contracts leads to file collisions, architectural drift, happy-path-only testing, and security blind spots.

`jetski-orchestrator` solves both problems simultaneously:
1. **Maximum Parallel Speedup**: Every phase of the engineering lifecycle—reconnaissance, implementation, broad-spectrum functional testing, adversarial corner-case testing, staff code review, and offensive security review—is fanned out across concurrent subagents in parallel waves.
2. **Zero-Inference Quality & Security Governance**: Shared interfaces are locked upfront, write boundaries are 100% disjoint, and every deliverable must pass a **6-Gate Parallel Audit Council** with autonomous **Red-Green-Refactor self-healing**.

---

## Architecture: The 6-Wave Parallel Subagent Pipeline

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                        JETSKI-ORCHESTRATOR: 6-WAVE PARALLEL PIPELINE                     │
├────────────────────────────────────────────┬─────────────────────────────────────────────┤
│ WAVE 1: PARALLEL 360° RECON SWARM (3x)     │ WAVE 2: ZERO-INFERENCE ARCHITECTURE LOCK    │
│ • Subagent 1A: AST, Types & Conventions    │ • Pre-create shared contracts & interfaces  │
│ • Subagent 1B: 4-Pillar RTM & 10D Matrix   │ • Partition disjoint Work Packets (WP-1..N) │
│ • Subagent 1C: AppSec STRIDE & Taint Map   │ • Validate spec & disjoint write boundaries │
├────────────────────────────────────────────┼─────────────────────────────────────────────┤
│ WAVE 3: PARALLEL CODING & TEST FLEET (Nx)  │ WAVE 4: PARALLEL 6-GATE AUDIT COUNCIL (3x)  │
│ • Workers WP-1..K: Disjoint Feature Code   │ • Auditor 4A: Tests, >=90% RTM, Anti-Cheat  │
│ • Worker WP-Verify: >=90% 4-Pillar Tests   │ • Auditor 4B: Staff Code Review (>=75/100)  │
│ • Worker WP-Corner: 10D Adversarial Tests  │ • Auditor 4C: AppSec STRIDE/OWASP/CVSS<7.0  │
├────────────────────────────────────────────┼─────────────────────────────────────────────┤
│ WAVE 5: PARALLEL SELF-HEALING LOOP         │ WAVE 6: HOLISTIC INTEGRATION & SIGN-OFF     │
│ • Concurrent send_message to workers       │ • Wire shared routers / barrel exports      │
│ • Test-First Red -> Green surgical fix     │ • Full E2E regression & mutation check      │
│ • Anti-Cheat git diff audit & 3-Strike CB  │ • Unified 6-Gate Scorecard & Sign-Off Report│
└────────────────────────────────────────────┴─────────────────────────────────────────────┘
```

---

## Directory Structure

```text
.agents/skills/jetski-orchestrator/
├── SKILL.md                                           # Authoritative skill specification for jetski-cli
├── README.md                                          # Architectural overview & CLI quick-start guide
├── references/
│   ├── subagent-swarm-and-workflow-patterns.md        # Jetski-CLI parallel subagent & run_workflow patterns
│   ├── zero-inference-planning-and-recon.md           # Research-Planner: 360° reqs, AST recon, spoon-fed packets
│   ├── verification-and-corner-case-playbooks.md      # Verify-Tester (>=90% RTM) & Corner-Case-Tester (10D + Healing)
│   ├── staff-code-review-playbook.md                  # Code-Reviewer: 6 Doctrines, 8D Scorecard, Concurrency/Perf
│   └── offensive-appsec-and-cvss-playbook.md          # Security-Reviewer: STRIDE, Taint, OWASP Top 10, CVSS v3.1/v4.0
├── templates/
│   ├── master-orchestration-dossier.md                # Unified Spec + 4-Pillar RTM + 10D Matrix + STRIDE + DAG
│   ├── zero-inference-work-packet.md                  # 8-Section Spoon-Fed Subagent Work Packet template
│   ├── subagent-personas-catalog.md                   # Ready-to-use `define_subagent` blueprints for 6 personas
│   ├── unified-6gate-scorecard.md                     # 6-Gate Council Audit Scorecard template
│   ├── surgical-correction-directive.md               # Contextual `send_message` reassignment template
│   └── executive-signoff-report.md                    # Dual-audience Executive Triage & Sign-Off Dossier
├── scripts/
│   ├── jetski_orchestrator.py                         # Unified 10-command Python 3 CLI engine
│   ├── jetski_orchestrator.ps1                        # Native PowerShell 7 CLI wrapper
│   └── jetski_swarm_workflow.py                       # Programmable `run_workflow` parallel orchestration script
└── examples/
    └── full-jetski-orchestration-walkthrough.md       # End-to-end walkthrough of 6-Wave subagent orchestration
```

---

## Quick-Start CLI Reference

`scripts/jetski_orchestrator.py` (and `scripts/jetski_orchestrator.ps1`) consolidates all deterministic verification, generation, scanning, dumb-subagent scaffolding, and scoring scripts from the 5 fused skills into 12 subcommands:

| # | Subcommand | Origin Skill | Purpose |
| :---: | :--- | :--- | :--- |
| 1 | `validate-spec` | `research-planner` | Audits specs/packets for mandatory sections, anti-slop, vague language, and `--strict-literal` dumb-model readiness |
| 2 | `validate-packets` | `research-planner` | Verifies 100% disjoint file write sets across parallel Work Packets |
| 3 | `generate-skeleton` | `research-planner` | Pre-scaffolds "Fill-in-the-Blank" skeleton files with `# === [ANCHOR: IMPLEMENT <fn>] ===` markers for weak subagents |
| 4 | `lock-tests` | `corner-case-tester` | Computes/verifies SHA-256 checksums and assertion counts of test files (`--verify`) to block test tampering |
| 5 | `calc-coverage` | `verify-tester` | Computes Bidirectional RTM Scenario Coverage ($\ge 90.0\%$ across 4 Pillars) |
| 6 | `generate-corner-cases` | `corner-case-tester` | Generates a prioritized P0–P3 10-Dimension Corner-Case Matrix |
| 7 | `run-remediation` | `corner-case-tester` | Runs Red-Green test loop, baseline regression check, and Git Anti-Cheat audit |
| 8 | `audit-diff` | `code-reviewer` | Scans diffs/files for debug leftovers, anti-slop, tautological assertions (`assert True`), and hardcoded test literals |
| 9 | `eval-review-scorecard` | `code-reviewer` | Computes the 8-Dimension Weighted Staff Code Review Scorecard ($\ge 75/100$) |
| 10 | `audit-security` | `security-reviewer` | Scans diffs/files for hardcoded secrets, CWEs, OWASP sinks, weak crypto, and IaC |
| 11 | `calc-cvss` | `security-reviewer` | Computes exact CVSS v3.1 Base, Impact, and Exploitability scores |
| 12 | `generate-council-scorecard` | `jetski-orchestrator` | Synthesizes all 6 Gates into a Unified Council Audit Scorecard |
