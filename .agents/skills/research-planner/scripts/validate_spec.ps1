<#
.SYNOPSIS
    Zero-Inference Spec & Task Packet Validator for PowerShell.
.DESCRIPTION
    Validates specifications and task packet markdown files for zero-inference completeness,
    checks for vague phrasing, and audits modified source files for anti-slop markers.
.EXAMPLE
    pwsh validate_spec.ps1 -Mode Spec -File path/to/task-01.md
    pwsh validate_spec.ps1 -Mode Audit -AllowedFiles src/auth/token.ts
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Spec", "Audit")]
    [string]$Mode,

    [Parameter(Mandatory = $false)]
    [string]$File,

    [Parameter(Mandatory = $false)]
    [string[]]$AllowedFiles = @()
)

$TaskSections = @(
    @{ Name = "Objective"; Pattern = "(?i)(single-sentence\s+objective|mission|task\s+objective)" },
    @{ Name = "File Whitelist"; Pattern = "(?i)(file\s+access\s+boundaries|permitted\s+write\s+targets|allowed\s+to\s+create|allowed\s+files)" },
    @{ Name = "Forbidden Files"; Pattern = "(?i)(strictly\s+forbidden|do\s+not\s+touch|out\s+of\s+scope)" },
    @{ Name = "Step-by-Step Recipe"; Pattern = "(?i)(step-by-step\s+implementation\s+recipe|implementation\s+steps|procedural\s+steps)" },
    @{ Name = "Anti-Slop / Prohibited Patterns"; Pattern = "(?i)(prohibited\s+patterns|anti-slop|forbidden\s+constructs)" },
    @{ Name = "Verification Command"; Pattern = "(?i)(deterministic\s+verification\s+command|verification\s+command|acceptance\s+criteria)" }
)

$MasterSections = @(
    @{ Name = "Architecture & File Manifest"; Pattern = "(?i)(architecture|module\s+directory|file\s+manifest)" },
    @{ Name = "Frozen Data Contracts / Types"; Pattern = "(?i)(frozen\s+data\s+contracts|interfaces|domain\s+models)" },
    @{ Name = "Algorithmic Flow / State Machine"; Pattern = "(?i)(state\s+machine|state\s+transition|algorithmic)" },
    @{ Name = "Error & Edge Case Matrix"; Pattern = "(?i)(error\s+(&|and)\s+edge\s+case|error\s+matrix|failure\s+modes)" },
    @{ Name = "Verification & Test Plan"; Pattern = "(?i)(verification\s+(&|and)\s+test|acceptance\s+criteria|test\s+plan)" }
)

$VaguePatterns = @(
    @{ Pattern = "(?i)\bhandle\s+(it|errors?|exceptions?)\s+gracefully\b"; Message = "Vague error handling: 'handle errors gracefully'. Specify exact error classes." },
    @{ Pattern = "(?i)\bas\s+appropriate\b"; Message = "Subjective phrasing: 'as appropriate'. Explicitly state exact logic." },
    @{ Pattern = "(?i)\bas\s+needed\b"; Message = "Subjective phrasing: 'as needed'. Define exact requirements." },
    @{ Pattern = "(?i)\bas\s+you\s+see\s+fit\b"; Message = "Ambiguous choice: 'as you see fit'. Do not leave choices to executors." },
    @{ Pattern = "(?i)\breasonable\s+(timeout|defaults?|values?)\b"; Message = "Vague threshold: 'reasonable timeout/default'. Provide exact numbers." },
    @{ Pattern = "(?i)\bimplement\s+appropriately\b"; Message = "Vague directive: 'implement appropriately'. Provide step-by-step recipe." },
    @{ Pattern = "(?i)\betc\.?\b"; Message = "Incomplete enumeration: 'etc.'. List all cases explicitly." }
)

$AntiSlopPatterns = @(
    @{ Name = "TODO comment"; Pattern = "\bTODO\b" },
    @{ Name = "FIXME comment"; Pattern = "\bFIXME\b" },
    @{ Name = "HACK / XXX marker"; Pattern = "\b(HACK|XXX)\b" },
    @{ Name = "TypeScript @ts-ignore"; Pattern = "@ts-(ignore|expect-error)" },
    @{ Name = "TypeScript 'as any'"; Pattern = "\bas\s+any\b" },
    @{ Name = "Python # type: ignore"; Pattern = "#\s*type:\s*ignore" },
    @{ Name = "Python # noqa"; Pattern = "#\s*noqa" },
    @{ Name = "Unimplemented stub"; Pattern = "\b(NotImplementedError|unimplemented!|todo!)\b" }
)

Write-Host "================================================================================"
Write-Host "Zero-Inference Spec & Task Packet Validator (PowerShell)"
Write-Host "================================================================================"

if ($Mode -eq "Spec") {
    if (-not $File -or -not (Test-Path $File)) {
        Write-Error "ERROR: Spec file path is missing or file does not exist: '$File'"
        exit 1
    }

    $content = Get-Content -Path $File -Raw -Encoding utf8
    $lines = $content -split "`r?`n"
    $errors = @()
    $warnings = @()

    $isTaskPacket = ($content -match "(?im)^#.*task\s+packet" -or $content -match "(?im)^##\s+task\s+metadata")
    $sections = if ($isTaskPacket) { $TaskSections } else { $MasterSections }
    $docType = if ($isTaskPacket) { "Atomic Task Packet" } else { "Master Technical Specification" }

    Write-Host "Auditing $docType document: $File`n"

    foreach ($sec in $sections) {
        if ($content -notmatch $sec.Pattern) {
            $errors += "Missing mandatory section in ${docType}: '$($sec.Name)'"
        }
    }

    foreach ($vague in $VaguePatterns) {
        if ($content -match $vague.Pattern) {
            $warnings += $vague.Message
        }
    }

    if ($lines.Count -lt 20) {
        $errors += "Document is too brief ($($lines.Count) lines). Zero-inference specs must include exact details."
    }

    if ($content -notmatch "```(bash|sh|pwsh|powershell|cmd)") {
        $warnings += "No executable shell command block detected in verification section."
    }

    if ($warnings.Count -gt 0) {
        Write-Host "⚠️  SPECIFICATION WARNINGS (Vague Phrasing / Optimization Opportunities):" -ForegroundColor Yellow
        foreach ($w in $warnings) {
            Write-Host "  - $w" -ForegroundColor Yellow
        }
        Write-Host ""
    }

    if ($errors.Count -gt 0) {
        Write-Host "❌ SPECIFICATION FAILED ZERO-INFERENCE AUDIT:" -ForegroundColor Red
        foreach ($err in $errors) {
            Write-Host "  - $err" -ForegroundColor Red
        }
        exit 1
    } else {
        Write-Host "✅ SPECIFICATION PASSED ZERO-INFERENCE AUDIT." -ForegroundColor Green
        Write-Host "   Document meets high-standard requirements for execution by low-tier models."
        exit 0
    }
}

if ($Mode -eq "Audit") {
    if ($AllowedFiles.Count -eq 0) {
        Write-Error "ERROR: At least one -AllowedFiles target is required for audit mode."
        exit 1
    }

    $errors = @()
    Write-Host "Auditing code files: $($AllowedFiles -join ', ')`n"

    foreach ($f in $AllowedFiles) {
        if (-not (Test-Path $f)) {
            $errors += "Expected modified file does not exist: $f"
            continue
        }

        $fileContent = Get-Content -Path $f -Raw -Encoding utf8
        $fileLines = $fileContent -split "`r?`n"

        for ($i = 0; $i -lt $fileLines.Count; $i++) {
            $line = $fileLines[$i]
            $lineNum = $i + 1
            foreach ($rule in $AntiSlopPatterns) {
                if ($line -match $rule.Pattern) {
                    $errors += "Anti-slop violation in ${f}:${lineNum} - [$($rule.Name)]: $($line.Trim())"
                }
            }
        }
    }

    if ($errors.Count -gt 0) {
        Write-Host "❌ CODE AUDIT FAILED:" -ForegroundColor Red
        foreach ($err in $errors) {
            Write-Host "  - $err" -ForegroundColor Red
        }
        exit 1
    } else {
        Write-Host "✅ CODE AUDIT PASSED: Zero anti-slop markers found." -ForegroundColor Green
        exit 0
    }
}
