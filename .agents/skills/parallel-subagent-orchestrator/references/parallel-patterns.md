# Parallel Subagent Execution Patterns

This reference covers the concrete tool patterns for spawning subagents in parallel, managing their workspaces, and running iterative review-and-reassign loops.

---

## Pattern 1: Parallel `invoke_subagent` + `send_message` Loop (Recommended for 2–6 Complex Tasks)

Use `invoke_subagent` when you want direct interactive control over each subagent conversation and want to send follow-up correction messages via `send_message`.

### Step 1: Spawn All Independent Subagents in a Single Turn
Emit multiple `invoke_subagent` tool calls in the **same response turn** so they run concurrently in the background:

```json
[
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "self",
      "Role": "WP-1: Auth Token Service",
      "Workspace": "inherit",
      "Model": "inherit",
      "Prompt": "<Full Zero-Assumption Work Packet WP-1>"
    }
  },
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "self",
      "Role": "WP-2: Session Store Repository",
      "Workspace": "inherit",
      "Model": "inherit",
      "Prompt": "<Full Zero-Assumption Work Packet WP-2>"
    }
  },
  {
    "tool": "invoke_subagent",
    "args": {
      "TypeName": "self",
      "Role": "WP-3: Rate Limiter Middleware",
      "Workspace": "inherit",
      "Model": "inherit",
      "Prompt": "<Full Zero-Assumption Work Packet WP-3>"
    }
  }
]
```

> [!TIP]
> If the `task-worker` custom subagent is installed in `agents/task-worker.md`, pass `"TypeName": "task-worker"` instead of `"self"` so the worker automatically receives strict spec-compliance and anti-slop rules.

### Step 2: Wait for Reactive Completion Notifications
- Stop calling tools at the end of your turn after spawning the subagents.
- The system will automatically wake you up as subagents complete and send you their completion messages.

### Step 3: Audit & Reassign via `send_message`
When Subagent `conv-abc-123` (WP-1) finishes:
1. Run the **4-Gate Review** (`read_file` on WP-1's files + `run_command` for WP-1's tests).
2. If WP-1 has defects, call `send_message`:

```json
{
  "tool": "send_message",
  "args": {
    "Recipient": "conv-abc-123",
    "Message": "<Full Correction Directive detailing exact file/line fixes and re-verification commands>"
  }
}
```

3. Repeat until WP-1 passes all 4 Gates.

---

## Pattern 2: Dynamic `run_workflow` Orchestration (Recommended for Programmable Pipelines or High Fan-Out)

When orchestrating many parallel tasks or enforcing automated review/reassignment loops in code, use the `run_workflow` tool with multi-turn `agent()` instances and `parallel()`.

### Multi-Turn Worker + Reviewer Loop in `run_workflow`

```python
# Example workflow script demonstrating parallel execution + mandatory review & reassignment loop
MAX_RETRIES = 3

 work_packets = [
    {
        "id": "WP-1",
        "role": "WP-1: Parser Module",
        "allowed_files": ["src/parser.py", "tests/test_parser.py"],
        "spec": """<Detailed Zero-Assumption Work Packet for WP-1>""",
    },
    {
        "id": "WP-2",
        "role": "WP-2: Validator Module",
        "allowed_files": ["src/validator.py", "tests/test_validator.py"],
        "spec": """<Detailed Zero-Assumption Work Packet for WP-2>""",
    },
]

worker_schema = {
    "type": "object",
    "properties": {
        "modified_files": {"type": "array", "items": {"type": "string"}},
        "test_command_run": {"type": "string"},
        "tests_passed": {"type": "boolean"},
        "summary": {"type": "string"},
    },
    "required": ["modified_files", "test_command_run", "tests_passed", "summary"],
}

review_schema = {
    "type": "object",
    "properties": {
        "approved": {"type": "boolean"},
        "scope_ok": {"type": "boolean"},
        "spec_complete": {"type": "boolean"},
        "quality_excellent": {"type": "boolean"},
        "defects": {"type": "array", "items": {"type": "string"}},
        "correction_directive": {"type": "string"},
    },
    "required": [
        "approved",
        "scope_ok",
        "spec_complete",
        "quality_excellent",
        "defects",
        "correction_directive",
    ],
}

async def execute_and_verify_packet(wp):
    # Create a persistent multi-turn worker agent that keeps its context across reassignments
    worker = agent(role=wp["role"], workspace="inherit")
    prompt = wp["spec"]

    for attempt in range(1, MAX_RETRIES + 1):
        log(f"[{wp['id']}] Starting execution attempt {attempt}/{MAX_RETRIES}")
        worker_report = await worker(prompt, schema=worker_schema)

        # Spawn an independent audit or inspect files directly
        review_prompt = f"""
You are the strict QA Auditor reviewing {wp['id']} (Attempt {attempt}).
Allowed files: {wp['allowed_files']}
Worker self-report: {worker_report}
Original Spec:
{wp['spec']}

1. Read every file in {wp['allowed_files']} and check git status/diff.
2. Verify responsibility boundaries (no unauthorized files touched).
3. Check 100% of spec requirements, edge cases, and zero TODO/placeholder slop.
4. Run the verification test suite yourself.
5. If ANY issue exists, set approved=False and write a surgical correction_directive with exact file paths and line numbers.
"""
        audit = await agent(
            review_prompt,
            schema=review_schema,
            role=f"Audit {wp['id']} (#{attempt})",
        )

        if audit["approved"]:
            log(f"[{wp['id']}] APPROVED on attempt {attempt}!")
            del worker
            return {"id": wp["id"], "attempts": attempt, "report": worker_report}

        log(f"[{wp['id']}] REJECTED on attempt {attempt}. Defects: {audit['defects']}")
        prompt = f"""
REVIEW VERDICT: CHANGES REQUIRED (Attempt {attempt} failed audit)

Defects found during mandatory audit:
{chr(10).join('- ' + d for d in audit['defects'])}

Correction Directive:
{audit['correction_directive']}

Fix all defects above, re-run all verification commands, and submit an updated completion report.
"""

    del worker
    raise RuntimeError(f"[{wp['id']}] Failed quality audit after {MAX_RETRIES} attempts.")

phase("Parallel Execution & Iterative QA")
results = await parallel(work_packets, execute_and_verify_packet)
log("All parallel work packets passed audit:", results)
```

---

## Choosing the Workspace Mode (`Workspace` Parameter)

| Mode | When to Use | Pros & Cons |
| :--- | :--- | :--- |
| `"inherit"` | Parallel subagents edit **strictly disjoint file sets** (enforced by your File Ownership Matrix). | Zero merge overhead; changes are immediately visible in the main workspace for Lead Agent review. |
| `"share"` | Parallel subagents need isolated working trees sharing the underlying repo (like `git worktree`). | Prevents build artifact collisions while keeping disk usage fast and light. |
| `"branch"` | Parallel subagents must edit overlapping files or run destructive/conflicting build steps. | Full isolation, but requires explicit diff extraction/merging after review. |
