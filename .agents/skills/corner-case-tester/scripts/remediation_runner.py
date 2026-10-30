#!/usr/bin/env python3
"""Autonomous Red-Green Remediation Controller & Anti-Cheat Auditor.

Executes test commands, captures execution telemetry, parses pass/fail metrics,
enforces anti-cheat invariants (verifying zero test tampering via git diff),
and tracks remediation convergence across iterations.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from typing import List, Optional, Tuple


def run_cmd(cmd: str) -> Tuple[int, str, str, float]:
    start = time.time()
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate()
    duration = round(time.time() - start, 2)
    return proc.returncode, stdout, stderr, duration


def check_anti_cheat(test_dir: str) -> Tuple[bool, List[str]]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", test_dir],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            lines = [l.strip() for l in proc.stdout.strip().split("\n") if l.strip()]
            return False, lines
        return True, []
    except Exception:
        # Git not installed or not in a git repo
        return True, []


def main():
    parser = argparse.ArgumentParser(description="Autonomous Red-Green Remediation Runner")
    parser.add_argument("--test-command", required=True, help="Shell command to run target corner-case test")
    parser.add_argument("--baseline-command", help="Shell command to run existing regression test suite")
    parser.add_argument("--test-dir", default="tests", help="Directory where test suites reside")
    parser.add_argument("--iteration", type=int, default=1, help="Current iteration number")
    parser.add_argument("--max-iterations", type=int, default=5, help="Maximum allowed iterations")
    parser.add_argument("--report-out", help="Path to write markdown scorecard")
    parser.add_argument("--json-out", help="Path to write JSON telemetry")
    parser.add_argument("--enforce-anti-cheat", action="store_true", help="Fail if test files were edited")
    args = parser.parse_args()

    print("=" * 60)
    print(f" RED-GREEN REMEDIATION RUNNER (Iteration {args.iteration} / {args.max_iterations})")
    print("=" * 60)
    print(f"[CONFIG] Target Test Command: {args.test_command}")
    if args.baseline_command:
        print(f"[CONFIG] Baseline Command: {args.baseline_command}")

    # Step 1: Anti-Cheat check
    anti_cheat_passed = True
    tampered_files = []
    if args.enforce_anti_cheat:
        print(f"\n[STEP 1] Running Anti-Cheat Audit on {args.test_dir}...")
        anti_cheat_passed, tampered_files = check_anti_cheat(args.test_dir)
        if not anti_cheat_passed:
            print("[ALERT] ANTI-CHEAT VIOLATION DETECTED!")
            print(f"Test files modified in {args.test_dir}:")
            for f in tampered_files:
                print(f"  - {f}")
        else:
            print("[ANTI-CHEAT] Audit Passed: Zero test tampering detected.")

    # Step 2: Run target test
    print("\n[STEP 2] Executing Target Corner-Case Test Command...")
    exit_code, stdout, stderr, duration = run_cmd(args.test_command)
    print(f"Test Execution Completed in {duration} seconds. Exit Code: {exit_code}")
    if stdout.strip():
        print("\n--- Output ---")
        print(stdout.strip())
    if stderr.strip():
        print("\n--- Errors ---")
        print(stderr.strip())

    target_passed = (exit_code == 0)

    # Step 3: Run baseline if target passed
    baseline_passed = True
    baseline_duration = 0.0
    if target_passed and args.baseline_command:
        print("\n[STEP 3] Target test passed! Running Baseline Regression Suite...")
        b_exit, b_out, b_err, baseline_duration = run_cmd(args.baseline_command)
        if b_exit != 0:
            baseline_passed = False
            print(f"[REGRESSION DETECTED] Baseline suite failed (Exit Code: {b_exit})!")
        else:
            print(f"[REGRESSION PASSED] Baseline suite fully green in {baseline_duration}s.")

    overall_success = target_passed and baseline_passed and anti_cheat_passed

    print("\n" + "=" * 60)
    if overall_success:
        print(" VERDICT: ALL GREEN - REMEDIATION SUCCESSFUL")
    elif not anti_cheat_passed:
        print(" VERDICT: FAILED - ANTI-CHEAT VIOLATION")
    elif not target_passed:
        print(" VERDICT: RED - TARGET CORNER-CASE TESTS FAILING")
    else:
        print(" VERDICT: REGRESSION - BASELINE SUITE BROKEN")
    print("=" * 60)

    # Report writing
    verdict_text = "✅ **GREEN - ALL CRITERIA SATISFIED**" if overall_success else "❌ **FAILING - REMEDIATION REQUIRED**"
    anti_cheat_text = "✅ **PASSED (0 test modifications)**" if anti_cheat_passed else f"🚨 **VIOLATION ({len(tampered_files)} files altered)**"
    baseline_text = "N/A" if not args.baseline_command else ("✅ **PASSED**" if baseline_passed else "❌ **REGRESSION DETECTED**")

    md = f"""# Remediation Execution Scorecard: Iteration {args.iteration} / {args.max_iterations}

**Timestamp**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Verdict**: {verdict_text}  
**Target Test Duration**: {duration} s | **Exit Code**: {exit_code}  
**Anti-Cheat Status**: {anti_cheat_text}  
**Baseline Regression**: {baseline_text}  

---

## Command Telemetry

- **Target Command**: `{args.test_command}`
- **Target Exit Code**: {exit_code}
- **Baseline Command**: `{args.baseline_command or 'None'}`

## Execution Details

```text
{stdout.strip()}
{('ERRORS:' + chr(10) + stderr.strip()) if stderr.strip() else ''}
```

---
*Generated by Corner-Case Tester Remediation Controller.*
"""

    if args.report_out:
        with open(args.report_out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[REPORT] Scorecard saved to: {args.report_out}")

    if args.json_out:
        res = {
            "iteration": args.iteration,
            "max_iterations": args.max_iterations,
            "overall_success": overall_success,
            "target_passed": target_passed,
            "baseline_passed": baseline_passed,
            "anti_cheat_passed": anti_cheat_passed,
            "exit_code": exit_code,
            "duration_seconds": duration,
            "tampered_files": tampered_files,
        }
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"[JSON] Telemetry saved to: {args.json_out}")

    if overall_success:
        return 0
    elif not anti_cheat_passed:
        return 2
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
