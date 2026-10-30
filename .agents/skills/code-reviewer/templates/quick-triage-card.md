# Quick Code Review Triage Card

Use this compact card for rapid turnaround reviews, bot status reports, or fast feedback loops.

---

```markdown
## ⚡ Code Review Triage Card

- **Target**: `[PR #123 / Branch / Commit]`
- **Verdict**: `[ ✅ APPROVE | ⚠️ REQUEST_CHANGES | 💬 NEEDS_DISCUSSION ]`
- **Quality Score**: `[XX/100]`

### Summary of Findings
- **Blockers (P0)**: `[0]`
- **Major Issues (P1)**: `[0]`
- **Minor Suggestions (P2)**: `[0]`
- **Nits (P3)**: `[0]`

### Key Takeaways
1. `[Key positive observation or architectural note]`
2. `[Key required fix or verification step]`

### Pre-Flight Checks
- [x] Linting & Formatting
- [x] No Debug Artifacts (`console.log`, `print`)
- [x] Test Suite Passing
- [x] No Hardcoded Secrets
```
