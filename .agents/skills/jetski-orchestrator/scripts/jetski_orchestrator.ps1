#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Jetski Orchestrator PowerShell 7 Wrapper CLI.
    Forwards all subcommands and arguments directly to jetski_orchestrator.py.

.DESCRIPTION
    Supports all 12 unified subcommands of jetski-orchestrator:
      1. validate-spec
      2. validate-packets
      3. calc-coverage
      4. generate-corner-cases
      5. run-remediation
      6. audit-diff
      7. eval-review-scorecard
      8. audit-security
      9. calc-cvss
     10. generate-council-scorecard
     11. lock-tests
     12. generate-skeleton

.EXAMPLE
    pwsh .agents/skills/jetski-orchestrator/scripts/jetski_orchestrator.ps1 validate-packets --packet-dir ./docs/packets
    pwsh .agents/skills/jetski-orchestrator/scripts/jetski_orchestrator.ps1 calc-cvss --vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
#>

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "jetski_orchestrator.py"
if (-not (Test-Path -LiteralPath $scriptPath)) {
    Write-Error "Unable to locate Python CLI script at: $scriptPath"
    exit 1
}

& python "$PSScriptRoot/jetski_orchestrator.py" @args
exit $LASTEXITCODE
