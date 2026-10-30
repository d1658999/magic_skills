#!/usr/bin/env python3
"""CVSS v3.1 Base Score Calculator & Vector Evaluator.

Accurately computes CVSS v3.1 base score, impact sub-score, exploitability sub-score,
and qualitative severity rating from a standard CVSS vector string or individual metrics.
"""

import argparse
import json
import math
import re
import sys
from typing import Any, Dict, Optional, Tuple

# Metric weight mappings
AV_WEIGHTS = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
AC_WEIGHTS = {"L": 0.77, "H": 0.44}
PR_WEIGHTS_UNCHANGED = {"N": 0.85, "L": 0.62, "H": 0.27}
PR_WEIGHTS_CHANGED = {"N": 0.85, "L": 0.68, "H": 0.50}
UI_WEIGHTS = {"N": 0.85, "R": 0.62}
CIA_WEIGHTS = {"H": 0.56, "L": 0.22, "N": 0.0}


def cvss_round_up(val: float) -> float:
    """Rounds up to 1 decimal place per CVSS v3.1 specification."""
    int_input = math.floor(val * 100000 + 0.5)
    if int_input % 10000 == 0:
        return int_input / 100000.0
    else:
        return (math.floor(int_input / 10000) + 1) / 10.0


def parse_vector(vector_str: str) -> Dict[str, str]:
    """Parses a CVSS:3.1 or CVSS:3.0 vector string."""
    vector_clean = vector_str.strip().strip("'\"")
    parts = vector_clean.split("/")
    metrics = {}
    for p in parts:
        if ":" in p:
            k, v = p.split(":", 1)
            metrics[k.upper()] = v.upper()
    return metrics


def calculate_cvss_v31(metrics: Dict[str, str]) -> Dict[str, Any]:
    required = ["AV", "AC", "PR", "UI", "S", "C", "I", "A"]
    missing = [m for m in required if m not in metrics]
    if missing:
        raise ValueError(f"Missing required CVSS metrics: {', '.join(missing)}")

    av = metrics["AV"]
    ac = metrics["AC"]
    pr = metrics["PR"]
    ui = metrics["UI"]
    s = metrics["S"]
    c = metrics["C"]
    i = metrics["I"]
    a = metrics["A"]

    if av not in AV_WEIGHTS: raise ValueError(f"Invalid AV: {av}")
    if ac not in AC_WEIGHTS: raise ValueError(f"Invalid AC: {ac}")
    if ui not in UI_WEIGHTS: raise ValueError(f"Invalid UI: {ui}")
    if s not in ["U", "C"]: raise ValueError(f"Invalid S: {s}")
    if c not in CIA_WEIGHTS: raise ValueError(f"Invalid C: {c}")
    if i not in CIA_WEIGHTS: raise ValueError(f"Invalid I: {i}")
    if a not in CIA_WEIGHTS: raise ValueError(f"Invalid A: {a}")

    scope_changed = (s == "C")
    pr_weight = PR_WEIGHTS_CHANGED[pr] if scope_changed else PR_WEIGHTS_UNCHANGED[pr]

    # ISS (Impact Sub Score)
    iss = 1.0 - ((1.0 - CIA_WEIGHTS[c]) * (1.0 - CIA_WEIGHTS[i]) * (1.0 - CIA_WEIGHTS[a]))

    # Impact calculation
    if not scope_changed:
        impact = 6.42 * iss
    else:
        impact = 7.52 * (iss - 0.029) - 3.25 * math.pow(iss - 0.02, 15)

    # Exploitability calculation
    exploitability = 8.22 * AV_WEIGHTS[av] * AC_WEIGHTS[ac] * pr_weight * UI_WEIGHTS[ui]

    # Base Score calculation
    if impact <= 0:
        base_score = 0.0
    else:
        if not scope_changed:
            base_score = cvss_round_up(min(impact + exploitability, 10.0))
        else:
            base_score = cvss_round_up(min(1.08 * (impact + exploitability), 10.0))

    # Severity Rating
    if base_score == 0.0:
        severity = "NONE"
    elif 0.1 <= base_score <= 3.9:
        severity = "LOW"
    elif 4.0 <= base_score <= 6.9:
        severity = "MEDIUM"
    elif 7.0 <= base_score <= 8.9:
        severity = "HIGH"
    else:
        severity = "CRITICAL"

    vector_canonical = f"CVSS:3.1/AV:{av}/AC:{ac}/PR:{pr}/UI:{ui}/S:{s}/C:{c}/I:{i}/A:{a}"

    return {
        "vector": vector_canonical,
        "base_score": base_score,
        "severity": severity,
        "impact_subscore": round(impact, 2),
        "exploitability_subscore": round(exploitability, 2),
        "metrics": metrics,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="CVSS v3.1 Calculator & Severity Evaluator")
    parser.add_argument("--vector", "-v", type=str, help="Full CVSS vector (e.g. CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)")
    parser.add_argument("--av", choices=["N", "A", "L", "P"], default="N", help="Attack Vector")
    parser.add_argument("--ac", choices=["L", "H"], default="L", help="Attack Complexity")
    parser.add_argument("--pr", choices=["N", "L", "H"], default="N", help="Privileges Required")
    parser.add_argument("--ui", choices=["N", "R"], default="N", help="User Interaction")
    parser.add_argument("--s", choices=["U", "C"], default="U", help="Scope (U=Unchanged, C=Changed)")
    parser.add_argument("--c", choices=["H", "L", "N"], default="H", help="Confidentiality Impact")
    parser.add_argument("--i", choices=["H", "L", "N"], default="H", help="Integrity Impact")
    parser.add_argument("--a", choices=["H", "L", "N"], default="H", help="Availability Impact")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if args.vector:
        metrics = parse_vector(args.vector)
    else:
        metrics = {
            "AV": args.av, "AC": args.ac, "PR": args.pr, "UI": args.ui,
            "S": args.s, "C": args.c, "I": args.i, "A": args.a
        }

    try:
        result = calculate_cvss_v31(metrics)
    except Exception as e:
        print(f"Error evaluating CVSS: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 60)
        print(" 🎯 CVSS v3.1 EVALUATION RESULT")
        print("=" * 60)
        print(f"  Vector String       : {result['vector']}")
        print(f"  Base Score          : {result['base_score']} / 10.0")
        print(f"  Qualitative Severity: {result['severity']}")
        print(f"  Impact Subscore     : {result['impact_subscore']}")
        print(f"  Exploitability      : {result['exploitability_subscore']}")
        print("=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
