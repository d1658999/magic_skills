"""Jetski Orchestrator Multi-Wave Parallel Subagent Pipeline (`run_workflow` Script).

Orchestrates the 6-Wave Parallel Engineering Lifecycle in `jetski-cli`:
- Wave 1 (Optional): Parallel 3-Way Reconnaissance Swarm (`Recon-Codebase-AST`,
  `Recon-RTM-And-Corner-Cases`, `Recon-AppSec-STRIDE`) when `objective` and `auto_recon=True` are passed.
- Wave 3: Parallel Work Packet Execution (`execute_and_audit_packet` across all `work_packets`).
- Wave 4: Parallel 3-Auditor Council per Work Packet (concurrently evaluating all 6 Mandatory Gates:
  Auditor A [Gates 1, 3, 4], Auditor B [Gates 2, 5], Auditor C [Gate 6]).
- Wave 5: Contextual Multi-Turn Self-Healing Loop (re-prompting the persistent `worker` instance
  with consolidated drop-in fixes up to `max_retries` times).

Usage via `run_workflow`:
  run_workflow(
      ScriptPath="C:/Users/pricewu/Documents/SideProject/magic_skills/.agents/skills/jetski-orchestrator/scripts/jetski_swarm_workflow.py",
      Description="Execute parallel work packets with 6-Gate Council Audit and self-healing loop",
      Args={
          "objective": "Implement rate-limited token service",
          "auto_recon": False,
          "max_retries": 3,
          "workspace": "inherit",
          "work_packets": [
              {
                  "id": "WP-1",
                  "role": "WP-1: Core Service",
                  "model": "inherit",
                  "workspace": "inherit",
                  "allowed_files": ["src/service.py", "tests/test_service.py"],
                  "spec": "<Full Zero-Inference Work Packet Markdown>",
                  "verification_command": "pytest tests/test_service.py"
              }
          ]
      }
  )
"""

try:
    from advanced import best_of, fallback, parallel, retry, verify
except ImportError:
    best_of = None
    fallback = None
    retry = None
    verify = None

WORKFLOW_ARGS = args if ("args" in dir() and isinstance(args, dict)) else {}
OBJECTIVE = WORKFLOW_ARGS.get("objective", "")
AUTO_RECON = bool(WORKFLOW_ARGS.get("auto_recon", False))
MAX_RETRIES = int(WORKFLOW_ARGS.get("max_retries", 3))
DEFAULT_WORKSPACE = WORKFLOW_ARGS.get("workspace", "inherit")
DEFAULT_FALLBACK_MODEL = WORKFLOW_ARGS.get("fallback_model", "pro")
DEFAULT_USE_BEST_OF = int(WORKFLOW_ARGS.get("use_best_of", 1))
WORK_PACKETS = WORKFLOW_ARGS.get("work_packets", [])

# ==============================================================================
# 1. JSON SCHEMAS FOR STRUCTURED SUBAGENT OUTPUTS
# ==============================================================================

RECON_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "domain": {"type": "string"},
        "key_findings": {
            "type": "array",
            "items": {"type": "string"},
        },
        "constraints_and_contracts": {
            "type": "array",
            "items": {"type": "string"},
        },
        "recommended_verification_commands": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "domain",
        "key_findings",
        "constraints_and_contracts",
        "recommended_verification_commands",
    ],
}

WORKER_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "files_created_or_modified": {
            "type": "array",
            "items": {"type": "string"},
        },
        "verification_command_executed": {"type": "string"},
        "verification_passed": {"type": "boolean"},
        "rtm_scenarios_covered": {
            "type": "array",
            "items": {"type": "string"},
        },
        "corner_cases_handled": {
            "type": "array",
            "items": {"type": "string"},
        },
        "implementation_summary": {"type": "string"},
    },
    "required": [
        "files_created_or_modified",
        "verification_command_executed",
        "verification_passed",
        "rtm_scenarios_covered",
        "corner_cases_handled",
        "implementation_summary",
    ],
}

COUNCIL_AUDITOR_SCHEMA = {
    "type": "object",
    "properties": {
        "auditor_role": {"type": "string"},
        "gates_evaluated": {
            "type": "array",
            "items": {"type": "string"},
        },
        "passed": {"type": "boolean"},
        "score_or_metric": {"type": "number"},
        "defects": {
            "type": "array",
            "items": {"type": "string"},
        },
        "drop_in_remediation": {"type": "string"},
    },
    "required": [
        "auditor_role",
        "gates_evaluated",
        "passed",
        "score_or_metric",
        "defects",
        "drop_in_remediation",
    ],
}


# ==============================================================================
# 2. WAVE 1: PARALLEL 3-WAY RECONNAISSANCE SWARM
# ==============================================================================

async def run_wave1_recon_swarm(objective_text: str):
    phase("Wave 1: Parallel 360-Degree Reconnaissance Swarm")
    log(f"Spawning 3 parallel read-only reconnaissance subagents for objective: {objective_text}")

    recon_tasks = [
        {
            "role": "Recon-Codebase-AST",
            "type_name": "research",
            "model": "flash",
            "prompt": f"""You are Subagent 1A (`Recon-Codebase-AST`).
Perform fast, read-only AST & codebase reconnaissance for the following objective:
{objective_text}

1. Map existing directory structure, shared interfaces, data models, and error classes.
2. Identify 2-3 canonical code exemplars and pinned dependency versions.
3. Discover exact working lint, typecheck, and unit test commands.
Return structured findings matching the required schema.""",
        },
        {
            "role": "Recon-RTM-And-Corner-Cases",
            "type_name": "research",
            "model": "flash",
            "prompt": f"""You are Subagent 1B (`Recon-RTM-And-Corner-Cases`).
Deconstruct requirements and edge cases for the following objective:
{objective_text}

1. Extract atomic Functional Requirements (`REQ-001..N`) and Acceptance Criteria (`AC-001..M`).
2. Plan a >=90% 4-Pillar RTM scenario matrix (40% Happy, 30% Alternate, 20% Error, 10% E2E).
3. Interrogate all 10 Corner-Case Dimensions (Numeric, Float, String/Encoding, Collections, Nullability, Concurrency/TOCTOU, State Machine, Resources, Network, Injection).
Return structured findings matching the required schema.""",
        },
        {
            "role": "Recon-AppSec-STRIDE",
            "type_name": "research",
            "model": "inherit",
            "prompt": f"""You are Subagent 1C (`Recon-AppSec-STRIDE`).
Perform offensive STRIDE threat modeling and source-to-sink taint mapping for:
{objective_text}

1. Identify all untrusted input sources, trust boundaries, and authorization checks (BOLA/IDOR).
2. Map dangerous sinks (SQL/NoSQL, shell execution, filesystem paths, SSRF, deserialization, crypto, LLM prompts).
3. Specify mandatory security controls and negative security regression test cases.
Return structured findings matching the required schema.""",
        },
    ]

    recon_results = await parallel(
        recon_tasks,
        lambda t: agent(
            t["prompt"],
            schema=RECON_REPORT_SCHEMA,
            role=t["role"],
            type_name=t["type_name"],
            workspace="inherit",
            model=t["model"],
        ),
    )
    log("Wave 1 Reconnaissance Swarm completed all 3 reports.")
    return recon_results


# ==============================================================================
# 3. WAVE 3, 4 & 5: WORK PACKET EXECUTION + PARALLEL 3-AUDITOR COUNCIL LOOP
# ==============================================================================

async def execute_and_audit_packet(wp: dict, recon_context=None):
    wp_id = wp["id"]
    role = wp.get("role", f"{wp_id}: Implementation Worker")
    initial_model = wp.get("model", "inherit")
    active_model = initial_model
    fallback_model = wp.get("fallback_model", DEFAULT_FALLBACK_MODEL)
    best_of_n = int(wp.get("best_of_n", wp.get("use_best_of", DEFAULT_USE_BEST_OF)))
    ws = wp.get("workspace", DEFAULT_WORKSPACE)
    allowed_files = wp.get("allowed_files", [])
    spec = wp["spec"]
    verify_cmd = wp.get("verification_command", "")

    worker = agent(role=role, workspace=ws, model=active_model)

    recon_banner = ""
    if recon_context:
        recon_banner = f"\n\n### Wave 1 Reconnaissance Context:\n{recon_context}\n"

    current_prompt = f"""{spec}{recon_banner}

### Strict Execution Rules (Bottom-Bun Reminder):
- You may ONLY create or modify files in this whitelist: {allowed_files}
- Zero unfinished markers, zero placeholder stubs, zero suppressed type/linter warnings.
- Run the verification command `{verify_cmd}` before finishing and report the exact output.
"""

    for attempt in range(1, MAX_RETRIES + 1):
        log(f"[{wp_id}] Wave 3: Running worker turn (Attempt {attempt}/{MAX_RETRIES}, model={active_model})...")
        if attempt == 1 and best_of_n > 1 and best_of is not None:
            log(f"[{wp_id}] Running high-risk best_of(n={best_of_n}) candidate tournament...")
            judge_prompt = (
                f"Select the candidate implementation for {wp_id} that strictly obeys allowed_files={allowed_files}, "
                f"passes `{verify_cmd}`, covers all RTM & 10D corner cases, and has zero anti-slop defects."
            )
            worker_report = await best_of(best_of_n, current_prompt, WORKER_REPORT_SCHEMA, judge_prompt)
        else:
            worker_report = await worker(current_prompt, schema=WORKER_REPORT_SCHEMA)

        log(f"[{wp_id}] Wave 4: Spawning Parallel 3-Auditor Council (Attempt {attempt}/{MAX_RETRIES})...")

        auditor_configs = [
            {
                "role": f"Auditor 4A: Scope, RTM & Corner Cases ({wp_id} #{attempt})",
                "model": "inherit",
                "workspace": ws,
                "schema": COUNCIL_AUDITOR_SCHEMA,
                "prompt": f"""You are **Auditor A (`Scope, RTM & Corner-Case Execution Auditor`)** for Work Packet `{wp_id}` (Attempt {attempt}/{MAX_RETRIES}).

### Allowed File Whitelist:
{allowed_files}

### Required Verification Command:
{verify_cmd}

### Original Work Packet Specification:
{spec}

### Worker Self-Report (UNTRUSTED - VERIFY INDEPENDENTLY):
{worker_report}

### Audit Instructions (Gates 1, 3, and 4):
1. **Gate 1 (Scope & Boundary Isolation)**: Verify that ONLY files in `{allowed_files}` were created or modified and all required files exist.
2. **Gate 3 (Broad-Spectrum RTM >= 90%)**: Verify that functional requirements and 4-Pillar scenarios in the spec are covered by real assertions.
3. **Gate 4 (10D Corner Cases & Anti-Cheat Integrity)**: Run `{verify_cmd}` yourself. Confirm 100% test pass rate, verify boundary/corner cases are tested, and confirm zero test tampering or weakened assertions.

Set `passed = true` ONLY if Gates 1, 3, and 4 all pass with zero defects. Set `score_or_metric` to the measured RTM coverage percentage (0-100).""",
            },
            {
                "role": f"Auditor 4B: Staff Code Reviewer ({wp_id} #{attempt})",
                "model": "inherit",
                "workspace": ws,
                "schema": COUNCIL_AUDITOR_SCHEMA,
                "prompt": f"""You are **Auditor B (`Staff Code Reviewer`)** for Work Packet `{wp_id}` (Attempt {attempt}/{MAX_RETRIES}).

### Allowed File Whitelist:
{allowed_files}

### Original Work Packet Specification:
{spec}

### Worker Self-Report (UNTRUSTED - VERIFY INDEPENDENTLY):
{worker_report}

### Audit Instructions (Gates 2 and 5):
1. **Gate 2 (Spec Compliance & Anti-Slop)**: Read every file in `{allowed_files}`. Verify 100% contract fidelity and zero anti-slop markers (no unfinished markers, placeholder stubs, empty catch blocks, loose type bypasses, or linter/type suppressions).
2. **Gate 5 (Staff Code Quality & 8-Dimension Scorecard)**: Evaluate Architecture (15%), Correctness (20%), Security (20%), Concurrency/TOCTOU safety (15%), Performance (10%), Reliability/Resource cleanup (10%), Testing (5%), and Maintainability (5%).

Set `passed = true` ONLY if Gate 2 and Gate 5 pass with Score >= 75.0/100 and 0 Blockers / 0 Majors. Set `score_or_metric` to the 8-Dimension score (0-100) and provide drop-in replacement code for any defect.""",
            },
            {
                "role": f"Auditor 4C: Principal AppSec Reviewer ({wp_id} #{attempt})",
                "model": "inherit",
                "workspace": ws,
                "schema": COUNCIL_AUDITOR_SCHEMA,
                "prompt": f"""You are **Auditor C (`Principal AppSec Reviewer`)** for Work Packet `{wp_id}` (Attempt {attempt}/{MAX_RETRIES}).

### Allowed File Whitelist:
{allowed_files}

### Original Work Packet Specification:
{spec}

### Worker Self-Report (UNTRUSTED - VERIFY INDEPENDENTLY):
{worker_report}

### Audit Instructions (Gate 6):
1. **Gate 6 (STRIDE, Taint Sinks, OWASP Top 10 & CVSS < 7.0)**: Inspect all files in `{allowed_files}` for hardcoded secrets (`CWE-798`), command/code injection (`CWE-78`/`CWE-95`), SQL/NoSQL injection (`CWE-89`), path traversal (`CWE-22`), SSRF (`CWE-918`), XSS (`CWE-79`), insecure deserialization (`CWE-502`), weak cryptography (`CWE-328`/`CWE-338`), and BOLA/IDOR flaws.
2. Score any discovered vulnerability using CVSS v3.1.

Set `passed = true` ONLY if there are 0 Critical/High vulnerabilities (max CVSS < 7.0) and 0 unmitigated Medium flaws. Set `score_or_metric` to the maximum CVSS score found (0.0 if clean) and provide drop-in hardened remediation code for any finding.""",
            },
        ]

        auditor_reports = await parallel(
            auditor_configs,
            lambda cfg: agent(
                cfg["prompt"],
                schema=cfg["schema"],
                role=cfg["role"],
                workspace=cfg["workspace"],
                model=cfg["model"],
            ),
        )

        auditor_a, auditor_b, auditor_c = auditor_reports
        all_gates_passed = (
            bool(auditor_a.get("passed"))
            and bool(auditor_b.get("passed"))
            and bool(auditor_c.get("passed"))
        )

        if all_gates_passed:
            log(
                f"[{wp_id}] APPROVED by all 3 Council Auditors on Attempt {attempt}! "
                f"(RTM: {auditor_a.get('score_or_metric')}%, "
                f"Review Score: {auditor_b.get('score_or_metric')}/100, "
                f"Max CVSS: {auditor_c.get('score_or_metric')})"
            )
            del worker
            return {
                "id": wp_id,
                "status": "APPROVED",
                "attempts": attempt,
                "worker_report": worker_report,
                "council_audit": {
                    "gates_1_3_4_execution_rtm_corner": auditor_a,
                    "gates_2_5_staff_code_review": auditor_b,
                    "gate_6_principal_appsec": auditor_c,
                },
            }

        combined_defects = []
        drop_in_replacements = []
        for rep in (auditor_a, auditor_b, auditor_c):
            role_label = rep.get("auditor_role", "Auditor")
            for d in rep.get("defects", []):
                combined_defects.append(f"[{role_label}] {d}")
            if rep.get("drop_in_remediation"):
                drop_in_replacements.append(f"#### {role_label} Drop-In Replacement:\n{rep['drop_in_remediation']}")

        log(f"[{wp_id}] Wave 4 Council REJECTED Attempt {attempt} ({len(combined_defects)} total defects). Entering Wave 5 Self-Healing...")
        for defect in combined_defects:
            log(f"  - [{wp_id}] {defect}")

        # Fast Model Promotion on Attempt 2 Failure for weak/small-capacity models
        escalated_spec_prefix = ""
        if attempt == 2 and attempt < MAX_RETRIES and initial_model in ("flash_lite", "flash"):
            log(
                f"[{wp_id}] Fast Model Promotion: Lower-tier worker (model={active_model}) failed 2 consecutive attempts. "
                f"Respawning escalated worker with model='{fallback_model}' for final attempt!"
            )
            del worker
            active_model = fallback_model
            worker = agent(role=f"{role} (Escalated-{fallback_model})", workspace=ws, model=active_model)
            escalated_spec_prefix = f"## Original Work Packet Specification:\n{spec}\n\n"

        current_prompt = f"""# WAVE 5 SURGICAL CORRECTION DIRECTIVE: {wp_id} (Attempt {attempt}/{MAX_RETRIES})
## 6-Gate Council Verdict: CHANGES REQUIRED

{escalated_spec_prefix}- **Auditor A (Gates 1, 3, 4 - Scope, RTM & Corner Cases)**: {'PASS' if auditor_a.get('passed') else 'FAIL'} (Metric: {auditor_a.get('score_or_metric')})
- **Auditor B (Gates 2 & 5 - Anti-Slop & Staff Code Review)**: {'PASS' if auditor_b.get('passed') else 'FAIL'} (Score: {auditor_b.get('score_or_metric')}/100)
- **Auditor C (Gate 6 - Principal AppSec & CVSS < 7.0)**: {'PASS' if auditor_c.get('passed') else 'FAIL'} (Max CVSS: {auditor_c.get('score_or_metric')})

### Blocking Defects to Remediate Immediately:
{chr(10).join(f'{idx + 1}. {item}' for idx, item in enumerate(combined_defects))}

### Exact Mechanical Patch (Apply Directly with edit_file)
{chr(10).join(drop_in_replacements) if drop_in_replacements else 'Apply surgical fixes for the blocking defects listed above.'}

### Mandatory Red-Green-Refactor Self-Healing Instructions (Bottom-Bun Final Hard Rules):
1. Reproduce each defect or corner case with a deterministic test first (RED).
2. Apply the minimal surgical fix strictly within your allowed file whitelist `{allowed_files}` (GREEN).
3. Do NOT weaken, delete, or tamper with existing tests (Anti-Cheat & SHA-256 Lock enforced).
4. Re-run `{verify_cmd}` to confirm 100% green execution and zero regressions, then return your updated report.
"""

    del worker
    raise RuntimeError(
        f"Work Packet {wp_id} failed the 6-Gate Council Audit after {MAX_RETRIES} attempts (3-Strike Circuit Breaker triggered)."
    )


# ==============================================================================
# 4. MAIN WORKFLOW ORCHESTRATION ENTRYPOINT
# ==============================================================================

recon_summary = None
if OBJECTIVE and AUTO_RECON:
    recon_summary = await run_wave1_recon_swarm(OBJECTIVE)

if not WORK_PACKETS:
    log("No work_packets provided in Args. Pass Args={'work_packets': [...]} to execute Wave 3-5.")
    print({"recon_summary": recon_summary, "work_packet_results": []})
else:
    phase("Wave 3-5: Parallel Work Packet Execution, 6-Gate Council Audit & Self-Healing")
    packet_results = await parallel(
        WORK_PACKETS,
        lambda packet: execute_and_audit_packet(packet, recon_context=recon_summary),
    )

    phase("Wave 6: Holistic Integration & Council Sign-Off Summary")
    for res in packet_results:
        log(f"[{res['id']}] Final Status: {res['status']} (Completed in {res['attempts']} attempt(s))")

    print({
        "recon_summary": recon_summary,
        "work_packet_results": packet_results,
    })
