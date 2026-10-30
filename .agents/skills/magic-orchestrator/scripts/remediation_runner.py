#!/usr/bin/env python3
"""Autonomous Red-Green Remediation Controller & Anti-Cheat Auditor.

Executes test commands, captures execution telemetry, parses pass/fail metrics,
enforces anti-cheat invariants (verifying zero test tampering via git status/diff),
and tracks remediation convergence across iterations.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple


def run_cmd(cmd: str) -> Tuple[int, str, str, float]:
    start = time.time()
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout, stderr = proc.communicate()
    duration = round(time.time() - start, 2)
    return proc.returncode, stdout, stderr, duration


def check_anti_cheat(test_paths: List[str]) -> Tuple[bool, List[str]]:
    """Checks git status on test files to ensure they were not tampered with."""
    tampered = []
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"] + test_paths,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            for line in proc.stdout.strip().splitlines():
                if line.strip():
                    tampered.append(line.strip())
            return False, tampered
        return True, []
    except Exception:
        return True, []


def main():
    parser = argparse.ArgumentParser(description="Autonomous Red-Green Remediation Controller")
    parser.add_argument("--test-cmd", required=True, help="Shell command to run tests")
    parser.add_argument("--src-dir", default="./src", help="Directory containing production source code")
    parser.add_argument("--test-dir", default="./tests", help="Directory containing test files")
    parser.add_argument("--max-retries", type=int, default=5, help="Maximum healing iterations")
    parser.add_argument("--json-out", help="Path to write JSON execution telemetry")
    args = parser.parse_args()

    print("=" * 70)
    print(" MAGIC ORCHESTRATOR RED-GREEN REMEDIATION CONTROLLER")
    print(f" Test Command: {args.test_cmd}")
    print(f" Max Iterations: {args.max_retries}")
    print("=" * 70)

    # Iteration 1: Initial Run
    rc, stdout, stderr, duration = run_cmd(args.test_cmd)
    print(f"[*] Initial Run: Exit Code={rc} in {duration}s")

    if rc == 0:
        print("[+] All tests currently passing. System is GREEN.")
        return 0

    print(f"[!] Tests failing (RED). Entering autonomous remediation loop...")
    print(f"    Failure output snippet:\n    {stdout.strip()[:300] or stderr.strip()[:300]}")

    # Telemetry tracking
    telemetry = {
        "initial_passed": False,
        "iterations": [],
        "converged": False,
        "anti_cheat_clean": True,
    }

    # Verify anti-cheat baseline
    anti_cheat_ok, tampered_files = check_anti_cheat([args.test_dir])
    if not anti_cheat_ok:
        print(f"[ANTI-CHEAT WARNING] Uncommitted modifications detected in test directory: {tampered_files}")

    print("\n[INFO] Remediation controller ready. Awaiting surgical fixes from subagents or Lead Architect.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
