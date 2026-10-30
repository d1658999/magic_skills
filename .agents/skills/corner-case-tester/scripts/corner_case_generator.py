#!/usr/bin/env python3
"""Adversarial Corner-Case Generator & Boundary Matrix Builder.

Systematically inspects requirements, specifications, or source code files,
interrogates the 10 corner-case dimensions, and produces an exhaustive Markdown
Corner-Case Matrix or JSON plan for test scenario architecture.
"""

import argparse
import datetime
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional

# 10 Dimensions of Corner Cases with heuristic rules
DIMENSION_RULES = [
    {
        "dimension": "Numeric Boundary",
        "category": "Boundary",
        "severity": "P0",
        "likelihood": 3,
        "pattern": r"(?i)\b(amount|price|balance|limit|offset|page|count|total|quantity|discount|fee|rate|tax)\b",
        "scenarios": [
            {"vector": "Zero boundary (0, 0.0, -0.0)", "expected": "Handled gracefully; zero division avoided", "sev": "P1"},
            {"vector": "Negative value (-1, -100.00)", "expected": "Explicit ValidationError raised; negative rejected", "sev": "P0"},
            {"vector": "Maximum integer boundary (2^31-1, 2^63-1)", "expected": "Handled without integer overflow or crash", "sev": "P1"},
            {"vector": "Off-by-one upper/lower boundary (N-1, N, N+1)", "expected": "Boundary properly enclosed; exact limits respected", "sev": "P1"},
        ],
    },
    {
        "dimension": "Floating-Point Precision",
        "category": "Precision",
        "severity": "P1",
        "likelihood": 3,
        "pattern": r"(?i)\b(float|decimal|price|currency|tax|rate|cent|percent|calculate)\b",
        "scenarios": [
            {"vector": "Micro-penny / fractional cent rounding (0.005)", "expected": "Exact deterministic rounding (e.g. ROUND_HALF_UP)", "sev": "P1"},
            {"vector": "Floating-point drift (0.1 + 0.2 != 0.3)", "expected": "Exact equality preserved using Decimal/integer cents", "sev": "P1"},
            {"vector": "Infinite / NaN values", "expected": "Rejected with explicit validation error", "sev": "P0"},
        ],
    },
    {
        "dimension": "String & Encodings",
        "category": "Strings",
        "severity": "P1",
        "likelihood": 3,
        "pattern": r"(?i)\b(string|text|name|code|title|description|email|username|token|url|password)\b",
        "scenarios": [
            {"vector": "Empty string '' and whitespace-only '   '", "expected": "Trimmed and validated; rejected if required", "sev": "P2"},
            {"vector": "Surrogate pairs / 4-byte astral emojis (👨‍👩‍👧‍👦, 🎁)", "expected": "Stored and retrieved without byte truncation or crash", "sev": "P2"},
            {"vector": "Multi-byte UTF-8 and RTL characters (ñ, 日本語, עברית)", "expected": "Normalized and handled with correct grapheme length", "sev": "P3"},
            {"vector": "Extreme string length (10,000+ chars)", "expected": "Rejected at boundary; ReDoS avoided", "sev": "P1"},
            {"vector": "Control characters (\0, \r\n, \t, escape codes)", "expected": "Sanitized or rejected; no terminal or log pollution", "sev": "P2"},
        ],
    },
    {
        "dimension": "Collections & Structures",
        "category": "Collections",
        "severity": "P1",
        "likelihood": 3,
        "pattern": r"(?i)\b(list|array|items|collection|records|entries|batch|elements|children)\b",
        "scenarios": [
            {"vector": "Empty collection [] or {}", "expected": "Handled cleanly without IndexOutOfBounds or NoSuchElement", "sev": "P1"},
            {"vector": "Single item collection [x]", "expected": "Iteration and delimiter joining succeed without formatting errors", "sev": "P2"},
            {"vector": "Duplicate elements [x, x, x]", "expected": "Deduplicated or handled according to business uniqueness rules", "sev": "P2"},
            {"vector": "Massive collection (100,000+ items)", "expected": "Memory consumption bounded; pagination enforced", "sev": "P1"},
        ],
    },
    {
        "dimension": "Nullability & Absence",
        "category": "Nulls",
        "severity": "P0",
        "likelihood": 3,
        "pattern": r"(?i)\b(optional|nullable|null|none|nil|undefined|default|fallback)\b",
        "scenarios": [
            {"vector": "Explicit null / None payload", "expected": "Default fallback applied or typed ValidationError raised", "sev": "P0"},
            {"vector": "Missing / omitted payload keys ({})", "expected": "Missing required fields detected; descriptive error returned", "sev": "P1"},
            {"vector": "Type coercion mismatch (string '123' passed for integer)", "expected": "Type-checked strictly; implicit coercion prevented", "sev": "P2"},
        ],
    },
    {
        "dimension": "Concurrency & Race Hazards",
        "category": "Concurrency",
        "severity": "P0",
        "likelihood": 2,
        "pattern": r"(?i)\b(async|thread|lock|concurrent|parallel|transaction|balance|redeem|checkout|voucher|queue|worker)\b",
        "scenarios": [
            {"vector": "Simultaneous double-submit / parallel execution (TOCTOU)", "expected": "Atomic lock/CAS ensures exactly one transaction succeeds", "sev": "P0"},
            {"vector": "Out-of-order event delivery / message jitter", "expected": "Sequence versions checked; stale writes rejected", "sev": "P1"},
            {"vector": "High-contention resource locking", "expected": "Zero deadlocks; lock acquisition timeout handled gracefully", "sev": "P0"},
        ],
    },
    {
        "dimension": "State Machine & Lifecycles",
        "category": "State",
        "severity": "P1",
        "likelihood": 2,
        "pattern": r"(?i)\b(status|state|lifecycle|transition|init|start|stop|close|cancel|refund|complete|pending)\b",
        "scenarios": [
            {"vector": "Illegal state transition (e.g. CANCELLED -> COMPLETED)", "expected": "Explicit IllegalStateTransitionError raised", "sev": "P1"},
            {"vector": "Premature invocation (method called before init)", "expected": "UninitializedStateError raised cleanly; no null pointer crash", "sev": "P1"},
            {"vector": "Double finalization (close() called twice)", "expected": "Strictly idempotent; no-op on subsequent calls", "sev": "P2"},
        ],
    },
    {
        "dimension": "Resource Limits & Starvation",
        "category": "Resources",
        "severity": "P1",
        "likelihood": 2,
        "pattern": r"(?i)\b(file|io|stream|socket|connection|pool|buffer|memory|disk|cache|upload)\b",
        "scenarios": [
            {"vector": "Unclosed resource / file descriptor on exception", "expected": "Resources cleaned in finally/defer; zero descriptor leak", "sev": "P1"},
            {"vector": "Payload size exceeding memory threshold", "expected": "Streamed processing or 413 Payload Too Large returned", "sev": "P1"},
        ],
    },
    {
        "dimension": "Distributed & Network",
        "category": "Network",
        "severity": "P1",
        "likelihood": 2,
        "pattern": r"(?i)\b(http|api|remote|fetch|request|timeout|retry|client|service|webhook)\b",
        "scenarios": [
            {"vector": "Upstream service timeout / connection drop", "expected": "Circuit breaker / retry policy triggers with bounded timeout", "sev": "P1"},
            {"vector": "Duplicate webhook / idempotency key replay", "expected": "Idempotency cache returns cached response without duplicate side effect", "sev": "P0"},
        ],
    },
    {
        "dimension": "Security & Injection",
        "category": "Security",
        "severity": "P0",
        "likelihood": 2,
        "pattern": r"(?i)\b(input|path|file|query|sql|command|param|header|auth|token|json)\b",
        "scenarios": [
            {"vector": "Path traversal sequences (../../etc/passwd, ..\\..\\win.ini)", "expected": "Path canonicalized; traversal rejected", "sev": "P0"},
            {"vector": "Injection metacharacters (' OR 1=1 --, $(whoami), <script>)", "expected": "Parameterized or escaped; treated as raw literals", "sev": "P0"},
            {"vector": "Prototype pollution / object injection (__proto__, constructor)", "expected": "Prototype keys stripped or isolated", "sev": "P0"},
        ],
    },
]


def main():
    parser = argparse.ArgumentParser(description="Adversarial Corner-Case Generator & Matrix Builder")
    parser.add_argument("--spec-file", help="Path to specification markdown or text file")
    parser.add_argument("--source-file", help="Path to source code file to analyze")
    parser.add_argument("--component", default="TargetComponent", help="Name of target component")
    parser.add_argument("--markdown-out", help="Path to output Markdown file")
    parser.add_argument("--json-out", help="Path to output JSON file")
    args = parser.parse_args()

    content = ""
    if args.spec_file and os.path.exists(args.spec_file):
        with open(args.spec_file, "r", encoding="utf-8") as f:
            content += f.read()
    if args.source_file and os.path.exists(args.source_file):
        with open(args.source_file, "r", encoding="utf-8") as f:
            content += "\n" + f.read()

    discovered_cases = []
    case_counter = 1

    for rule in DIMENSION_RULES:
        matched = False
        if content:
            if re.search(rule["pattern"], content):
                matched = True
        else:
            matched = True

        if matched:
            for scen in rule["scenarios"]:
                case_id = f"CC-{case_counter:03d}"
                case_counter += 1

                sev_score = 3 if scen["sev"] == "P0" else (2 if scen["sev"] == "P1" else 1)
                risk = sev_score * rule["likelihood"]

                discovered_cases.append({
                    "case_id": case_id,
                    "dimension": rule["dimension"],
                    "category": rule["category"],
                    "severity": scen["sev"],
                    "likelihood": rule["likelihood"],
                    "risk_score": risk,
                    "trigger_vector": scen["vector"],
                    "expected_invariant": scen["expected"],
                    "status": "PENDING_TEST",
                })

    discovered_cases.sort(key=lambda x: x["risk_score"], reverse=True)

    p0 = sum(1 for c in discovered_cases if c["severity"] == "P0")
    p1 = sum(1 for c in discovered_cases if c["severity"] == "P1")
    p2 = sum(1 for c in discovered_cases if c["severity"] == "P2")
    p3 = sum(1 for c in discovered_cases if c["severity"] == "P3")

    md_lines = [
        f"# Corner-Case Discovery Matrix: {args.component}",
        "",
        f"**Generated At**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Target Component**: `{args.component}`  ",
        f"**Total Cases Discovered**: {len(discovered_cases)} (P0: {p0}, P1: {p1}, P2: {p2}, P3: {p3})  ",
        "",
        "---",
        "",
        "## Exhaustive Corner-Case Register",
        "",
        "| Case ID | Dimension | Severity | Risk Score | Input Trigger Vector | Expected Invariant / Outcome | Test Status |",
        "| :--- | :--- | :---: | :---: | :--- | :--- | :---: |",
    ]

    for c in discovered_cases:
        md_lines.append(
            f"| `{c['case_id']}` | {c['dimension']} | {c['severity']} | {c['risk_score']} | {c['trigger_vector']} | {c['expected_invariant']} | `PENDING` |"
        )

    md_lines.extend(["", "---", "*Generated automatically by Corner-Case Tester Agent.*"])
    md_output = "\n".join(md_lines)

    if args.markdown_out:
        with open(args.markdown_out, "w", encoding="utf-8") as f:
            f.write(md_output)
        print(f"[SUCCESS] Markdown matrix written to: {args.markdown_out}")
    else:
        print("\n" + md_output + "\n")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(discovered_cases, f, indent=2)
        print(f"[SUCCESS] JSON matrix written to: {args.json_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
