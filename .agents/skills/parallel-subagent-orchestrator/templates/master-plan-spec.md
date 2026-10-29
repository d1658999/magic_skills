# Master Orchestration Plan & Specification

## 1. Goal & Architectural Overview
- **User Goal**: `<Clear statement of the end goal and quality bar>`
- **Architectural Approach**: `<How the system works end-to-end and how components interact>`
- **Pre-Flight Recon Summary**:
  - **Existing Patterns / Conventions**: `<Naming, error handling, test framework, module system>`
  - **Verification Commands**:
    - **Build / Typecheck**: `<exact command>`
    - **Linter**: `<exact command>`
    - **Test Runner**: `<exact command>`

---

## 2. Shared Data Contracts & Interfaces (Locked Pre-Spawn)
> All parallel subagents must adhere strictly to these exact definitions. Do not deviate from field names, types, or signatures.

```ts
// Paste exact shared interfaces, schemas, types, or constants here
```

---

## 3. Parallel Decomposition & File Ownership Matrix
> **Zero-Overlap Rule**: No two parallel subagents in an `"inherit"` workspace may write to the same file. Shared integration files (routers, barrel exports, configs) are wired by the Lead Agent in Phase 5B.

| Work Packet ID | Subagent Role | Core Responsibility | Allowed Write Files (Exclusive) | Read-Only Reference Files | Workspace Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `WP-1` | `<Role Name>` | `<1-sentence scope>` | `path/to/fileA`, `tests/fileA.test` | `path/to/ref1` | `inherit` |
| `WP-2` | `<Role Name>` | `<1-sentence scope>` | `path/to/fileB`, `tests/fileB.test` | `path/to/ref2` | `inherit` |
| `WP-3` | `<Role Name>` | `<1-sentence scope>` | `path/to/fileC`, `tests/fileC.test` | `path/to/ref3` | `inherit` |
| `INTEGRATION` | **Lead Agent** | Final wiring & E2E verification | `path/to/index`, `path/to/router` | All `WP-*` outputs | Main |

---

## 4. Detailed Work Packet Specifications
- **Work Packet `WP-1`**: `<Summary or inline full Work Packet using subagent-work-packet.md>`
- **Work Packet `WP-2`**: `<Summary or inline full Work Packet using subagent-work-packet.md>`
- **Work Packet `WP-3`**: `<Summary or inline full Work Packet using subagent-work-packet.md>`

---

## 5. Live Subagent Orchestration & QA Tracker

| Work Packet ID | Subagent `conversationId` | Attempt # | Gate 1: Scope | Gate 2: Spec | Gate 3: Quality | Gate 4: Tests | Status | Notes / Defects |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| `WP-1` | `<conv-id>` | 1 | ⏳ | ⏳ | ⏳ | ⏳ | `RUNNING` | — |
| `WP-2` | `<conv-id>` | 1 | ⏳ | ⏳ | ⏳ | ⏳ | `RUNNING` | — |
| `WP-3` | `<conv-id>` | 1 | ⏳ | ⏳ | ⏳ | ⏳ | `RUNNING` | — |
