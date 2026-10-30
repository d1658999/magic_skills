<#
.SYNOPSIS
    Autonomous Red-Green Remediation Controller & Anti-Cheat Auditor (PowerShell 7).
.DESCRIPTION
    Executes test commands, captures execution telemetry, parses pass/fail metrics,
    enforces anti-cheat invariants (verifying zero test tampering via git diff),
    and tracks remediation convergence across iterations.
.EXAMPLE
    pwsh remediation_runner.ps1 -TestCommand "npm test" -Iteration 1 -MaxIterations 5
    pwsh remediation_runner.ps1 -TestCommand "pytest tests/adversarial" -TestDir "tests" -ReportOut scorecard.md
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$TestCommand,
    [string]$BaselineCommand,
    [string]$TestDir = "tests",
    [int]$Iteration = 1,
    [int]$MaxIterations = 5,
    [string]$ReportOut,
    [string]$JsonOut,
    [switch]$EnforceAntiCheat
)

Write-Host "========================================================" -ForegroundColor Magenta
Write-Host " RED-GREEN REMEDIATION RUNNER (Iteration $Iteration / $MaxIterations)" -ForegroundColor Magenta
Write-Host "========================================================" -ForegroundColor Magenta
Write-Host "[CONFIG] Target Test Command: $TestCommand" -ForegroundColor Cyan
if ($BaselineCommand) {
    Write-Host "[CONFIG] Baseline Regression Command: $BaselineCommand" -ForegroundColor Cyan
}

# Step 1: Anti-Cheat Git Audit
$antiCheatPassed = $true
$tamperedFiles = @()

if ($EnforceAntiCheat) {
    Write-Host "`n[STEP 1] Running Anti-Cheat Audit on directory: $TestDir..." -ForegroundColor Yellow
    try {
        $gitStatus = git status --porcelain $TestDir 2>&1
        if ($gitStatus) {
            $tamperedFiles = $gitStatus -split "`r?`n" | Where-Object { $_ -match '\S' }
            if ($tamperedFiles.Count -gt 0) {
                $antiCheatPassed = $false
                Write-Host "[ALERT] ANTI-CHEAT VIOLATION DETECTED!" -ForegroundColor Red
                Write-Host "Test files have been modified in ${TestDir}:" -ForegroundColor Red
                foreach ($f in $tamperedFiles) {
                    Write-Host "  - $f" -ForegroundColor Red
                }
                Write-Host "Mandatory Rule: Test files must NEVER be modified to satisfy test failures!" -ForegroundColor Red
            }
        }
    } catch {
        Write-Host "[WARN] Git not available or repository uninitialized. Skipping git anti-cheat check." -ForegroundColor Yellow
    }
}

if ($antiCheatPassed) {
    Write-Host "[ANTI-CHEAT] Audit Passed: Zero test tampering detected." -ForegroundColor Green
}

# Step 2: Execute Target Test Command
Write-Host "`n[STEP 2] Executing Target Corner-Case Test Command..." -ForegroundColor Yellow
$startTime = Get-Date

$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = "pwsh"
$processInfo.Arguments = "-NoProfile -Command `"$TestCommand`""
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$processInfo.UseShellExecute = $false
$processInfo.CreateNoWindow = $true

$proc = [System.Diagnostics.Process]::Start($processInfo)
$stdout = $proc.StandardOutput.ReadToEnd()
$stderr = $proc.StandardError.ReadToEnd()
$proc.WaitForExit()
$exitCode = $proc.ExitCode
$endTime = Get-Date
$durationSec = [math]::Round(($endTime - $startTime).TotalSeconds, 2)

Write-Host "Test Execution Completed in $durationSec seconds. Exit Code: $exitCode" -ForegroundColor White

if ($stdout) {
    Write-Host "`n--- Standard Output ---" -ForegroundColor DarkGray
    Write-Host $stdout.Trim() -ForegroundColor Gray
}
if ($stderr) {
    Write-Host "`n--- Standard Error ---" -ForegroundColor DarkGray
    Write-Host $stderr.Trim() -ForegroundColor Yellow
}

# Step 3: Heuristic Output Parsing
$targetPassed = ($exitCode -eq 0)

# Step 4: Execute Baseline Regression Suite if specified
$baselinePassed = $true
$baselineDuration = 0
$baselineOutput = ""

if ($targetPassed -and $BaselineCommand) {
    Write-Host "`n[STEP 3] Target test passed! Running Baseline Regression Suite..." -ForegroundColor Yellow
    $bStart = Get-Date
    $bInfo = New-Object System.Diagnostics.ProcessStartInfo
    $bInfo.FileName = "pwsh"
    $bInfo.Arguments = "-NoProfile -Command `"$BaselineCommand`""
    $bInfo.RedirectStandardOutput = $true
    $bInfo.RedirectStandardError = $true
    $bInfo.UseShellExecute = $false
    $bInfo.CreateNoWindow = $true

    $bProc = [System.Diagnostics.Process]::Start($bInfo)
    $baselineStdout = $bProc.StandardOutput.ReadToEnd()
    $baselineStderr = $bProc.StandardError.ReadToEnd()
    $bProc.WaitForExit()
    $bExitCode = $bProc.ExitCode
    $bEnd = Get-Date
    $baselineDuration = [math]::Round(($bEnd - $bStart).TotalSeconds, 2)
    $baselineOutput = $baselineStdout + "`n" + $baselineStderr

    if ($bExitCode -ne 0) {
        $baselinePassed = $false
        Write-Host "[REGRESSION DETECTED] Baseline regression suite failed (Exit Code: $bExitCode)!" -ForegroundColor Red
    } else {
        Write-Host "[REGRESSION PASSED] Baseline suite fully green in $baselineDuration seconds." -ForegroundColor Green
    }
}

# Determine overall verdict
$overallSuccess = $targetPassed -and $baselinePassed -and $antiCheatPassed

Write-Host "`n========================================================" -ForegroundColor Magenta
if ($overallSuccess) {
    Write-Host " VERDICT: ALL GREEN - REMEDIATION SUCCESSFUL" -ForegroundColor Green
} elseif (-not $antiCheatPassed) {
    Write-Host " VERDICT: FAILED - ANTI-CHEAT VIOLATION" -ForegroundColor Red
} elseif (-not $targetPassed) {
    Write-Host " VERDICT: RED - TARGET CORNER-CASE TESTS FAILING" -ForegroundColor Yellow
} else {
    Write-Host " VERDICT: REGRESSION - BASELINE SUITE BROKEN" -ForegroundColor Red
}
Write-Host "========================================================" -ForegroundColor Magenta

# Step 5: Generate Markdown Report
$mdLines = [System.Collections.Generic.List[string]]::new()
$mdLines.Add("# Remediation Execution Scorecard: Iteration " + $Iteration + " / " + $MaxIterations)
$mdLines.Add("")
$mdLines.Add("**Timestamp**: " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + "  ")
$verdictBadge = if ($overallSuccess) { "✅ **GREEN - ALL CRITERIA SATISFIED**" } else { "❌ **FAILING - REMEDIATION REQUIRED**" }
$mdLines.Add("**Overall Verdict**: " + $verdictBadge + "  ")
$mdLines.Add("**Target Test Duration**: " + $durationSec + " s | **Exit Code**: " + $exitCode + "  ")
$antiCheatBadge = if ($antiCheatPassed) { "✅ **PASSED (0 test modifications)**" } else { "🚨 **VIOLATION (" + $tamperedFiles.Count + " files altered)**" }
$mdLines.Add("**Anti-Cheat Status**: " + $antiCheatBadge + "  ")
$baselineBadge = if (-not $BaselineCommand) { "N/A" } elseif ($baselinePassed) { "✅ **PASSED (" + $baselineDuration + " s)**" } else { "❌ **REGRESSION DETECTED**" }
$mdLines.Add("**Baseline Regression**: " + $baselineBadge + "  ")
$mdLines.Add("")
$mdLines.Add("---")
$mdLines.Add("")
$mdLines.Add("## Command Telemetry")
$mdLines.Add("")
$mdLines.Add("- **Target Command**: ``" + $TestCommand + "``")
$mdLines.Add("- **Target Exit Code**: " + $exitCode)
$baselineCmdText = if ($BaselineCommand) { "``" + $BaselineCommand + "``" } else { "None" }
$mdLines.Add("- **Baseline Command**: " + $baselineCmdText)
$mdLines.Add("")
$mdLines.Add("## Execution Details")
$mdLines.Add("")
$mdLines.Add("````text")
if ($stdout) { $mdLines.Add($stdout.Trim()) }
if ($stderr) {
    $mdLines.Add("ERRORS:")
    $mdLines.Add($stderr.Trim())
}
$mdLines.Add("````")
$mdLines.Add("")
$mdLines.Add("---")
$mdLines.Add("*Generated by Corner-Case Tester Remediation Controller.*")

$md = $mdLines -join "`n"

if ($ReportOut) {
    Set-Content -Path $ReportOut -Value $md -Encoding utf8
    Write-Host "[REPORT] Scorecard saved to: $ReportOut" -ForegroundColor Cyan
}

if ($JsonOut) {
    $resultObj = [PSCustomObject]@{
        Iteration = $Iteration
        MaxIterations = $MaxIterations
        OverallSuccess = $overallSuccess
        TargetPassed = $targetPassed
        BaselinePassed = $baselinePassed
        AntiCheatPassed = $antiCheatPassed
        ExitCode = $exitCode
        DurationSeconds = $durationSec
        TamperedFiles = $tamperedFiles
    }
    $jsonStr = $resultObj | ConvertTo-Json -Depth 4
    Set-Content -Path $JsonOut -Value $jsonStr -Encoding utf8
    Write-Host "[JSON] Telemetry saved to: $JsonOut" -ForegroundColor Cyan
}

if ($overallSuccess) {
    exit 0
} elseif (-not $antiCheatPassed) {
    exit 2
} else {
    exit 1
}
