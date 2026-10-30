#!/usr/bin/env python3
"""High-Quality Code Review Diff & Hygiene Analyzer.

Analyzes unified git diffs or source files for:
- Security red flags (hardcoded secrets, dangerous execution sinks, injection vectors)
- Debug artifacts (console.log, print, debugger, pdb)
- Anti-slop & suppression markers (TODO, FIXME, @ts-ignore, # type: ignore)
- Test-to-code ratio calculation
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

# Regular expression definitions for security & hygiene scans
SECURITY_PATTERNS = [
    (
        "Hardcoded Secret / API Key",
        re.compile(
            r"""(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|bearer\s+[a-z0-9_\-\.]{20,}|['\"][A-Za-z0-9/+=]{40}['\"])"""
        ),
        "BLOCKER",
    ),
    (
        "Dangerous Code Execution (eval / exec)",
        re.compile(r"""\b(eval|exec)\s*\("""),
        "BLOCKER",
    ),
    (
        "Command Injection Risk (shell=True / os.system)",
        re.compile(r"""(subprocess\.(Popen|run|call)\s*\(.*shell\s*=\s*True|os\.system\s*\()"""),
        "BLOCKER",
    ),
    (
        "Raw SQL Concatenation Risk",
        re.compile(r"""(execute|raw_query|rawQuery)\s*\(\s*(f['\"]|['\"].*%\s*\(|['\"].*\+\s*\w+)"""),
        "BLOCKER",
    ),
    (
        "Unsafe React innerHTML Injection",
        re.compile(r"""dangerouslySetInnerHTML\s*="""),
        "MAJOR",
    ),
]

HYGIENE_PATTERNS = [
    (
        "Debug Print Leftover (console.log / print)",
        re.compile(r"""(^\s*console\.(log|debug|info)\s*\(|^\s*print\s*\(|fmt\.Println\()"""),
        "MINOR",
    ),
    (
        "Debugger / Breakpoint Leftover",
        re.compile(r"""\b(debugger;|pdb\.set_trace\(\)|breakpoint\(\)|binding\.pry)\b"""),
        "MAJOR",
    ),
    (
        "TypeScript Type Suppression (@ts-ignore / @ts-expect-error)",
        re.compile(r"""//\s*@ts-(ignore|expect-error)"""),
        "MINOR",
    ),
    (
        "Python Type/Lint Suppression (# type: ignore / # noqa)",
        re.compile(r"""#\s*(type:\s*ignore|noqa)"""),
        "MINOR",
    ),
    (
        "Unresolved Anti-Slop Marker (TODO / FIXME / XXX)",
        re.compile(r"""\b(TODO|FIXME|HACK|XXX)\b"""),
        "MINOR",
    ),
]


def is_test_file(filepath: str) -> bool:
    lower = filepath.lower()
    return bool(
        "test" in lower
        or "spec" in lower
        or "__tests__" in lower
        or lower.endswith("_test.go")
        or lower.endswith("_test.py")
        or lower.endswith(".test.ts")
        or lower.endswith(".spec.ts")
        or lower.endswith(".test.js")
    )


def analyze_diff(diff_content: str) -> Dict[str, Any]:
    lines = diff_content.splitlines()
    current_file = "unknown"
    is_deleted = False

    findings: List[Dict[str, Any]] = []
    file_stats: Dict[str, Dict[str, int]] = {}

    current_line_no = 0

    for line in lines:
        if line.startswith("diff --git"):
            parts = line.split(" ")
            if len(parts) >= 4:
                current_file = parts[3].lstrip("b/")
            else:
                current_file = "unknown"
            if current_file not in file_stats:
                file_stats[current_file] = {"added": 0, "deleted": 0}
            is_deleted = False
            continue

        if line.startswith("--- a/"):
            continue
        if line.startswith("+++ b/"):
            if line == "+++ /dev/null":
                is_deleted = True
            else:
                current_file = line[6:]
                if current_file not in file_stats:
                    file_stats[current_file] = {"added": 0, "deleted": 0}
            continue

        if line.startswith("@@"):
            # Parse line number e.g. @@ -1,4 +1,6 @@
            match = re.search(r"\+(\d+)", line)
            if match:
                current_line_no = int(match.group(1)) - 1
            continue

        if is_deleted:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            current_line_no += 1
            content = line[1:]
            if current_file in file_stats:
                file_stats[current_file]["added"] += 1

            # Check security patterns
            for name, pattern, severity in SECURITY_PATTERNS:
                if pattern.search(content):
                    findings.append({
                        "file": current_file,
                        "line": current_line_no,
                        "content": content.strip()[:100],
                        "rule": name,
                        "category": "SECURITY",
                        "severity": severity,
                    })

            # Check hygiene patterns
            for name, pattern, severity in HYGIENE_PATTERNS:
                if pattern.search(content):
                    findings.append({
                        "file": current_file,
                        "line": current_line_no,
                        "content": content.strip()[:100],
                        "rule": name,
                        "category": "HYGIENE",
                        "severity": severity,
                    })

        elif line.startswith("-") and not line.startswith("---"):
            if current_file in file_stats:
                file_stats[current_file]["deleted"] += 1
        elif not line.startswith("+"):
            current_line_no += 1

    prod_added = 0
    test_added = 0
    for fpath, stats in file_stats.items():
        if is_test_file(fpath):
            test_added += stats["added"]
        else:
            prod_added += stats["added"]

    test_ratio = round((test_added / prod_added), 2) if prod_added > 0 else 1.0

    return {
        "files_analyzed": len(file_stats),
        "total_lines_added": sum(s["added"] for s in file_stats.values()),
        "total_lines_deleted": sum(s["deleted"] for s in file_stats.values()),
        "production_lines_added": prod_added,
        "test_lines_added": test_added,
        "test_to_code_ratio": test_ratio,
        "findings": findings,
        "summary": {
            "blockers": sum(1 for f in findings if f["severity"] == "BLOCKER"),
            "majors": sum(1 for f in findings if f["severity"] == "MAJOR"),
            "minors": sum(1 for f in findings if f["severity"] == "MINOR"),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze git diff for code review hygiene & security.")
    parser.add_argument("--diff", type=str, help="Path to unified diff file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    if args.diff:
        path = Path(args.diff)
        if not path.is_file():
            print(f"Error: Diff file not found at {path}", file=sys.stderr)
            sys.exit(1)
        content = path.read_text(encoding="utf-8", errors="replace")
    else:
        # Read from stdin
        content = sys.stdin.read()

    results = analyze_diff(content)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print("==================================================")
    print(" 🛡️  CODE REVIEW DIFF HYGIENE & PRE-FLIGHT AUDIT")
    print("==================================================")
    print(f"Files Modified     : {results['files_analyzed']}")
    print(f"Lines Added        : {results['total_lines_added']} (+{results['production_lines_added']} prod, +{results['test_lines_added']} test)")
    print(f"Lines Deleted      : {results['total_lines_deleted']}")
    print(f"Test-to-Code Ratio : {results['test_to_code_ratio']} (Recommended: >= 0.50)")
    print("--------------------------------------------------")
    print(f"Findings: {results['summary']['blockers']} Blocker(s), {results['summary']['majors']} Major(s), {results['summary']['minors']} Minor(s)")
    print("==================================================")

    if results["findings"]:
        for f in results["findings"]:
            icon = "🚨" if f["severity"] == "BLOCKER" else ("⚠️" if f["severity"] == "MAJOR" else "🔍")
            print(f"{icon} [{f['severity']}] {f['file']}:{f['line']} - {f['rule']}")
            print(f"   Snippet: {f['content']}")
        print("==================================================")
    else:
        print("✅ No automated hygiene or security red flags detected.")


if __name__ == "__main__":
    main()
