<#
.SYNOPSIS
    High-Quality Code Review Diff & Hygiene Analyzer (PowerShell 7).
.DESCRIPTION
    Scans unified git diff files or piped diff text for security red flags,
    debug leftovers (console.log, print, debugger), anti-slop markers (TODO/FIXME),
    and computes the test-to-production code ratio.
.EXAMPLE
    pwsh review_diff.ps1 -DiffFile "path/to/pr.diff"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$DiffFile,

    [Parameter(Mandatory = $false)]
    [switch]$AsJson
)

$SecurityPatterns = @(
    @{ Name = "Hardcoded Secret / API Key"; Pattern = '(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|bearer\s+[a-z0-9_\-\.]{20,}|[''"][A-Za-z0-9/+=]{40}[''"])'; Severity = "BLOCKER" },
    @{ Name = "Dangerous Code Execution (eval / exec)"; Pattern = '\b(eval|exec)\s*\('; Severity = "BLOCKER" },
    @{ Name = "Command Injection Risk (shell=True / os.system)"; Pattern = '(subprocess\.(Popen|run|call)\s*\(.*shell\s*=\s*True|os\.system\s*\()'; Severity = "BLOCKER" },
    @{ Name = "Raw SQL Concatenation Risk"; Pattern = '(execute|raw_query|rawQuery)\s*\(\s*(f[''"]|[''"].*%\s*\(|[''"].*\+\s*\w+)'; Severity = "BLOCKER" },
    @{ Name = "Unsafe React innerHTML Injection"; Pattern = 'dangerouslySetInnerHTML\s*='; Severity = "MAJOR" }
)

$HygienePatterns = @(
    @{ Name = "Debug Print Leftover (console.log / print)"; Pattern = '(^\s*console\.(log|debug|info)\s*\(|^\s*print\s*\(|fmt\.Println\()'; Severity = "MINOR" },
    @{ Name = "Debugger / Breakpoint Leftover"; Pattern = '\b(debugger;|pdb\.set_trace\(\)|breakpoint\(\)|binding\.pry)\b'; Severity = "MAJOR" },
    @{ Name = "TypeScript Type Suppression (@ts-ignore / @ts-expect-error)"; Pattern = '//\s*@ts-(ignore|expect-error)'; Severity = "MINOR" },
    @{ Name = "Python Type/Lint Suppression (# type: ignore / # noqa)"; Pattern = '#\s*(type:\s*ignore|noqa)'; Severity = "MINOR" },
    @{ Name = "Unresolved Anti-Slop Marker (TODO / FIXME / XXX)"; Pattern = '\b(TODO|FIXME|HACK|XXX)\b'; Severity = "MINOR" }
)

function Test-IsTestFile([string]$path) {
    $lower = $path.ToLower()
    return ($lower.Contains("test") -or $lower.Contains("spec") -or $lower.Contains("__tests__") -or
            $lower.EndsWith("_test.go") -or $lower.EndsWith("_test.py") -or
            $lower.EndsWith(".test.ts") -or $lower.EndsWith(".spec.ts") -or $lower.EndsWith(".test.js"))
}

# Read content
if ($DiffFile) {
    if (-not (Test-Path $DiffFile)) {
        Write-Error "Diff file not found: $DiffFile"
        exit 1
    }
    $lines = Get-Content -Path $DiffFile
} else {
    $lines = [Console]::In.ReadToEnd() -split "`r?`n"
}

$fileStats = @{}
$findings = [System.Collections.Generic.List[PSCustomObject]]::new()
$currentFile = "unknown"
$isDeleted = $false
$currentLineNo = 0

foreach ($line in $lines) {
    if ($line.StartsWith("diff --git")) {
        $parts = $line.Split(" ")
        if ($parts.Count -ge 4) {
            $currentFile = $parts[3].TrimStart("b/")
        } else {
            $currentFile = "unknown"
        }
        if (-not $fileStats.ContainsKey($currentFile)) {
            $fileStats[$currentFile] = @{ Added = 0; Deleted = 0 }
        }
        $isDeleted = $false
        continue
    }

    if ($line.StartsWith("--- a/")) { continue }
    if ($line.StartsWith("+++ b/")) {
        if ($line -eq "+++ /dev/null") {
            $isDeleted = $true
        } else {
            $currentFile = $line.Substring(6)
            if (-not $fileStats.ContainsKey($currentFile)) {
                $fileStats[$currentFile] = @{ Added = 0; Deleted = 0 }
            }
        }
        continue
    }

    if ($line.StartsWith("@@")) {
        if ($line -match '\+(\d+)') {
            $currentLineNo = [int]$matches[1] - 1
        }
        continue
    }

    if ($isDeleted) { continue }

    if ($line.StartsWith("+") -and -not $line.StartsWith("+++")) {
        $currentLineNo++
        $content = $line.Substring(1)
        if ($fileStats.ContainsKey($currentFile)) {
            $fileStats[$currentFile].Added++
        }

        foreach ($sp in $SecurityPatterns) {
            if ($content -match $sp.Pattern) {
                $findings.Add([PSCustomObject]@{
                    File = $currentFile
                    Line = $currentLineNo
                    Content = $content.Trim()
                    Rule = $sp.Name
                    Category = "SECURITY"
                    Severity = $sp.Severity
                })
            }
        }

        foreach ($hp in $HygienePatterns) {
            if ($content -match $hp.Pattern) {
                $findings.Add([PSCustomObject]@{
                    File = $currentFile
                    Line = $currentLineNo
                    Content = $content.Trim()
                    Rule = $hp.Name
                    Category = "HYGIENE"
                    Severity = $hp.Severity
                })
            }
        }
    } elseif ($line.StartsWith("-") -and -not $line.StartsWith("---")) {
        if ($fileStats.ContainsKey($currentFile)) {
            $fileStats[$currentFile].Deleted++
        }
    } elseif (-not $line.StartsWith("+")) {
        $currentLineNo++
    }
}

$prodAdded = 0
$testAdded = 0
foreach ($entry in $fileStats.GetEnumerator()) {
    if (Test-IsTestFile $entry.Key) {
        $testAdded += $entry.Value.Added
    } else {
        $prodAdded += $entry.Value.Added
    }
}

$testRatio = if ($prodAdded -gt 0) { [Math]::Round(($testAdded / $prodAdded), 2) } else { 1.0 }

$blockers = ($findings | Where-Object { $_.Severity -eq "BLOCKER" }).Count
$majors = ($findings | Where-Object { $_.Severity -eq "MAJOR" }).Count
$minors = ($findings | Where-Object { $_.Severity -eq "MINOR" }).Count

$result = [PSCustomObject]@{
    FilesAnalyzed = $fileStats.Count
    TotalLinesAdded = ($fileStats.Values | Measure-Object -Property Added -Sum).Sum
    TotalLinesDeleted = ($fileStats.Values | Measure-Object -Property Deleted -Sum).Sum
    ProductionLinesAdded = $prodAdded
    TestLinesAdded = $testAdded
    TestToCodeRatio = $testRatio
    Summary = [PSCustomObject]@{
        Blockers = $blockers
        Majors = $majors
        Minors = $minors
    }
    Findings = $findings
}

if ($AsJson) {
    $result | ConvertTo-Json -Depth 5
    return
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " 🛡️  CODE REVIEW DIFF HYGIENE & PRE-FLIGHT AUDIT" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Files Modified     : $($result.FilesAnalyzed)"
Write-Host "Lines Added        : $($result.TotalLinesAdded) (+$prodAdded prod, +$testAdded test)"
Write-Host "Lines Deleted      : $($result.TotalLinesDeleted)"
Write-Host "Test-to-Code Ratio : $testRatio (Recommended: >= 0.50)"
Write-Host "--------------------------------------------------"
Write-Host "Findings: $blockers Blocker(s), $majors Major(s), $minors Minor(s)"
Write-Host "=================================================="

if ($findings.Count -gt 0) {
    foreach ($f in $findings) {
        $color = if ($f.Severity -eq "BLOCKER") { "Red" } elseif ($f.Severity -eq "MAJOR") { "Yellow" } else { "Gray" }
        Write-Host "[$($f.Severity)] $($f.File):$($f.Line) - $($f.Rule)" -ForegroundColor $color
        Write-Host "   Snippet: $($f.Content)"
    }
    Write-Host "=================================================="
} else {
    Write-Host "✅ No automated hygiene or security red flags detected." -ForegroundColor Green
}
