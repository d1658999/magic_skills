<#
.SYNOPSIS
    Adversarial Corner-Case Generator & Boundary Matrix Builder (PowerShell 7).
.DESCRIPTION
    Systematically inspects requirements, specifications, or source code files,
    interrogates the 10 corner-case dimensions, and produces an exhaustive Markdown
    Corner-Case Matrix or JSON plan for test scenario architecture.
.EXAMPLE
    pwsh corner_case_generator.ps1 -SpecFile docs/spec.md -Component "BillingEngine"
    pwsh corner_case_generator.ps1 -SourceFile src/discount.py -MarkdownOut matrix.md
#>

[CmdletBinding()]
param(
    [string]$SpecFile,
    [string]$SourceFile,
    [string]$Component = "TargetComponent",
    [string]$MarkdownOut,
    [string]$JsonOut
)

# 10 Dimensions of Corner Cases with heuristic rules
$DimensionRules = @(
    @{
        Dimension = "Numeric Boundary"
        Category = "Boundary"
        Severity = "P0"
        Likelihood = 3
        Pattern = '(?i)\b(amount|price|balance|limit|offset|page|count|total|quantity|discount|fee|rate|tax)\b'
        Scenarios = @(
            @{ Vector = "Zero boundary (0, 0.0, -0.0)"; Expected = "Handled gracefully; zero division avoided"; Sev = "P1" },
            @{ Vector = "Negative value (-1, -100.00)"; Expected = "Explicit ValidationError raised; negative rejected"; Sev = "P0" },
            @{ Vector = "Maximum integer boundary (2^31-1, 2^63-1)"; Expected = "Handled without integer overflow or crash"; Sev = "P1" },
            @{ Vector = "Off-by-one upper/lower boundary (N-1, N, N+1)"; Expected = "Boundary properly enclosed; exact limits respected"; Sev = "P1" }
        )
    },
    @{
        Dimension = "Floating-Point Precision"
        Category = "Precision"
        Severity = "P1"
        Likelihood = 3
        Pattern = '(?i)\b(float|decimal|price|currency|tax|rate|cent|percent|calculate)\b'
        Scenarios = @(
            @{ Vector = "Micro-penny / fractional cent rounding (0.005)"; Expected = "Exact deterministic rounding (e.g. ROUND_HALF_UP)"; Sev = "P1" },
            @{ Vector = "Floating-point drift (0.1 + 0.2 != 0.3)"; Expected = "Exact equality preserved using Decimal/integer cents"; Sev = "P1" },
            @{ Vector = "Infinite / NaN values"; Expected = "Rejected with explicit validation error"; Sev = "P0" }
        )
    },
    @{
        Dimension = "String & Encodings"
        Category = "Strings"
        Severity = "P1"
        Likelihood = 3
        Pattern = '(?i)\b(string|text|name|code|title|description|email|username|token|url|password)\b'
        Scenarios = @(
            @{ Vector = "Empty string '' and whitespace-only '   '"; Expected = "Trimmed and validated; rejected if required"; Sev = "P2" },
            @{ Vector = "Surrogate pairs / 4-byte astral emojis (👨‍👩‍👧‍👦, 🎁)"; Expected = "Stored and retrieved without byte truncation or crash"; Sev = "P2" },
            @{ Vector = "Multi-byte UTF-8 and RTL characters (ñ, 日本語, עברית)"; Expected = "Normalized and handled with correct grapheme length"; Sev = "P3" },
            @{ Vector = "Extreme string length (10,000+ chars)"; Expected = "Rejected at boundary; ReDoS avoided"; Sev = "P1" },
            @{ Vector = "Control characters (\0, \r\n, \t, escape codes)"; Expected = "Sanitized or rejected; no terminal or log pollution"; Sev = "P2" }
        )
    },
    @{
        Dimension = "Collections & Structures"
        Category = "Collections"
        Severity = "P1"
        Likelihood = 3
        Pattern = '(?i)\b(list|array|items|collection|records|entries|batch|elements|children)\b'
        Scenarios = @(
            @{ Vector = "Empty collection [] or {}"; Expected = "Handled cleanly without IndexOutOfBounds or NoSuchElement"; Sev = "P1" },
            @{ Vector = "Single item collection [x]"; Expected = "Iteration and delimiter joining succeed without formatting errors"; Sev = "P2" },
            @{ Vector = "Duplicate elements [x, x, x]"; Expected = "Deduplicated or handled according to business uniqueness rules"; Sev = "P2" },
            @{ Vector = "Massive collection (100,000+ items)"; Expected = "Memory consumption bounded; pagination enforced"; Sev = "P1" }
        )
    },
    @{
        Dimension = "Nullability & Absence"
        Category = "Nulls"
        Severity = "P0"
        Likelihood = 3
        Pattern = '(?i)\b(optional|nullable|null|none|nil|undefined|default|fallback)\b'
        Scenarios = @(
            @{ Vector = "Explicit null / None payload"; Expected = "Default fallback applied or typed ValidationError raised"; Sev = "P0" },
            @{ Vector = "Missing / omitted payload keys ({})"; Expected = "Missing required fields detected; descriptive error returned"; Sev = "P1" },
            @{ Vector = "Type coercion mismatch (string '123' passed for integer)"; Expected = "Type-checked strictly; implicit coercion prevented"; Sev = "P2" }
        )
    },
    @{
        Dimension = "Concurrency & Race Hazards"
        Category = "Concurrency"
        Severity = "P0"
        Likelihood = 2
        Pattern = '(?i)\b(async|thread|lock|concurrent|parallel|transaction|balance|redeem|checkout|voucher|queue|worker)\b'
        Scenarios = @(
            @{ Vector = "Simultaneous double-submit / parallel execution (TOCTOU)"; Expected = "Atomic lock/CAS ensures exactly one transaction succeeds"; Sev = "P0" },
            @{ Vector = "Out-of-order event delivery / message jitter"; Expected = "Sequence versions checked; stale writes rejected"; Sev = "P1" },
            @{ Vector = "High-contention resource locking"; Expected = "Zero deadlocks; lock acquisition timeout handled gracefully"; Sev = "P0" }
        )
    },
    @{
        Dimension = "State Machine & Lifecycles"
        Category = "State"
        Severity = "P1"
        Likelihood = 2
        Pattern = '(?i)\b(status|state|lifecycle|transition|init|start|stop|close|cancel|refund|complete|pending)\b'
        Scenarios = @(
            @{ Vector = "Illegal state transition (e.g. CANCELLED -> COMPLETED)"; Expected = "Explicit IllegalStateTransitionError raised"; Sev = "P1" },
            @{ Vector = "Premature invocation (method called before init)"; Expected = "UnitializedStateError raised cleanly; no null pointer crash"; Sev = "P1" },
            @{ Vector = "Double finalization (close() called twice)"; Expected = "Strictly idempotent; no-op on subsequent calls"; Sev = "P2" }
        )
    },
    @{
        Dimension = "Resource Limits & Starvation"
        Category = "Resources"
        Severity = "P1"
        Likelihood = 2
        Pattern = '(?i)\b(file|io|stream|socket|connection|pool|buffer|memory|disk|cache|upload)\b'
        Scenarios = @(
            @{ Vector = "Unclosed resource / file descriptor on exception"; Expected = "Resources cleaned in finally/defer; zero descriptor leak"; Sev = "P1" },
            @{ Vector = "Payload size exceeding memory threshold"; Expected = "Streamed processing or 413 Payload Too Large returned"; Sev = "P1" }
        )
    },
    @{
        Dimension = "Distributed & Network"
        Category = "Network"
        Severity = "P1"
        Likelihood = 2
        Pattern = '(?i)\b(http|api|remote|fetch|request|timeout|retry|client|service|webhook)\b'
        Scenarios = @(
            @{ Vector = "Upstream service timeout / connection drop"; Expected = "Circuit breaker / retry policy triggers with bounded timeout"; Sev = "P1" },
            @{ Vector = "Duplicate webhook / idempotency key replay"; Expected = "Idempotency cache returns cached response without duplicate side effect"; Sev = "P0" }
        )
    },
    @{
        Dimension = "Security & Injection"
        Category = "Security"
        Severity = "P0"
        Likelihood = 2
        Pattern = '(?i)\b(input|path|file|query|sql|command|param|header|auth|token|json)\b'
        Scenarios = @(
            @{ Vector = "Path traversal sequences (../../etc/passwd, ..\\..\\win.ini)"; Expected = "Path canonicalized; traversal rejected"; Sev = "P0" },
            @{ Vector = "Injection metacharacters (' OR 1=1 --, $(whoami), <script>)"; Expected = "Parameterized or escaped; treated as raw literals"; Sev = "P0" },
            @{ Vector = "Prototype pollution / object injection (__proto__, constructor)"; Expected = "Prototype keys stripped or isolated"; Sev = "P0" }
        )
    }
)

# Read input content
$ContentToAnalyze = ""
if ($SpecFile -and (Test-Path $SpecFile)) {
    $ContentToAnalyze += Get-Content -Path $SpecFile -Raw
    Write-Host "[INFO] Loaded specification from $SpecFile" -ForegroundColor Cyan
}
if ($SourceFile -and (Test-Path $SourceFile)) {
    $ContentToAnalyze += "`n" + (Get-Content -Path $SourceFile -Raw)
    Write-Host "[INFO] Loaded source code from $SourceFile" -ForegroundColor Cyan
}

if (-not $ContentToAnalyze) {
    Write-Host "[WARN] No input file provided or file empty. Generating standard 10-dimension corner-case baseline for '$Component'." -ForegroundColor Yellow
}

# Discover relevant dimensions based on regex pattern matching
$DiscoveredCases = [System.Collections.Generic.List[PSCustomObject]]::new()
$CaseCounter = 1

foreach ($rule in $DimensionRules) {
    $matched = $false
    if ($ContentToAnalyze) {
        if ($ContentToAnalyze -match $rule.Pattern) {
            $matched = $true
        }
    } else {
        # Default baseline: include all
        $matched = $true
    }

    if ($matched) {
        foreach ($scen in $rule.Scenarios) {
            $caseId = "CC-{0:D3}" -f $CaseCounter
            $CaseCounter++
            
            $sevScore = switch ($scen.Sev) {
                "P0" { 3 }
                "P1" { 2 }
                default { 1 }
            }
            $risk = $sevScore * $rule.Likelihood

            $caseObj = [PSCustomObject]@{
                CaseId = $caseId
                Dimension = $rule.Dimension
                Category = $rule.Category
                Severity = $scen.Sev
                Likelihood = $rule.Likelihood
                RiskScore = $risk
                TriggerVector = $scen.Vector
                ExpectedInvariant = $scen.Expected
                Status = "PENDING_TEST"
            }
            $DiscoveredCases.Add($caseObj)
        }
    }
}

# Sort by RiskScore descending
$DiscoveredCases = [System.Collections.Generic.List[PSCustomObject]]($DiscoveredCases | Sort-Object RiskScore -Descending)

# Output summary to console
Write-Host "`n========================================================" -ForegroundColor Green
Write-Host " ADVERSARIAL CORNER-CASE DISCOVERY MATRIX: $Component" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "Total Corner Cases Identified: $($DiscoveredCases.Count)" -ForegroundColor White
$p0Count = ($DiscoveredCases | Where-Object { $_.Severity -eq "P0" }).Count
$p1Count = ($DiscoveredCases | Where-Object { $_.Severity -eq "P1" }).Count
$p2Count = ($DiscoveredCases | Where-Object { $_.Severity -eq "P2" }).Count
$p3Count = ($DiscoveredCases | Where-Object { $_.Severity -eq "P3" }).Count
Write-Host "Critical (P0): $p0Count | High (P1): $p1Count | Medium (P2): $p2Count | Low (P3): $p3Count" -ForegroundColor Cyan

# Generate Markdown
$mdLines = [System.Collections.Generic.List[string]]::new()
$mdLines.Add("# Corner-Case Discovery Matrix: $Component")
$mdLines.Add("")
$mdLines.Add("**Generated At**: " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + "  ")
$mdLines.Add("**Target Component**: ``" + $Component + "``  ")
$mdLines.Add("**Total Cases Discovered**: " + $DiscoveredCases.Count + " (P0: " + $p0Count + ", P1: " + $p1Count + ", P2: " + $p2Count + ", P3: " + $p3Count + ")  ")
$mdLines.Add("")
$mdLines.Add("---")
$mdLines.Add("")
$mdLines.Add("## Exhaustive Corner-Case Register")
$mdLines.Add("")
$mdLines.Add("| Case ID | Dimension | Severity | Risk Score | Input Trigger Vector | Expected Invariant / Outcome | Test Status |")
$mdLines.Add("| :--- | :--- | :---: | :---: | :--- | :--- | :---: |")

foreach ($c in $DiscoveredCases) {
    $line = "| `{0}` | {1} | {2} | {3} | {4} | {5} | `PENDING` |" -f $c.CaseId, $c.Dimension, $c.Severity, $c.RiskScore, $c.TriggerVector, $c.ExpectedInvariant
    $mdLines.Add($line)
}

$mdLines.Add("")
$mdLines.Add("---")
$mdLines.Add("*Generated automatically by Corner-Case Tester Agent.*")

$markdownOutput = $mdLines -join "`n"

if ($MarkdownOut) {
    Set-Content -Path $MarkdownOut -Value $markdownOutput -Encoding utf8
    Write-Host "[SUCCESS] Markdown matrix written to: $MarkdownOut" -ForegroundColor Green
} else {
    Write-Host "`n$markdownOutput`n"
}

if ($JsonOut) {
    $json = $DiscoveredCases | ConvertTo-Json -Depth 5
    Set-Content -Path $JsonOut -Value $json -Encoding utf8
    Write-Host "[SUCCESS] JSON matrix written to: $JsonOut" -ForegroundColor Green
}

exit 0
