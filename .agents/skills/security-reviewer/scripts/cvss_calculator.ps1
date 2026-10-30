<#
.SYNOPSIS
    CVSS v3.1 Calculator & Severity Evaluator (PowerShell 7).
.DESCRIPTION
    Calculates CVSS v3.1 base score, subscores, and severity rating from vector or parameters.
.EXAMPLE
    pwsh cvss_calculator.ps1 -Vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
#>

[CmdletBinding()]
param(
    [string]$Vector,
    [ValidateSet("N", "A", "L", "P")][string]$AV = "N",
    [ValidateSet("L", "H")][string]$AC = "L",
    [ValidateSet("N", "L", "H")][string]$PR = "N",
    [ValidateSet("N", "R")][string]$UI = "N",
    [ValidateSet("U", "C")][string]$S = "U",
    [ValidateSet("H", "L", "N")][string]$C = "H",
    [ValidateSet("H", "L", "N")][string]$I = "H",
    [ValidateSet("H", "L", "N")][string]$A = "H",
    [switch]$AsJson
)

$AVWeights = @{ "N" = 0.85; "A" = 0.62; "L" = 0.55; "P" = 0.20 }
$ACWeights = @{ "L" = 0.77; "H" = 0.44 }
$PRUnchanged = @{ "N" = 0.85; "L" = 0.62; "H" = 0.27 }
$PRChanged   = @{ "N" = 0.85; "L" = 0.68; "H" = 0.50 }
$UIWeights   = @{ "N" = 0.85; "R" = 0.62 }
$CIAWeights  = @{ "H" = 0.56; "L" = 0.22; "N" = 0.00 }

function Round-CvssUp([double]$Val) {
    $intInput = [Math]::Floor($Val * 100000 + 0.5)
    if ($intInput % 10000 -eq 0) {
        return ($intInput / 100000.0)
    } else {
        return (([Math]::Floor($intInput / 10000) + 1) / 10.0)
    }
}

if ($Vector) {
    $clean = $Vector.Trim().Trim("'`"")
    $parts = $clean.Split('/')
    foreach ($p in $parts) {
        if ($p -match '^([A-Za-z]+):([A-Za-z]+)$') {
            $k = $Matches[1].ToUpper()
            $v = $Matches[2].ToUpper()
            switch ($k) {
                "AV" { $AV = $v }
                "AC" { $AC = $v }
                "PR" { $PR = $v }
                "UI" { $UI = $v }
                "S"  { $S  = $v }
                "C"  { $C  = $v }
                "I"  { $I  = $v }
                "A"  { $A  = $v }
            }
        }
    }
}

$scopeChanged = ($S -eq "C")
$prWeight = if ($scopeChanged) { $PRChanged[$PR] } else { $PRUnchanged[$PR] }

$iss = 1.0 - ((1.0 - $CIAWeights[$C]) * (1.0 - $CIAWeights[$I]) * (1.0 - $CIAWeights[$A]))

$impact = if (-not $scopeChanged) {
    6.42 * $iss
} else {
    7.52 * ($iss - 0.029) - 3.25 * [Math]::Pow(($iss - 0.02), 15)
}

$exploitability = 8.22 * $AVWeights[$AV] * $ACWeights[$AC] * $prWeight * $UIWeights[$UI]

$baseScore = if ($impact -le 0) {
    0.0
} elseif (-not $scopeChanged) {
    Round-CvssUp ([Math]::Min(($impact + $exploitability), 10.0))
} else {
    Round-CvssUp ([Math]::Min((1.08 * ($impact + $exploitability)), 10.0))
}

$severity = if ($baseScore -eq 0.0) { "NONE" }
    elseif ($baseScore -le 3.9) { "LOW" }
    elseif ($baseScore -le 6.9) { "MEDIUM" }
    elseif ($baseScore -le 8.9) { "HIGH" }
    else { "CRITICAL" }

$vectorCanonical = "CVSS:3.1/AV:$AV/AC:$AC/PR:$PR/UI:$UI/S:$S/C:$C/I:$I/A:$A"

$result = [PSCustomObject]@{
    Vector         = $vectorCanonical
    BaseScore      = $baseScore
    Severity       = $severity
    ImpactSubscore = [Math]::Round($impact, 2)
    Exploitability = [Math]::Round($exploitability, 2)
}

if ($AsJson) {
    $result | ConvertTo-Json
} else {
    Write-Host ("`n" + ("=" * 60))
    Write-Host " 🎯 CVSS v3.1 EVALUATION RESULT (PowerShell 7)" -ForegroundColor Cyan
    Write-Host ("=" * 60)
    Write-Host "  Vector String       : $($result.Vector)"
    $color = switch ($result.Severity) {
        "CRITICAL" { "Red" }
        "HIGH"     { "DarkRed" }
        "MEDIUM"   { "Yellow" }
        default    { "Gray" }
    }
    Write-Host "  Base Score          : $($result.BaseScore) / 10.0" -ForegroundColor $color
    Write-Host "  Qualitative Severity: $($result.Severity)" -ForegroundColor $color
    Write-Host "  Impact Subscore     : $($result.ImpactSubscore)"
    Write-Host "  Exploitability      : $($result.Exploitability)"
    Write-Host ("=" * 60 + "`n")
}
