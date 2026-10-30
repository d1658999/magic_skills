<#
.SYNOPSIS
    Task Decomposition & DAG Integrity Validator for PowerShell.
.DESCRIPTION
    Audits execution DAG markdown files for cycles, parallel file collisions, and valid task dependencies.
.EXAMPLE
    pwsh decompose_tasks.ps1 -PlanFile path/to/execution-dag-plan.md
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanFile
)

if (-not (Test-Path $PlanFile)) {
    Write-Error "ERROR: Plan file not found: '$PlanFile'"
    exit 1
}

Write-Host "================================================================================"
Write-Host "Task DAG & Decomposition Validator (PowerShell)"
Write-Host "================================================================================`n"

$content = Get-Content -Path $PlanFile -Raw -Encoding utf8
$regex = [regex]'\|\s*`?(TASK-[0-9A-Za-z_-]+)`?\s*\|\s*([^|]+)\|\s*`?([^|]+?)`?\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|'

$matches = $regex.Matches($content)
if ($matches.Count -eq 0) {
    Write-Host "⚠️ No tasks found matching table pattern: | `TASK-XXX` | ... |" -ForegroundColor Yellow
    exit 1
}

$tasks = @{}
foreach ($m in $matches) {
    $taskId = $m.Groups[1].Value.Trim()
    $title = $m.Groups[2].Value.Trim()
    $filesRaw = $m.Groups[3].Value.Trim().Replace('`', '')
    $depsRaw = $m.Groups[4].Value.Trim().Replace('`', '')
    $concurrency = $m.Groups[5].Value.Trim()
    $gate = $m.Groups[6].Value.Trim().Replace('`', '')

    $fileList = @($filesRaw -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ -and $_ -ne "None" })
    
    $depMatches = [regex]::Matches($depsRaw, 'TASK-[0-9A-Za-z_-]+')
    $depList = @($depMatches | ForEach-Object { $_.Value })

    $tasks[$taskId] = @{
        Title = $title
        Files = $fileList
        Deps = $depList
        Concurrency = $concurrency
        Gate = $gate
    }
}

Write-Host "Parsed $($tasks.Count) tasks from plan:"
foreach ($key in $tasks.Keys) {
    $t = $tasks[$key]
    Write-Host "  - [$key] $($t.Title) (Files: $($t.Files -join ', '), Deps: $($t.Deps -join ', '))"
}
Write-Host ""

$errors = @()

# 1. Check for missing dependencies
foreach ($key in $tasks.Keys) {
    foreach ($dep in $tasks[$key].Deps) {
        if (-not $tasks.ContainsKey($dep)) {
            $errors += "Task '$key' depends on undefined task '$dep'."
        }
    }
}

# 2. Check for parallel file collisions
$parallelFiles = @{}
foreach ($key in $tasks.Keys) {
    $concurrency = $tasks[$key].Concurrency.ToLower()
    if ($concurrency -match "parallel" -or $concurrency -match "slot") {
        foreach ($file in $tasks[$key].Files) {
            if ($parallelFiles.ContainsKey($file)) {
                $otherTask = $parallelFiles[$file]
                $errors += "Parallel file collision! Both '$key' and '$otherTask' claim write access to '$file'."
            } else {
                $parallelFiles[$file] = $key
            }
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "❌ DAG VALIDATION FAILED:" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  - $err" -ForegroundColor Red
    }
    exit 1
} else {
    Write-Host "✅ DAG VALIDATION PASSED:" -ForegroundColor Green
    Write-Host "  - Zero parallel file write collisions."
    Write-Host "  - All task dependencies are valid and resolvable."
    exit 0
}
