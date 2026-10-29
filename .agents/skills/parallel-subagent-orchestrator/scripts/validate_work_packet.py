#!/usr/bin/env python3
"""Validation & Audit helper for the Parallel Subagent Orchestrator skill.

Provides two modes:
1. `spec`: Validates that a Work Packet markdown file contains all mandatory
   zero-assumption sections before spawning a subagent.
2. `audit`: Audits a completed subagent's target files for:
   - Forbidden anti-slop markers (TODO, FIXME, HACK, XXX, @ts-ignore, # type: ignore, etc.)
   - Missing expected files
   - Out-of-scope git modifications (when run inside a git repository)

Usage examples:
  python validate_work_packet.py --mode spec --spec-file path/to/wp1.md
  python validate_work_packet.py --mode audit --allowed-files src/a.ts tests/a.test.ts
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

REQUIRED_SPEC_SECTIONS = [
    ("Mission / Objective", r"(?i)(mission|objective|responsibility\s+scope)"),
    ("Allowed Files", r"(?i)(allowed\s+to\s+create|write-permitted\s+files|allowed\s+write\s+files)"),
    ("Forbidden / Out-of-Scope Files", r"(?i)(strictly\s+forbidden|out\s+of\s+scope|do\s+not\s+touch)"),
    ("Exact Interfaces / Signatures", r"(?i)(exact\s+interfaces|signatures|data\s+contracts)"),
    ("Step-by-Step Implementation", r"(?i)(step-by-step|implementation\s+blueprint)"),
    ("Edge-Case Matrix", r"(?i)(edge-case|edge\s+cases|error-handling\s+matrix)"),
    ("Unit Test Specification", r"(?i)(required\s+unit\s+tests|unit\s+test\s+specification)"),
    ("Verification Commands", r"(?i)(self-verification|verification\s+commands|completion\s+report)"),
]

ANTI_SLOP_PATTERNS = [
    ("TODO/FIXME/HACK/XXX comment", re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")),
    ("TypeScript type suppression (@ts-ignore / @ts-expect-error)", re.compile(r"@ts-(ignore|expect-error)")),
    ("TypeScript explicit 'as any'", re.compile(r"\bas\s+any\b")),
    ("Python type/lint suppression (# type: ignore / # noqa)", re.compile(r"#\s*(type:\s*ignore|noqa)")),
    ("Unimplemented stub (NotImplementedError / unimplemented!)", re.compile(r"\b(NotImplementedError|unimplemented!|todo!)\b")),
]


def validate_spec_file(spec_path: Path) -> Tuple[bool, List[str]]:
    if not spec_path.is_file():
        return False, [f"Spec file does not exist: {spec_path}"]

    content = spec_path.read_text(encoding="utf-8", errors="replace")
    errors: List[str] = []

    for section_name, pattern in REQUIRED_SPEC_SECTIONS:
        if not re.search(pattern, content):
            errors.append(f"Missing required spec section: '{section_name}'")

    if len(content.strip().splitlines()) < 25:
        errors.append(
            "Spec file is too short (< 25 lines). Zero-assumption specs must include "
            "detailed signatures, step-by-step logic, and edge cases."
        )

    return len(errors) == 0, errors


def check_git_scope(workspace: Path, allowed_files: List[str]) -> List[str]:
    """If workspace is a git repo, check if any modified/untracked files fall outside allowed_files."""
    errors: List[str] = []
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []

        allowed_resolved = {
            (workspace / Path(f)).resolve() for f in allowed_files
        }
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            rel_path_str = line[3:].strip().strip('"')
            if " -> " in rel_path_str:
                rel_path_str = rel_path_str.split(" -> ", 1)[1].strip('"')
            file_resolved = (workspace / Path(rel_path_str)).resolve()
            if file_resolved not in allowed_resolved:
                errors.append(
                    f"[Gate 1 Scope Warning] Modified/untracked file outside allowed list: {rel_path_str}"
                )
    except OSError:
        pass
    return errors


def audit_target_files(
    workspace: Path, allowed_files: List[str], check_git: bool = False
) -> Tuple[bool, List[str]]:
    findings: List[str] = []

    for rel_file in allowed_files:
        target = (workspace / Path(rel_file)).resolve()
        if not target.is_file():
            findings.append(f"[Gate 1 Missing Deliverable] Expected file does not exist: {rel_file}")
            continue

        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        if not lines:
            findings.append(f"[Gate 2 Empty File] File is completely empty: {rel_file}")
            continue

        for idx, line in enumerate(lines, start=1):
            for label, regex in ANTI_SLOP_PATTERNS:
                if regex.search(line):
                    findings.append(
                        f"[Gate 2 Anti-Slop Defect] {rel_file}:L{idx} ({label}): {line.strip()}"
                    )

    if check_git:
        findings.extend(check_git_scope(workspace, allowed_files))

    return len(findings) == 0, findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate subagent Work Packet specs or audit subagent deliverables."
    )
    parser.add_argument(
        "--mode",
        choices=["spec", "audit"],
        required=True,
        help="'spec' validates a Work Packet markdown file; 'audit' checks subagent output files.",
    )
    parser.add_argument(
        "--spec-file",
        type=str,
        help="Path to the Work Packet markdown file (required for --mode spec).",
    )
    parser.add_argument(
        "--allowed-files",
        nargs="+",
        help="List of allowed target files created/modified by the subagent (required for --mode audit).",
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: current directory).",
    )
    parser.add_argument(
        "--check-git-scope",
        action="store_true",
        help="Also check `git status --porcelain` for any modified files outside --allowed-files.",
    )

    args = parser.parse_args()
    workspace_path = Path(args.workspace).resolve()

    if args.mode == "spec":
        if not args.spec_file:
            print("ERROR: --spec-file is required when --mode is 'spec'.", file=sys.stderr)
            return 2
        passed, issues = validate_spec_file(Path(args.spec_file).resolve())
        if passed:
            print("SPEC VALIDATION PASSED: All mandatory zero-assumption sections are present.")
            return 0
        print("SPEC VALIDATION FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    if args.mode == "audit":
        if not args.allowed_files:
            print("ERROR: --allowed-files is required when --mode is 'audit'.", file=sys.stderr)
            return 2
        passed, findings = audit_target_files(
            workspace_path, args.allowed_files, check_git=args.check_git_scope
        )
        if passed:
            print(
                f"AUDIT SCAN PASSED: All {len(args.allowed_files)} file(s) exist and contain zero anti-slop markers."
            )
            return 0
        print("AUDIT SCAN FAILED (REASSIGNMENT REQUIRED):")
        for finding in findings:
            print(f"  - {finding}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
