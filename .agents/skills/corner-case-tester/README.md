# Corner-Case Tester & Self-Healing Test Architect

An elite agent skill that operates with an adversarial, zero-assumption mindset to systematically uncover hidden corner cases, boundary traps, race conditions, and failure modes from requirements or code. It plans and executes deterministic test scenarios, generates high-level executive triage reports for leadership, and autonomously modifies code or contents in an automated **Red-Green-Refactor remediation loop** until 100% of the corner-case scenarios pass with zero regressions.

---

## Key Capabilities

- **360° Corner-Case Discovery**: Systematically analyzes requirements across **10 distinct dimensions**: numeric boundaries, strings & encodings, collections, nullability, concurrency races, state machines, resource limits, network/distributed timeouts, business logic invariants, and security injections.
- **Adversarial Scenario Planning**: Formulates deterministic Given-When-Then specifications using Boundary Value Analysis (BVA), Equivalence Partitioning, Property-Based Fuzzing, and Concurrency Barriers.
- **Dual-Audience Communication**: Delivers high-level Executive Triage Reports with risk heatmaps, pass/fail ratios, and business exposure summaries for engineering directors, while maintaining byte-precise technical diagnostics for code.
- **Autonomous Self-Healing Loop**: Diagnoses root causes from failing test assertion traces and iteratively modifies application code in a surgical Red-to-Green cycle until all tests pass.
- **Anti-Cheat & Mutation Guardrails**: Enforces strict invariants that prevent the agent from cheating (banning test tampering, assertion weakening, mock poisoning, and regression ignorance), verified via git diff audits and mutation testing.

---

## Directory Structure

```
corner-case-tester/
├── SKILL.md                                 # Core operating doctrine, 5-phase lifecycle & decision trees
├── README.md                                # Skill overview & quick-start guide
├── references/
│   ├── corner-case-taxonomy.md              # Exhaustive guide across the 10 failure dimensions
│   ├── scenario-planning-playbook.md        # Methodologies for BVA, Equivalence Partitioning & Concurrency
│   ├── self-healing-remediation-loop.md     # Protocol for surgical Red-to-Green code modification
│   ├── high-level-reporting-framework.md    # Executive presentation standards and risk scorecards
│   └── anti-cheat-and-mutation-rules.md     # Invariant rules banning test tampering and weak assertions
├── templates/
│   ├── corner-case-matrix.md                # Markdown matrix mapping requirements to edge conditions
│   ├── test-scenario-plan.md                # Detailed scenario specification template
│   ├── executive-triage-report.md           # High-level executive dashboard template
│   ├── test-execution-scorecard.md          # Granular technical test execution scorecard
│   └── remediation-changelog.md             # Code modification and regression audit log
├── scripts/
│   ├── corner_case_generator.ps1            # PowerShell: Automated corner-case matrix generator
│   ├── corner_case_generator.py             # Python: Automated corner-case matrix generator
│   ├── remediation_runner.ps1               # PowerShell: Autonomous Red-Green test runner & anti-cheat auditor
│   └── remediation_runner.py                # Python: Autonomous Red-Green test runner & anti-cheat auditor
└── examples/
    ├── full-corner-case-lifecycle-walkthrough.md  # Complete end-to-end e-commerce discount walkthrough
    ├── sample-corner-case-matrix.md               # Concrete completed corner-case matrix
    ├── sample-test-scenario-plan.md               # Concrete executable test scenario plan
    └── sample-executive-report.md                 # Realistic executive triage briefing
```

---

## The 5-Phase Adversarial Lifecycle

```
[Phase 1: 360° Requirement & Corner-Case Deconstruction]
                         │
                         ▼
[Phase 2: Adversarial Scenario Architecture & Test Synthesis]
                         │
                         ▼
[Phase 3: Test Execution & High-Level Executive Triage Reporting]
                         │
                         ▼
[Phase 4: Autonomous Red-to-Green Remediation Loop (Iterative)]
         ▲               │
         └── (Fail) ─────┤ (All Green)
                         ▼
[Phase 5: Anti-Cheat, Mutation & Regression Verification]
```

---

## Tooling & Command-Line Usage

### 1. Generating a Corner-Case Matrix
Inspect specifications or source code to automatically synthesize a 10-dimension corner-case matrix:

```powershell
# PowerShell
pwsh .agents/skills/corner-case-tester/scripts/corner_case_generator.ps1 -SpecFile docs/spec.md -Component "PaymentGateway"

# Python
python .agents/skills/corner-case-tester/scripts/corner_case_generator.py --spec-file docs/spec.md --component "PaymentGateway" --markdown-out matrix.md
```

### 2. Running the Autonomous Red-Green Remediation Controller
Execute corner-case tests with automated anti-cheat git auditing and regression verification:

```powershell
# PowerShell
pwsh .agents/skills/corner-case-tester/scripts/remediation_runner.ps1 `
    -TestCommand "pytest tests/adversarial" `
    -BaselineCommand "pytest tests/unit" `
    -TestDir "tests" `
    -Iteration 1 `
    -MaxIterations 5 `
    -EnforceAntiCheat

# Python
python .agents/skills/corner-case-tester/scripts/remediation_runner.py \
    --test-command "pytest tests/adversarial" \
    --baseline-command "pytest tests/unit" \
    --test-dir "tests" \
    --iteration 1 \
    --max-iterations 5 \
    --enforce-anti-cheat
```
