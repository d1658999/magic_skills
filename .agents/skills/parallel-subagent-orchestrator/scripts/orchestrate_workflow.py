"""Reusable `run_workflow` script for Parallel Subagent Orchestration with Mandatory QA & Reassignment.

Run via `run_workflow`:
  run_workflow(
      ScriptPath="/abs/path/to/skills/parallel-subagent-orchestrator/scripts/orchestrate_workflow.py",
      Description="Execute parallel work packets with mandatory 4-gate review and iterative reassignment",
      Args={
          "max_retries": 3,
          "workspace": "inherit",
          "work_packets": [
              {
                  "id": "WP-1",
                  "role": "WP-1: Auth Validator",
                  "allowed_files": ["src/auth/validator.ts", "tests/auth/validator.test.ts"],
                  "spec": "<Full Zero-Assumption Work Packet Markdown>",
                  "verification_command": "npx vitest run tests/auth/validator.test.ts"
              }
          ]
      }
  )
"""

from advanced import parallel

MAX_RETRIES = int(args.get("max_retries", 3)) if "args" in dir() and isinstance(args, dict) else 3
DEFAULT_WORKSPACE = args.get("workspace", "inherit") if "args" in dir() and isinstance(args, dict) else "inherit"
WORK_PACKETS = args.get("work_packets", []) if "args" in dir() and isinstance(args, dict) else []

WORKER_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "files_created_or_modified": {
            "type": "array",
            "items": {"type": "string"},
        },
        "verification_command_executed": {"type": "string"},
        "verification_passed": {"type": "boolean"},
        "edge_cases_handled": {
            "type": "array",
            "items": {"type": "string"},
        },
        "implementation_summary": {"type": "string"},
    },
    "required": [
        "files_created_or_modified",
        "verification_command_executed",
        "verification_passed",
        "edge_cases_handled",
        "implementation_summary",
    ],
}

AUDIT_SCORECARD_SCHEMA = {
    "type": "object",
    "properties": {
        "gate1_responsibility_scope_pass": {"type": "boolean"},
        "gate2_spec_and_no_slop_pass": {"type": "boolean"},
        "gate3_code_quality_pass": {"type": "boolean"},
        "gate4_independent_verification_pass": {"type": "boolean"},
        "approved": {"type": "boolean"},
        "defects": {
            "type": "array",
            "items": {"type": "string"},
        },
        "correction_directive": {"type": "string"},
    },
    "required": [
        "gate1_responsibility_scope_pass",
        "gate2_spec_and_no_slop_pass",
        "gate3_code_quality_pass",
        "gate4_independent_verification_pass",
        "approved",
        "defects",
        "correction_directive",
    ],
}


async def run_and_audit_packet(wp):
    wp_id = wp["id"]
    role = wp.get("role", f"{wp_id} Worker")
    allowed_files = wp.get("allowed_files", [])
    spec = wp["spec"]
    verify_cmd = wp.get("verification_command", "")
    ws = wp.get("workspace", DEFAULT_WORKSPACE)

    # Persistent multi-turn worker retains conversation context across reassignments
    worker = agent(role=role, workspace=ws)
    current_prompt = spec

    for attempt in range(1, MAX_RETRIES + 1):
        log(f"[{wp_id}] Dispatching worker (Attempt {attempt}/{MAX_RETRIES})...")
        worker_report = await worker(current_prompt, schema=WORKER_REPORT_SCHEMA)

        log(f"[{wp_id}] Worker finished Attempt {attempt}. Starting Mandatory 4-Gate Audit...")
        audit_prompt = f"""You are the Lead QA Auditor performing a strict 4-Gate Review of Work Packet {wp_id} (Attempt {attempt}/{MAX_RETRIES}).

### Assigned Responsibility & Allowed Write Files:
{allowed_files}

### Required Verification Command:
{verify_cmd}

### Original Zero-Assumption Specification:
{spec}

### Subagent Self-Report (UNTRUSTED — VERIFY INDEPENDENTLY):
{worker_report}

### Mandatory Audit Instructions:
1. **Gate 1 (Responsibility & Scope)**: Read every file in {allowed_files} and check if any unauthorized files were modified. Confirm all required files exist.
2. **Gate 2 (Spec Compliance & Anti-Slop)**: Compare every exported signature, type, step, and edge case in the actual file contents against the Original Specification. Check for forbidden shortcuts (`TODO`, `FIXME`, `HACK`, placeholders, `@ts-ignore`, `# type: ignore`, `as any`, fake tests).
3. **Gate 3 (Code Quality)**: Check logic correctness, error handling, naming conventions, and documentation integrity.
4. **Gate 4 (Independent Verification)**: Run `{verify_cmd}` yourself to confirm all tests and checks pass.

Set `approved = true` ONLY if ALL 4 Gates pass with zero defects.
If ANY Gate fails, set `approved = false`, list each defect with exact file path and line numbers in `defects`, and write a comprehensive `correction_directive` instructing the subagent how to fix every defect without breaking passing code.
"""
        audit = await agent(
            audit_prompt,
            schema=AUDIT_SCORECARD_SCHEMA,
            role=f"QA Audit {wp_id} (#{attempt})",
            workspace=ws,
        )

        all_gates_passed = (
            audit["gate1_responsibility_scope_pass"]
            and audit["gate2_spec_and_no_slop_pass"]
            and audit["gate3_code_quality_pass"]
            and audit["gate4_independent_verification_pass"]
            and audit["approved"]
        )

        if all_gates_passed:
            log(f"[{wp_id}] APPROVED on Attempt {attempt}!")
            del worker
            return {
                "id": wp_id,
                "status": "APPROVED",
                "attempts": attempt,
                "worker_report": worker_report,
                "audit": audit,
            }

        log(f"[{wp_id}] REJECTED on Attempt {attempt}. Defects found: {len(audit['defects'])}")
        for d in audit["defects"]:
            log(f"  - [{wp_id} Defect] {d}")

        current_prompt = f"""# CORRECTION DIRECTIVE: {wp_id} — Review Iteration #{attempt}
## Audit Verdict: CHANGES REQUIRED

Your submission failed the mandatory 4-Gate Quality & Responsibility Audit:
- Gate 1 (Responsibility Scope): {'PASS' if audit['gate1_responsibility_scope_pass'] else 'FAIL'}
- Gate 2 (Spec & Anti-Slop): {'PASS' if audit['gate2_spec_and_no_slop_pass'] else 'FAIL'}
- Gate 3 (Code Quality): {'PASS' if audit['gate3_code_quality_pass'] else 'FAIL'}
- Gate 4 (Verification): {'PASS' if audit['gate4_independent_verification_pass'] else 'FAIL'}

### Blocking Defects to Fix Immediately:
{chr(10).join(f'{i+1}. {d}' for i, d in enumerate(audit['defects']))}

### Detailed Correction Instructions:
{audit['correction_directive']}

Apply all fixes above strictly within your allowed files ({allowed_files}), re-run `{verify_cmd}`, and return an updated completion report.
"""

    del worker
    raise RuntimeError(
        f"Work Packet {wp_id} failed mandatory quality audit after {MAX_RETRIES} attempts."
    )


if not WORK_PACKETS:
    log("No work_packets provided in Args. Pass Args={'work_packets': [...]} to run_workflow.")
else:
    phase("Parallel Subagent Execution & Iterative QA Loop")
    results = await parallel(WORK_PACKETS, run_and_audit_packet)
    phase("Orchestration Summary")
    for res in results:
        log(f"{res['id']}: {res['status']} in {res['attempts']} attempt(s)")
    print(results)
