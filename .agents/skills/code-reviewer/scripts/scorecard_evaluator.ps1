<#
.SYNOPSIS
    Code Review Scorecard Evaluator (PowerShell 7).
.DESCRIPTION
    Computes weighted quality scores and generates automated verdicts
    (APPROVE, REQUEST_CHANGES, COMMENT) based on review findings and severity counts.
.EXAMPLE
    pwsh scorecard_evaluator.ps1 -Blockers 0 -Majors 1 -Minors 2
#>

[CmdletBinding()]
param(
    [int]$Blockers = 0,
    [int]$Majors = 0,
    [int]$Minors = 0,
    [ValidateRange(1, 5)][int]$Architecture = 5,
    [ValidateRange(1, 5)][int]$Correctness = 5,
    [ValidateRange(1, 5)][int]$Security = 5,
    [ValidateRange(1, 5)][int]$Concurrency = 5,
    [ValidateRange(1, 5)][int]$Performance = 5,
    [ValidateRange(1, 5)][int]$Reliability = 5,
    [ValidateRange(1, 5)][int]$Testing = 5,
    [ValidateRange(1, 5)][int]$Maintainability = 5,
    [switch]$AsJson
)

$CategoryWeights = [ordered]@{
    "Architecture"    = @{ Weight = 0.15; Score = $Architecture }
    "Correctness"     = @{ Weight = 0.20; Score = $Correctness }
    "Security"        = @{ Weight = 0.20; Score = $Security }
    "Concurrency"     = @{ Weight = 0.15; Score = $Concurrency }
    "Performance"     = @{ Weight = 0.10; Score = $Performance }
    "Reliability"     = @{ Weight = 0.10; Score = $Reliability }
    "Testing"         = @{ Weight = 0.05; Score = $Testing }
    "Maintainability" = @{ Weight = 0.05; Score = $Maintainability }
}

$weightedSum = 0.0
$breakdown = [ordered]@{}

foreach ($entry in $CategoryWeights.GetEnumerator()) {
    $cat = $entry.Key
    $weight = $entry.Value.Weight
    $raw = $entry.Value.Score
    $earned = ($raw / 5.0) * ($weight * 100)
    $weightedSum += $earned
    $breakdown[$cat] = [PSCustomObject]@{
        RawScore = $raw
        WeightPct = [int]($weight * 100)
        PointsEarned = [Math]::Round($earned, 1)
    }
}

$penalty = ($Blockers * 40) + ($Majors * 15) + ($Minors * 2)
$finalScore = [Math]::Max(0, [Math]::Min(100, [Math]::Round($weightedSum - $penalty, 1)))

if ($Blockers -gt 0) {
    $verdict = "REQUEST_CHANGES"
    $reason = "Contains $Blockers critical blocker(s) that must be resolved before merge."
} elseif ($Majors -gt 0) {
    $verdict = "REQUEST_CHANGES"
    $reason = "Contains $Majors major issue(s) that require fixes."
} elseif ($finalScore -lt 75.0) {
    $verdict = "REQUEST_CHANGES"
    $reason = "Overall quality score ($finalScore/100) falls below acceptance threshold (75/100)."
} elseif ($Minors -gt 5) {
    $verdict = "COMMENT / NEEDS_DISCUSSION"
    $reason = "High number of minor issues ($Minors); consider cleaning up before final sign-off."
} else {
    $verdict = "APPROVE"
    $reason = "Meets high quality bar ($finalScore/100) with zero blockers or major issues."
}

$result = [PSCustomObject]@{
    FinalScore = $finalScore
    BaseWeightedScore = [Math]::Round($weightedSum, 1)
    PenaltyPoints = $penalty
    Verdict = $verdict
    Reason = $reason
    IssueCounts = [PSCustomObject]@{
        Blockers = $Blockers
        Majors = $Majors
        Minors = $Minors
    }
    CategoryBreakdown = $breakdown
}

if ($AsJson) {
    $result | ConvertTo-Json -Depth 4
    return
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " 📊 CODE REVIEW SCORECARD EVALUATION RESULT" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Overall Score  : $finalScore / 100" -ForegroundColor Yellow
Write-Host "Verdict        : $verdict" -ForegroundColor $(if ($verdict -eq "APPROVE") { "Green" } else { "Red" })
Write-Host "Reason         : $reason"
Write-Host "--------------------------------------------------"
Write-Host "Defect Counts  : $Blockers Blockers, $Majors Majors, $Minors Minors"
Write-Host "--------------------------------------------------"
Write-Host "Category Breakdown (Score / 5):"
foreach ($cat in $breakdown.Keys) {
    $b = $breakdown[$cat]
    Write-Host (" - {0,-16}: {1}/5 ({2} / {3} pts)" -f $cat, $b.RawScore, $b.PointsEarned, $b.WeightPct)
}
Write-Host "==================================================" -ForegroundColor Cyan
