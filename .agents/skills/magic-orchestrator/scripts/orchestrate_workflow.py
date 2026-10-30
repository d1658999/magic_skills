"""Reusable Antigravity `run_workflow` script for Magic Orchestrator.

Executes parallel work packets with mandatory 6-Gate Council Review,
Anti-Cheat Invariant verification, and iterative reassignment loops.

Run via Antigravity `run_workflow`:
  run_workflow(
      ScriptPath="/abs/path/to/magic-orchestrator/scripts/orchestrate_workflow.py",
      Description="Execute magic orchestrator parallel work packets with 6-gate council review",
      Args={
          "max_retries": 3,
          "workspace": "inherit",
          "work_packets": [
              {
                  "id": "WP-1",
                  "role": "WP-1: Core Module",
                  "allowed_files": ["src/core.ts", "tests/core.test.ts"],
                  "spec": "<Full Zero-Assumption Work Packet Markdown>",
                  "verification_command": "npm test -- tests/core.test.ts"
              }
          ]
      }
  )
"""

from typing import Any, Dict, List

MAX_RETRIES = int(args.get("max_retries", 3)) if "args" in dir() and isinstance(args, dict) else 3
DEFAULT_WORKSPACE = args.get("workspace", "inherit") if "args" in dir() and isinstance(args, dict) else "inherit"
WORK_PACKETS = args.get("work_packets", []) if "args" in dir() and isinstance(args, dict) else []

COUNCIL_SCORECARD_SCHEMA = {
    "type": "object",
    "properties": {
        "gate1_boundary_isolation_pass": {"type": "boolean"},
        "gate2_spec_and_anti_slop_pass": {"type": "boolean"},
        "gate3_functional_rtm_pass": {"type": "boolean"},
        "gate4_corner_cases_pass": {"type": "boolean"},
        "gate5_staff_code_quality_pass": {"type": "boolean"},
        "gate6_appsec_stride_cvss_pass": {"type": "boolean"},
        "approved": {"type": "boolean"},
        "blockers": {"type": "array", "items": {"type": "string"}},
        "correction_directive": {"type": "string"},
    },
    "required": [
        "gate1_boundary_isolation_pass",
        "gate2_spec_and_anti_slop_pass",
        "gate3_functional_rtm_pass",
        "gate4_corner_cases_pass",
        "gate5_staff_code_quality_pass",
        "gate6_appsec_stride_cvss_pass",
        "approved",
    ],
}

print(f"[MAGIC ORCHESTRATOR] Initializing workflow with {len(WORK_PACKETS)} work packets. Max retries: {MAX_RETRIES}.")
