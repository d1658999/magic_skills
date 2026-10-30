# Research Planner & Zero-Inference Task Architect

> **An industrial-grade skill for researching requirements, investigating codebases, and producing zero-inference specifications and atomic task packets that lower-tier, small-parameter, or literal AI models can execute flawlessly.**

---

## Overview

When building complex software systems using autonomous AI workflows, developers often encounter a fundamental challenge: **model tier disparity**.
- High-reasoning planner models (e.g., Gemini Pro, Claude 3.5 Sonnet, GPT-4o) excel at architecture, domain research, and abstract system design.
- Lower-tier execution engines (e.g., small 7B–14B local models via Ollama/vLLM, Gemini Flash-Lite, Claude Haiku, GPT-4o-mini, GitHub Copilot CLI subagents) are cost-effective, fast, and high-throughput, but struggle with contextual inference, multi-step planning, and architectural ambiguity.

When given loose, high-level instructions, lower-tier models inevitably fail by:
- Hallucinating non-existent library APIs or methods.
- Emitting placeholder slop (`// TODO: implement later`, `# pass`, mock return values).
- Silently swallowing exceptions or dropping edge cases.
- Over-refactoring and modifying unrelated files.
- Drifting away from the project's established conventions.

The **Research Planner** skill solves this problem by enforcing the **Zero-Inference Doctrine**: **Front-load 100% of the research, architectural design, interface definition, edge-case handling, and verification mechanics into the planning phase.** By the time an executor model receives a task packet, zero design decisions remain—only deterministic, step-by-step code implementation.

---

## Directory Structure

```
research-planner/
├── SKILL.md                                 # Core operating doctrine, 5-phase lifecycle & protocols
├── README.md                                # This documentation file
├── templates/
│   ├── requirements-research-dossier.md     # Template for Phase 1 & 2 requirements & reconnaissance
│   ├── master-technical-spec.md             # Template for Phase 3 zero-inference technical spec
│   ├── atomic-task-packet.md                # Template for Phase 4 spoon-fed task packets
│   ├── execution-dag-plan.md                # Template for Phase 4 dependency DAG & rollout plan
│   └── executor-prompt-template.md          # Direct dispatch wrapper for subagents/executors
├── references/
│   ├── zero-inference-spec-guidelines.md    # Guide to writing unambiguous, zero-drift specifications
│   ├── low-tier-model-failure-modes.md      # Taxonomy of 10 small-model failure modes & defenses
│   ├── codebase-reconnaissance-playbook.md  # Systematic playbook for ground-truth repo investigation
│   ├── task-decomposition-and-granularity.md# Principles for slicing tasks into atomic micro-units
│   └── deterministic-verification-patterns.md# Crafting objective verification commands & test gates
├── scripts/
│   ├── validate_spec.py                     # Python validator for specs and task packets
│   ├── validate_spec.ps1                    # PowerShell validator for specs and task packets
│   ├── decompose_tasks.py                   # Python task DAG & file conflict validator
│   └── decompose_tasks.ps1                  # PowerShell task DAG & file conflict validator
└── examples/
    ├── full-planning-walkthrough.md         # End-to-end case study: from vague goal to executed plan
    ├── sample-requirements-dossier.md       # Concrete example of completed requirements dossier
    ├── sample-master-technical-spec.md      # Concrete example of zero-inference technical spec
    └── sample-atomic-task-packet.md         # Concrete example of a dispatch-ready task packet
```

---

## The 5-Phase Planning Lifecycle

1. **Phase 1: 360° Requirements Deconstruction**: Unpack explicit goals, negative constraints ("must NOT do"), implicit contracts, invariants, and performance/security parameters.
2. **Phase 2: Ground-Truth Codebase Reconnaissance**: Extract active AST definitions, verify installed dependency versions, identify test runners, and harvest existing code idioms.
3. **Phase 3: Zero-Inference Architecture & Contract Freezing**: Lock data schemas, interfaces, function signatures, state machines, and error handling matrices. Forbid all design choices during execution.
4. **Phase 4: Atomic Task Decomposition & Prompt Synthesis**: Slice work into isolated 1–2 file task packets with exact line anchors, linear recipes, and negative constraints.
5. **Phase 5: Deterministic Verification & Guardrail Hardening**: Embed copy-pasteable test commands with exact expected exit codes and automated anti-slop scans.

---

## Integration with Orchestration Skills

This skill seamlessly pairs with multi-agent orchestrators:
- **`parallel-subagent-orchestrator`**: The Research Planner generates the master plan, frozen contracts, and disjoint task packets that the Parallel Subagent Orchestrator dispatches and audits across concurrent subagents.
- **`copilot-subagent-orchestrator`**: The Research Planner prepares the exact prompts and verification scripts needed to safely drive local Copilot CLI engines (`ollama-copilot`, `collama`) without TPM/RPM or quality blowouts.

---

## Quick Start: Using the Automated Validation Scripts

### Auditing a Task Packet or Spec (PowerShell / Windows)
```powershell
pwsh .agents/skills/research-planner/scripts/validate_spec.ps1 -SpecFile path/to/task-01.md
```

### Auditing a Task Packet or Spec (Python / Cross-Platform)
```bash
python .agents/skills/research-planner/scripts/validate_spec.py --spec-file path/to/task-01.md
```

### Validating a Task DAG for Dependency Cycles & File Overlaps
```bash
python .agents/skills/research-planner/scripts/decompose_tasks.py --plan-file path/to/execution-dag-plan.md
```
