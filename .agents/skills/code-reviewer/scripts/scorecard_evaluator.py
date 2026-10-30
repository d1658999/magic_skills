#!/usr/bin/env python3
"""Code Review Scorecard Evaluator.

Computes weighted quality scores and generates automated verdicts
(APPROVE, REQUEST_CHANGES, COMMENT) based on review findings and severity counts.
"""

import argparse
import json
import sys
from typing import Dict

CATEGORY_WEIGHTS: Dict[str, float] = {
    "architecture": 0.15,
    "correctness": 0.20,
    "security": 0.20,
    "concurrency": 0.15,
    "performance": 0.10,
    "reliability": 0.10,
    "testing": 0.05,
    "maintainability": 0.05,
}


def calculate_score(
    scores: Dict[str, int],
    blockers: int,
    majors: int,
    minors: int,
) -> Dict[str, any]:
    weighted_sum = 0.0
    category_results = {}

    for cat, weight in CATEGORY_WEIGHTS.items():
        val = scores.get(cat, 5)  # default 5 if not provided
        category_score = (val / 5.0) * (weight * 100)
        weighted_sum += category_score
        category_results[cat] = {
            "raw": val,
            "weight_pct": int(weight * 100),
            "points_earned": round(category_score, 1),
        }

    # Deduct penalties for defect counts
    penalty = (blockers * 40) + (majors * 15) + (minors * 2)
    final_score = max(0, min(100, round(weighted_sum - penalty, 1)))

    if blockers > 0:
        verdict = "REQUEST_CHANGES"
        reason = f"Contains {blockers} critical blocker(s) that must be resolved before merge."
    elif majors > 0:
        verdict = "REQUEST_CHANGES"
        reason = f"Contains {majors} major issue(s) that require fixes."
    elif final_score < 75.0:
        verdict = "REQUEST_CHANGES"
        reason = f"Overall quality score ({final_score}/100) falls below acceptance threshold (75/100)."
    elif minors > 5:
        verdict = "COMMENT / NEEDS_DISCUSSION"
        reason = f"High number of minor issues ({minors}); consider cleaning up before final sign-off."
    else:
        verdict = "APPROVE"
        reason = f"Meets high quality bar ({final_score}/100) with zero blockers or major issues."

    return {
        "final_score": final_score,
        "base_weighted_score": round(weighted_sum, 1),
        "penalty_points": penalty,
        "verdict": verdict,
        "reason": reason,
        "issue_counts": {
            "blockers": blockers,
            "majors": majors,
            "minors": minors,
        },
        "category_breakdown": category_results,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate code review quality scorecard.")
    parser.add_argument("--blockers", type=int, default=0, help="Count of P0 blocker issues")
    parser.add_argument("--majors", type=int, default=0, help="Count of P1 major issues")
    parser.add_argument("--minors", type=int, default=0, help="Count of P2 minor issues")
    parser.add_argument("--architecture", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--correctness", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--security", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--concurrency", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--performance", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--reliability", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--testing", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--maintainability", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    scores = {
        "architecture": args.architecture,
        "correctness": args.correctness,
        "security": args.security,
        "concurrency": args.concurrency,
        "performance": args.performance,
        "reliability": args.reliability,
        "testing": args.testing,
        "maintainability": args.maintainability,
    }

    result = calculate_score(scores, args.blockers, args.majors, args.minors)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("==================================================")
    print(" 📊 CODE REVIEW SCORECARD EVALUATION RESULT")
    print("==================================================")
    print(f"Overall Score  : {result['final_score']} / 100")
    print(f"Verdict        : {result['verdict']}")
    print(f"Reason         : {result['reason']}")
    print("--------------------------------------------------")
    print(f"Defect Counts  : {args.blockers} Blockers, {args.majors} Majors, {args.minors} Minors")
    print("--------------------------------------------------")
    print("Category Breakdown (Score / 5):")
    for cat, data in result["category_breakdown"].items():
        print(f" - {cat.capitalize():<16}: {data['raw']}/5 ({data['points_earned']} / {data['weight_pct']} pts)")
    print("==================================================")


if __name__ == "__main__":
    main()
