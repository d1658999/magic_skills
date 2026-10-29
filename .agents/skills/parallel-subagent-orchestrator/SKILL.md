---
name: parallel-subagent-orchestrator
description: >-
  Orchestrates parallel subagents using ultra-detailed task specifications,
  strict responsibility boundaries, mandatory code/output audits, and iterative
  reassignment loops until excellence is achieved. Use this skill whenever decomposing
  a complex task into parallel subagent tasks, proposing technical specs for subagents,
  or reviewing and correcting subagent deliverables.
---

# Parallel Subagent Orchestrator Skill

This skill defines the operating protocol for a **Lead Orchestrator Agent** that plans, specifies, dispatches, audits, and iteratively refines work across multiple parallel subagents.

## Core Operating Doctrine

1. **Assume Subagents Are Literal & Context-Blind**: Never assume a subagent is "smart" enough to infer architecture, edge cases, coding conventions, or unstated requirements. Subagents start with a blank conversation context. Every ambiguity left in a prompt becomes a bug in the output.
2. **Front-Load All Intelligence into the Spec**: The Original (Lead) Agent is solely responsible for architectural design, shared contracts, and ultra-detailed task specifications *before* spawning any subagent.
3. **Strict Responsibility Isolation**: Parallel subagents must operate on mutually exclusive file/module boundaries or isolated workspaces so they never overwrite or conflict with one another.
4. **Trust Nothing, Verify Everything**: A subagent claiming *"Task complete, all tests pass"* is an unverified claim, not a fact. The Original Agent **MUST** inspect every modified file, verify responsibility boundaries, and run verification checks independently.
5. **Relentless Reassignment Until Excellence**: If a subagent's work is incomplete, violates its responsibility boundary, contains shortcuts/placeholders, or fails quality standards, the Original Agent **MUST NOT** accept it. Reassign the subagent with surgical correction feedback and re-review until the deliverable meets an excellent quality bar.

---

## The 5-Phase Orchestration Lifecycle

```
[Phase 1: Recon & Architecture Lock]
        │
        ▼
[Phase 2: Proposal & Zero-Assumption Spec] ──► (Optional User Approval Gate)
        │
        ▼
[Phase 3: Parallel Subagent Spawn] (Work Packet 1..N concurrently)
        │
        ▼
[Phase 4: Mandatory Audit & Responsibility Review]
        │
        ├──► ❌ Fails Spec / Scope / Quality ──► [Phase 5A: Reassign Subagent (send_message)] ──┐
        │                                                                                       │
        └──► ✅ Passes All Checks ◄─────────────────────────────────────────────────────────────┘
        │
        ▼
[Phase 5B: Holistic Integration & Goal Verification]
```

---

### Phase 1: Deep Reconnaissance & Architecture Lock (Lead Agent Only)

Before drafting tasks or spawning subagents, the Original Agent **must** gather ground-truth context:

1. **Map the Codebase**: Locate all relevant files, existing patterns, naming conventions, error-handling idioms, and build/test commands.
2. **Define Shared Contracts First**: If Parallel Task A produces data or interfaces consumed by Parallel Task B, define the exact types, schemas, function signatures, and file paths up front (or create the shared interface file yourself before spawning subagents).
3. **Verify Tooling & Test Commands**: Identify the exact lint, typecheck, and test commands that work in the environment so you can embed them directly into subagent instructions.

---

### Phase 2: Detailed Proposal & Zero-Assumption Task Specification

Produce a structured **Master Orchestration Plan & Spec** (use [templates/master-plan-spec.md](./templates/master-plan-spec.md)).

For **every** parallel task, author a **Zero-Assumption Work Packet** (use [templates/subagent-work-packet.md](./templates/subagent-work-packet.md) and consult [references/spec-writing-guide.md](./references/spec-writing-guide.md)). Each Work Packet **MUST** contain:

1. **Task ID & Single-Sentence Objective**: Clear, unambiguous mission statement.
2. **Strict Responsibility Boundary (Scope Lock)**:
   - **Allowed to Create/Modify**: Exact absolute paths of files the subagent is permitted to touch.
   - **Read-Only Reference Files**: Exact absolute paths with line numbers of existing files to follow as patterns.
   - **Strictly Forbidden (Out of Scope)**: Files, directories, or architectural concerns the subagent **must not** touch.
3. **Exact Technical Specification**:
   - Complete function/class/interface signatures, parameter types, and return types.
   - Step-by-step algorithmic logic and state transitions (leave zero design guesswork).
   - Required error handling and edge-case behaviors (e.g., `null`/empty inputs, timeout, invalid state, boundary values).
   - Code snippets or pattern examples copied directly from the codebase so the subagent matches existing style.
4. **Prohibited Shortcuts (Anti-Slop Rules)**:
   - Explicitly forbid `TODO`, `FIXME`, `pass`, `unimplemented!()`, hardcoded mock returns in production code, silent `catch {}` blocks, or disabling linter/type rules (`any`, `@ts-ignore`, `# noqa`).
5. **Self-Verification Commands**:
   - Exact shell commands the subagent must execute to verify compilation, linting, and unit tests before finishing.
6. **Required Completion Report Format**:
   - List of files created/modified, summary of implementation, verification command outputs, and confirmation of zero out-of-scope edits.

> [!IMPORTANT]
> If the user requested to review a proposal/spec before execution, or if requirements have major architectural trade-offs, present the Master Plan & Spec to the user first. Otherwise, proceed directly to Phase 3 once the spec is complete.

---

### Phase 3: Parallel Subagent Dispatch

Spawn subagents in parallel so independent tasks execute concurrently (see [references/parallel-patterns.md](./references/parallel-patterns.md)):

1. **Spawn Concurrently**:
   - Call `invoke_subagent` for all independent work packets in the **same turn**, or use `run_workflow` with `parallel(...)` for large fan-out tasks.
   - Choose `Workspace: "inherit"` **only** when file write sets are 100% disjoint across parallel subagents. Use `Workspace: "branch"` or `"share"` if subagents might run conflicting builds or touch overlapping areas.
2. **Maintain the Subagent Registry**:
   - Record every spawned subagent's `conversationId`, `Task ID`, `Role`, `Allowed Files`, and `Status` (`RUNNING` | `NEEDS_REVIEW` | `REASSIGNED` | `APPROVED`).
3. **Reactive Wait**:
   - Do not poll in a loop. Wait for subagent completion notifications before starting the review for each completed subagent.

---

### Phase 4: Mandatory Audit & Responsibility Review (Never Skip)

When a subagent reports completion, the Original Agent **MUST** treat the deliverable as an untrusted pull request and execute the **4-Gate Audit Protocol** (detailed in [references/review-and-qa-rubric.md](./references/review-and-qa-rubric.md) and scored via [templates/review-scorecard.md](./templates/review-scorecard.md)):

#### Gate 1: Responsibility & Boundary Audit
- Check `git status` / `git diff` or file timestamps.
- Did the subagent modify **only** the files in its `Allowed to Create/Modify` list?
- Did it accidentally revert, overwrite, or pollute another subagent's files or shared config?
- Did it fulfill 100% of its assigned responsibility without offloading work to "future tasks"?

#### Gate 2: Spec Compliance & Anti-Shortcut Audit
- **Read the actual code** written by the subagent using `read_file` (do not rely on the subagent's summary).
- Verify every function signature, data structure, and edge case listed in the Work Packet spec.
- Grep/scan the modified files for forbidden shortcuts: `TODO`, `FIXME`, `HACK`, `XXX`, placeholder implementations, suppressed warnings, or swallowed exceptions.

#### Gate 3: Code Quality & Craftsmanship Audit
- Verify adherence to project conventions, naming, modularity, type safety, resource cleanup, and documentation integrity.
- Check for subtle logic bugs, off-by-one errors, race conditions, or missing null/error checks.

#### Gate 4: Independent Verification Execution
- Run the build, linter, typechecker, and tests **yourself** (or inspect verifiable command outputs) to confirm they genuinely pass.

---

### Phase 5: Iterative Reassignment Loop & Final Integration

#### 5A: Reassigning Defective or Subpar Work
If **any** of Gates 1–4 fail:

1. **Mark Status as `REASSIGNED`**.
2. **Message the Existing Subagent**: Use `send_message(Recipient=<conversationId>, Message=...)` so the subagent retains its working context and fixes its own mistakes (see [references/reassignment-protocol.md](./references/reassignment-protocol.md) and [templates/correction-directive.md](./templates/correction-directive.md)).
3. **Include Surgical Correction Details**:
   - **Failed Gate(s)**: Explicitly state whether it failed Responsibility Scope, Spec Compliance, Code Quality, or Verification.
   - **Exact Defect Locations**: File paths and line numbers (`path/to/file.ts:L42-L58`).
   - **Current vs. Required Behavior**: Show what the code currently does and the exact change required.
   - **Re-Verification Mandate**: Require the subagent to re-run verification commands and report back.
4. **Re-Audit on Return**: When the reassigned subagent replies, run the full **4-Gate Audit Protocol** again. Repeat until all gates pass with excellence.
5. **Circuit Breaker (Max 3 Reassignments per Subagent)**:
   - If a subagent fails 3 consecutive correction rounds on the same issue, terminate the subagent (`manage_subagents(Action="kill")`), refine the spec or spawn a fresh `"pro"`-tier subagent, or apply the final surgical fix directly as the Lead Agent and document why.

#### 5B: Holistic Integration & Goal Check
Once **all** parallel subagents have earned `APPROVED` status:

1. **Cross-Boundary Integration Check**: Verify that all parallel modules wire together cleanly (imports, exports, shared types, routing, configuration).
2. **End-to-End Verification**: Run the full project build, test suite, and any integration/smoke checks.
3. **Goal Alignment Check**: Re-read the user's original prompt word-for-word to confirm every explicit and implicit goal has been met at the highest quality standard.

---

## Reference Manual & Templates

Load these files on-demand during orchestration:

- **Guides & Protocols (`references/`)**:
  - [spec-writing-guide.md](./references/spec-writing-guide.md): How to write bulletproof, zero-assumption specs for subagents.
  - [review-and-qa-rubric.md](./references/review-and-qa-rubric.md): Comprehensive 4-Gate audit checklist and anti-slop detection rules.
  - [reassignment-protocol.md](./references/reassignment-protocol.md): How to conduct iterative correction loops via `send_message` and handle stubborn failures.
  - [parallel-patterns.md](./references/parallel-patterns.md): Tool patterns for `invoke_subagent`, `send_message`, `manage_subagents`, and `run_workflow`.
- **Copy-Paste Templates (`templates/`)**:
  - [master-plan-spec.md](./templates/master-plan-spec.md): Master orchestration plan and decomposition proposal.
  - [subagent-work-packet.md](./templates/subagent-work-packet.md): Prompt template for spawning a subagent with a detailed spec.
  - [review-scorecard.md](./templates/review-scorecard.md): Audit scorecard for evaluating subagent work.
  - [correction-directive.md](./templates/correction-directive.md): Structured prompt for reassigning a subagent to fix defects.
- **Examples & Utilities**:
  - [full-orchestration-walkthrough.md](./examples/full-orchestration-walkthrough.md): Complete real-world example of planning, parallel spawning, rejecting flawed subagent work, reassigning, and achieving final approval.
  - [validate_work_packet.py](./scripts/validate_work_packet.py): Python script to validate work packet specs and scan subagent target files for forbidden placeholders (`TODO`, `FIXME`, etc.).
  - [orchestrate_workflow.py](./scripts/orchestrate_workflow.py): Ready-to-run `run_workflow` script that executes parallel work packets with an automated 4-Gate QA audit and iterative reassignment loop.
