# Task Decomposition & Granularity Heuristics

> **Reference Purpose**: Tactical rules for breaking complex software requirements into bite-sized, deterministic micro-tasks that small-parameter (7B–14B) and low-reasoning AI models can execute without cognitive fatigue or context collapse.

---

## 1. The Cognitive Load Ceiling of Low-Tier Models

Small-parameter models have an extremely sharp drop-off in output quality as task complexity grows:
- **1 Responsibility + 1 Target File (< 100 LoC change)**: ~95% zero-defect completion rate.
- **2 Responsibilities + 2 Target Files (100–200 LoC change)**: ~65% completion rate; frequent placeholder comments or missed edge cases.
- **Multi-File Architecture (> 250 LoC change)**: < 20% completion rate; almost guaranteed hallucination, broken imports, or skipped logic.

**Core Slicing Law**: If a task requires more than 150 lines of new/modified code or touches more than 2 files, it **MUST** be split into smaller sub-tasks.

---

## 2. The 4 Slicing Principles

### Principle 1: Single File Write Target
Every task packet should ideally permit modifications to **exactly one file**.
- If a task requires creating an interface in `types.ts` and implementing it in `service.ts`, split it:
  - `Task A`: Create and export the interface in `types.ts`.
  - `Task B`: Import the pre-existing interface in `service.ts` and write the implementation.

### Principle 2: Contract Pre-Baking (Layered Foundation)
Always sequence work from deepest dependencies to surface interfaces:
1. **Layer 0**: Types, Interfaces, DTOs, Enums.
2. **Layer 1**: Configuration, Schemas, Database Migrations.
3. **Layer 2**: Low-level Repositories / Data Access.
4. **Layer 3**: Business Logic Services.
5. **Layer 4**: HTTP Controllers, Routes, Event Listeners.
6. **Layer 5**: Integration & End-to-End Tests.

*An executor at Layer 3 should never have to design or modify a Layer 0 interface.*

### Principle 3: Linear State Flow (No Branching Trees Across Tasks)
Avoid tasks that say: *"If the user selects Option A, do X, otherwise do Y."*
Instead, make each state or option a distinct task or flatten the flow into an explicit, deterministic sequence.

### Principle 4: Self-Contained Context Windows
Do not expect the executor model to "remember" what it did in Task 1 when executing Task 3. Every task packet must include all necessary types, signatures, and context snippets self-contained in the prompt.

---

## 3. Slicing Anti-Patterns (And How to Fix Them)

| Anti-Pattern | Manifestation | Why Low-Tier Models Fail | How the Planner Must Fix It |
| :--- | :--- | :--- | :--- |
| **The Feature Dump** | *"Implement authentication system with JWT and Redis"* | Model writes a 400-line monolithic file with mocks, placeholders, and broken imports. | Split into 5 atomic tasks: 1) Types, 2) TokenSigner, 3) TokenValidator, 4) RedisStore, 5) FastifyRoutes. |
| **The Ping-Pong Task** | Task 1 edits `auth.ts`, Task 2 edits `user.ts`, Task 3 edits `auth.ts` again. | Model gets confused by intermediate states and overwrites previous changes. | Group all changes to `auth.ts` into a single, cohesive task or freeze `auth.ts` before moving to dependent files. |
| **The Implicit Contract** | Task 2 assumes Task 1 created a specific function signature without documenting it. | If Task 1 made even a minor naming deviation, Task 2 fails with import errors. | The Planner authors the exact interface in the master spec *before* either task runs. |
| **The "Write Tests Later" Trap** | Asking the model to write 200 lines of logic first, and unit tests in a separate step. | The model writes untestable, tightly coupled code with hard-to-mock internal dependencies. | Provide the pre-written unit tests first (TDD), or mandate writing unit tests alongside the micro-function. |

---

## 4. The Granularity Sizing Rubric

Before finalizing a task packet, evaluate it against this checklist:

1. **File Count**: Does this task touch ≤ 2 files? (Target: 1 file).
2. **Line Count**: Is the total generated code ≤ 150 lines?
3. **Cognitive Branches**: Does the logic contain ≤ 3 logical branches / conditions?
4. **Tool Invocations**: Can the model complete the work in a single turn using `write_file` or `edit_file` followed by 1 terminal verification command?
5. **External Decisions**: Are there ZERO architectural decisions left for the model to make?

If any answer is **NO**, slice the task further.
