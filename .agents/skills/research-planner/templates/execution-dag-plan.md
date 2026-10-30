# Execution DAG & Dependency Plan

> **Artifact Purpose**: Topological execution roadmap mapping out task dependencies, concurrency stages, milestone checkpoints, and failure recovery procedures. Ensures that low-tier models or parallel subagents are dispatched only when all prerequisite interfaces are completely locked and verified.

---

## 1. Master Execution Flowchart (Mermaid DAG)

```mermaid
flowchart TD
    subgraph Stage0["Stage 0: Foundation & Contracts (Sequential)"]
        T01["TASK-001: Define Shared Interfaces (src/types/auth.ts)"]
        T02["TASK-002: Add Configuration Keys (src/config/jwt.ts)"]
    end

    subgraph Stage1["Stage 1: Core Logic & Storage (Parallel Eligible)"]
        T03["TASK-003: Implement Token Signer (src/services/signer.ts)"]
        T04["TASK-004: Implement Token Validator (src/services/validator.ts)"]
        T05["TASK-005: Implement Redis Store (src/repos/token-store.ts)"]
    end

    subgraph Stage2["Stage 2: Orchestration & Service Wiring (Sequential)"]
        T06["TASK-006: Assemble AuthService (src/services/auth.service.ts)"]
    end

    subgraph Stage3["Stage 3: HTTP API & Middleware (Sequential)"]
        T07["TASK-007: Wire Auth Controller (src/routes/auth.routes.ts)"]
        T08["TASK-008: Wire Auth Middleware (src/middleware/auth.mw.ts)"]
    end

    subgraph Stage4["Stage 4: End-to-End Verification"]
        T09["TASK-009: Integration Test Suite (tests/e2e/auth.e2e.ts)"]
    end

    T01 --> T03
    T01 --> T04
    T01 --> T05
    T02 --> T03
    T02 --> T04

    T03 --> T06
    T04 --> T06
    T05 --> T06

    T06 --> T07
    T06 --> T08

    T07 --> T09
    T08 --> T09
```

---

## 2. Stage Breakdown & Dispatch Registry

### Stage 0: Foundation & Interfaces (Must complete before any business logic)
| Task ID | Task Title | Permitted Write Files | Dependencies | Concurrency Mode | Verification Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TASK-001` | Define Auth Interfaces | `src/types/auth.ts` | None | Sequential | `npx tsc --noEmit` |
| `TASK-002` | Add JWT Config Schema | `src/config/jwt.ts` | None | Sequential | `npx tsc --noEmit` |

### Stage 1: Isolated Units (Parallel execution safe)
| Task ID | Task Title | Permitted Write Files | Dependencies | Concurrency Mode | Verification Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TASK-003` | Implement Token Signer | `src/services/signer.ts` | `TASK-001`, `TASK-002` | Parallel (Slot 1) | Unit tests pass |
| `TASK-004` | Implement Token Validator | `src/services/validator.ts` | `TASK-001`, `TASK-002` | Parallel (Slot 2) | Unit tests pass |
| `TASK-005` | Implement Redis Store | `src/repos/token-store.ts` | `TASK-001` | Parallel (Slot 3) | Unit tests pass |

### Stage 2: Service Composition
| Task ID | Task Title | Permitted Write Files | Dependencies | Concurrency Mode | Verification Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TASK-006` | Assemble AuthService | `src/services/auth.service.ts` | `TASK-003`, `TASK-004`, `TASK-005` | Sequential | Unit tests pass |

### Stage 3: API & Route Wiring
| Task ID | Task Title | Permitted Write Files | Dependencies | Concurrency Mode | Verification Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TASK-007` | Wire Auth Routes | `src/routes/auth.routes.ts` | `TASK-006` | Sequential | Route tests pass |
| `TASK-008` | Wire Auth Middleware | `src/middleware/auth.mw.ts` | `TASK-006` | Sequential | Middleware tests pass |

### Stage 4: Holistic Verification
| Task ID | Task Title | Permitted Write Files | Dependencies | Concurrency Mode | Verification Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TASK-009` | Run Full E2E Suite | `tests/e2e/auth.e2e.ts` | `TASK-007`, `TASK-008` | Final Check | Full suite passes |

---

## 3. Disjoint Workspace & File Safety Rules

When dispatching tasks in parallel (e.g., Stage 1):
1. **Zero File Overlaps**: No two concurrent tasks may list the same file in their permitted write files.
2. **Read-Only Dependencies**: Files created in earlier stages become strictly read-only for subsequent parallel tasks.
3. **Workspace Isolation**: If running under Antigravity `invoke_subagent`, use `Workspace: "inherit"` only when file sets are 100% disjoint; otherwise use `Workspace: "branch"`.

---

## 4. Failure Recovery & Circuit Breakers

### Executor Failure Scenarios:
1. **Scenario A: Compilation or Test Failure**:
   - Do NOT advance the DAG.
   - Send the specific compiler/test error output back to the executor using the correction directive.
   - Max 2 correction attempts before terminating the executor.
2. **Scenario B: Out-of-Scope File Edits**:
   - Revert out-of-scope edits via `git checkout -- <unauthorized-file>`.
   - Re-instruct the model with strict file boundaries.
3. **Scenario C: Persistent Hallucination / Slop**:
   - Kill the subagent.
   - Split the task into two smaller micro-tasks or switch execution model to a higher-tier engine.
