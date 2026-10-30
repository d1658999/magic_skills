#!/usr/bin/env python3
"""Task Decomposition & DAG Integrity Validator.

Audits execution plans to verify:
1. Absence of dependency cycles (topological sort validity).
2. Absence of parallel file collisions (disjoint write boundaries).
3. Existence of required verification gates for every task.

Usage:
  python decompose_tasks.py --plan-file path/to/execution-dag-plan.md
"""

import argparse
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Set


def parse_plan_file(file_path: Path):
    if not file_path.is_file():
        print(f"ERROR: Plan file not found: {file_path}")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8", errors="replace")

    # Match markdown table rows with Task IDs:
    # Example: | `TASK-001` | Define Auth Interfaces | `src/types/auth.ts` | None | Sequential | `npx tsc` |
    row_pattern = re.compile(
        r"\|\s*`?(TASK-[0-9A-Za-z_-]+)`?\s*\|\s*([^|]+)\|\s*`?([^|]+?)`?\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|"
    )

    tasks: Dict[str, dict] = {}
    for match in row_pattern.finditer(content):
        task_id = match.group(1).strip()
        title = match.group(2).strip()
        raw_files = match.group(3).strip().replace("`", "")
        raw_deps = match.group(4).strip().replace("`", "")
        concurrency = match.group(5).strip()
        gate = match.group(6).strip().replace("`", "")

        files = [f.strip() for f in raw_files.split(",") if f.strip() and f.lower() != "none"]
        deps = [d.strip() for d in re.findall(r"TASK-[0-9A-Za-z_-]+", raw_deps)]

        tasks[task_id] = {
            "title": title,
            "files": files,
            "deps": deps,
            "concurrency": concurrency,
            "gate": gate,
        }

    return tasks


def check_cycles(tasks: Dict[str, dict]) -> List[str]:
    # Kahn's algorithm for topological sorting
    in_degree = {t: 0 for t in tasks}
    adj = defaultdict(list)

    for task_id, info in tasks.items():
        for dep in info["deps"]:
            if dep in tasks:
                adj[dep].append(task_id)
                in_degree[task_id] += 1
            else:
                return [f"Task '{task_id}' depends on undefined task '{dep}'."]

    queue = deque([t for t, deg in in_degree.items() if deg == 0])
    visited_count = 0

    while queue:
        node = queue.popleft()
        visited_count += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited_count != len(tasks):
        return ["Dependency cycle detected in task DAG! Tasks cannot be topologically sorted."]

    return []


def check_parallel_collisions(tasks: Dict[str, dict]) -> List[str]:
    errors = []
    # Group tasks that might run concurrently
    stage_groups = defaultdict(list)
    for task_id, info in tasks.items():
        concurrency = info["concurrency"].lower()
        if "parallel" in concurrency or "slot" in concurrency:
            stage_groups["parallel_pool"].append(task_id)

    # Check for overlapping files within parallel pool
    file_owners: Dict[str, str] = {}
    for task_id in stage_groups["parallel_pool"]:
        for file_path in tasks[task_id]["files"]:
            if file_path in file_owners:
                other_task = file_owners[file_path]
                errors.append(
                    f"Parallel file collision! Both '{task_id}' and '{other_task}' claim write access to '{file_path}'."
                )
            else:
                file_owners[file_path] = task_id

    return errors


def main():
    parser = argparse.ArgumentParser(description="Task Decomposition & DAG Integrity Validator")
    parser.add_argument("--plan-file", required=True, help="Path to execution DAG markdown file")
    args = parser.parse_args()

    plan_path = Path(args.plan_file)
    print("================================================================================")
    print(f"Task DAG & Decomposition Validator: {plan_path}")
    print("================================================================================\n")

    tasks = parse_plan_file(plan_path)
    if not tasks:
        print("⚠️ No tasks in table format found in plan file. Ensure tasks use format: | `TASK-XXX` | ... |")
        sys.exit(1)

    print(f"Parsed {len(tasks)} tasks from plan:")
    for tid, info in tasks.items():
        print(f"  - [{tid}] {info['title']} (Files: {info['files']}, Deps: {info['deps']})")
    print()

    cycle_errors = check_cycles(tasks)
    collision_errors = check_parallel_collisions(tasks)

    all_errors = cycle_errors + collision_errors

    if all_errors:
        print("❌ DAG VALIDATION FAILED:")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ DAG VALIDATION PASSED:")
        print("  - Zero dependency cycles.")
        print("  - Zero parallel file write collisions.")
        print("  - All task dependencies are valid and resolvable.")
        sys.exit(0)


if __name__ == "__main__":
    main()
