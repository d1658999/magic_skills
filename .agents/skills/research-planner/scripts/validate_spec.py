#!/usr/bin/env python3
"""Zero-Inference Spec & Task Packet Validator.

Audits specifications and task packets for zero-inference completeness,
detects slop/vague phrasing, and audits modified source files for placeholders.

Usage:
  # Validate a task packet or spec markdown file:
  python validate_spec.py --mode spec --file path/to/task-01.md

  # Audit modified code files for anti-slop markers & git boundaries:
  python validate_spec.py --mode audit --allowed-files src/auth/token.ts
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Mandatory sections for an Atomic Task Packet
TASK_PACKET_MANDATORY_SECTIONS = [
    ("Objective", r"(?i)(single-sentence\s+objective|mission|task\s+objective)"),
    ("File Whitelist", r"(?i)(file\s+access\s+boundaries|permitted\s+write\s+targets|allowed\s+to\s+create|allowed\s+files)"),
    ("Forbidden Files", r"(?i)(strictly\s+forbidden|do\s+not\s+touch|out\s+of\s+scope)"),
    ("Step-by-Step Recipe", r"(?i)(step-by-step\s+implementation\s+recipe|implementation\s+steps|procedural\s+steps)"),
    ("Anti-Slop / Prohibited Patterns", r"(?i)(prohibited\s+patterns|anti-slop|forbidden\s+constructs)"),
    ("Verification Command", r"(?i)(deterministic\s+verification\s+command|verification\s+command|acceptance\s+criteria)"),
]

# Mandatory sections for a Master Technical Spec
MASTER_SPEC_MANDATORY_SECTIONS = [
    ("Architecture & File Manifest", r"(?i)(architecture|module\s+directory|file\s+manifest)"),
    ("Frozen Data Contracts / Types", r"(?i)(frozen\s+data\s+contracts|interfaces|domain\s+models)"),
    ("Algorithmic Flow / State Machine", r"(?i)(state\s+machine|state\s+transition|algorithmic)"),
    ("Error & Edge Case Matrix", r"(?i)(error\s+(&|and)\s+edge\s+case|error\s+matrix|failure\s+modes)"),
    ("Verification & Test Plan", r"(?i)(verification\s+(&|and)\s+test|acceptance\s+criteria|test\s+plan)"),
]

# Vague phrasing that triggers hallucinations in low-tier models
VAGUE_PHRASING_PATTERNS = [
    (r"(?i)\bhandle\s+(it|errors?|exceptions?)\s+gracefully\b", "Vague error handling: 'handle errors gracefully'. Specify exact error classes and fallback status codes."),
    (r"(?i)\bas\s+appropriate\b", "Subjective phrasing: 'as appropriate'. Explicitly state the exact condition or logic."),
    (r"(?i)\bas\s+needed\b", "Subjective phrasing: 'as needed'. Define exact requirements."),
    (r"(?i)\bas\s+you\s+see\s+fit\b", "Ambiguous choice: 'as you see fit'. Low-tier models cannot make design choices."),
    (r"(?i)\breasonable\s+(timeout|defaults?|values?)\b", "Vague threshold: 'reasonable timeout/default'. Provide exact milliseconds or numbers."),
    (r"(?i)\bimplement\s+appropriately\b", "Vague directive: 'implement appropriately'. Provide step-by-step procedural recipe."),
    (r"(?i)\betc\.?\b", "Incomplete enumeration: 'etc.'. Low-tier models will miss unlisted items. List all cases explicitly."),
    (r"(?i)\bTODO\b", "Placeholder marker: 'TODO' found in specification."),
]

# Anti-slop markers in modified source code
ANTI_SLOP_CODE_PATTERNS = [
    ("TODO comment", re.compile(r"\bTODO\b", re.IGNORECASE)),
    ("FIXME comment", re.compile(r"\bFIXME\b", re.IGNORECASE)),
    ("HACK / XXX marker", re.compile(r"\b(HACK|XXX)\b")),
    ("TypeScript type suppression (@ts-ignore)", re.compile(r"@ts-(ignore|expect-error)")),
    ("TypeScript 'as any' bypass", re.compile(r"\bas\s+any\b")),
    ("Python type suppression (# type: ignore)", re.compile(r"#\s*type:\s*ignore")),
    ("Python linter suppression (# noqa)", re.compile(r"#\s*noqa")),
    ("Unimplemented stub (pass / NotImplementedError)", re.compile(r"\b(NotImplementedError|unimplemented!|todo!)\b")),
]


def validate_spec_document(file_path: Path) -> Tuple[bool, List[str], List[str]]:
    if not file_path.is_file():
        return False, [f"File not found: {file_path}"], []

    content = file_path.read_text(encoding="utf-8", errors="replace")
    errors: List[str] = []
    warnings: List[str] = []

    # Detect document type based on header
    is_task_packet = bool(re.search(r"(?im)^#.*task\s+packet", content) or re.search(r"(?im)^##\s+task\s+metadata", content))
    sections_to_check = TASK_PACKET_MANDATORY_SECTIONS if is_task_packet else MASTER_SPEC_MANDATORY_SECTIONS
    doc_type = "Atomic Task Packet" if is_task_packet else "Master Technical Specification"

    # Check for mandatory sections
    for section_name, pattern in sections_to_check:
        if not re.search(pattern, content):
            errors.append(f"Missing mandatory section in {doc_type}: '{section_name}'")

    # Check for vague phrasing
    for pattern, explanation in VAGUE_PHRASING_PATTERNS:
        matches = list(re.finditer(pattern, content))
        if matches:
            line_numbers = [content.count("\n", 0, m.start()) + 1 for m in matches[:3]]
            warnings.append(f"Vague phrasing detected on lines {line_numbers}: {explanation}")

    # Check length
    lines = content.strip().splitlines()
    if len(lines) < 20:
        errors.append(f"Document is too brief ({len(lines)} lines). Zero-inference specs must include exact details.")

    # Check for verification shell block
    if not re.search(r"```(bash|sh|pwsh|powershell|cmd)", content):
        warnings.append("No executable shell command block detected in verification section.")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def audit_code_files(allowed_files: List[str]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    resolved_allowed = {Path(p).resolve() for p in allowed_files}

    # 1. Audit allowed files for anti-slop patterns
    for file_str in allowed_files:
        path = Path(file_str)
        if not path.is_file():
            errors.append(f"Expected modified file does not exist: {file_str}")
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            errors.append(f"Could not read {file_str}: {e}")
            continue

        for label, regex in ANTI_SLOP_CODE_PATTERNS:
            for idx, line in enumerate(content.splitlines(), start=1):
                if regex.search(line):
                    errors.append(f"Anti-slop violation in {file_str}:{idx} - [{label}]: {line.strip()}")

    # 2. Check git boundaries if git repo is present
    try:
        git_res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        for line in git_res.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            # Format: ' M path/to/file' or '?? path/to/file'
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                status_code, git_path = parts
                resolved_git_path = Path(git_path).resolve()
                if resolved_git_path not in resolved_allowed:
                    # Ignore git untracked temp files or test scripts
                    if not git_path.startswith(".agents/") and not git_path.endswith(".tmp"):
                        errors.append(f"Scope breach: Out-of-scope file modified in git: '{git_path}' (status: {status_code})")
    except Exception:
        # Git not installed or not in repo - skip git scope check
        pass

    return len(errors) == 0, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Zero-Inference Spec & Task Packet Validator")
    parser.add_argument("--mode", choices=["spec", "audit"], required=True, help="Validation mode: 'spec' or 'audit'")
    parser.add_argument("--file", type=str, help="Path to specification/task packet markdown file (for --mode spec)")
    parser.add_argument("--allowed-files", nargs="*", default=[], help="Allowed file paths for code audit (for --mode audit)")

    args = parser.parse_args()

    print("================================================================================")
    print("Zero-Inference Spec & Task Packet Validator")
    print("================================================================================")

    if args.mode == "spec":
        if not args.file:
            print("ERROR: --file argument is required for spec validation.")
            sys.exit(1)
        spec_path = Path(args.file)
        print(f"Auditing Spec Document: {spec_path}\n")
        is_valid, errors, warnings = validate_spec_document(spec_path)

        if warnings:
            print("⚠️  SPECIFICATION WARNINGS (Vague Phrasing / Optimization Opportunities):")
            for w in warnings:
                print(f"  - {w}")
            print()

        if not is_valid:
            print("❌ SPECIFICATION FAILED ZERO-INFERENCE AUDIT:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        else:
            print("✅ SPECIFICATION PASSED ZERO-INFERENCE AUDIT.")
            print("   Document meets high-standard requirements for execution by low-tier models.")
            sys.exit(0)

    elif args.mode == "audit":
        if not args.allowed_files:
            print("ERROR: At least one --allowed-files argument is required for audit mode.")
            sys.exit(1)
        print(f"Auditing Code Files for Anti-Slop & Scope: {args.allowed_files}\n")
        passed, errors = audit_code_files(args.allowed_files)

        if not passed:
            print("❌ CODE AUDIT FAILED:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        else:
            print("✅ CODE AUDIT PASSED: Zero anti-slop markers found and boundaries respected.")
            sys.exit(0)


if __name__ == "__main__":
    main()
