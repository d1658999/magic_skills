<#
.SYNOPSIS
    Adversarial Security Code Scanner & Hygiene Analyzer (PowerShell 7).
.DESCRIPTION
    Scans unified git diffs or file directories for dangerous execution sinks,
    injection vulnerabilities, hardcoded secrets, cryptographic weaknesses, and
    infrastructure misconfigurations.
.EXAMPLE
    pwsh security_scanner.ps1 -DiffFile path/to/pr.diff
    pwsh security_scanner.ps1 -DirectoryPath ./src -FailOn HIGH
#>

[CmdletBinding()]
param(
    [string]$DiffFile,
    [string]$DirectoryPath,
    [ValidateSet("CRITICAL", "HIGH", "MEDIUM", "LOW")][string]$FailOn = "HIGH",
    [string]$JsonOut
)

$SecurityRules = @(
    # 1. Hardcoded Secrets
    @{
        Rule = "AWS Access Key ID"
        Pattern = '\b(AKIA[0-9A-Z]{16})\b'
        Severity = "CRITICAL"
        CWE = "CWE-798"
        Guidance = "Move AWS credentials to environment variables or IAM Roles / AWS Secrets Manager."
    },
    @{
        Rule = "Generic High-Entropy API Secret / Token"
        Pattern = '(?i)(secret[_-]?key|api[_-]?secret|auth[_-]?token|bearer\s+[a-z0-9_\-\.]{24,})\s*[:=]\s*[''"][A-Za-z0-9_\-]{16,}[''"]'
        Severity = "CRITICAL"
        CWE = "CWE-798"
        Guidance = "Never hardcode secrets in source code. Inject via environment variables or secret vaults."
    },
    @{
        Rule = "Private Cryptographic Key"
        Pattern = '-----BEGIN (RSA|EC|DSA|OPENSSH|PRIVATE) KEY-----'
        Severity = "CRITICAL"
        CWE = "CWE-321"
        Guidance = "Remove private key from repository immediately. Rotate the key and store in KMS/Vault."
    },
    @{
        Rule = "GitHub Personal Access Token"
        Pattern = '\b(ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})\b'
        Severity = "CRITICAL"
        CWE = "CWE-798"
        Guidance = "Revoke and rotate GitHub token immediately. Use GitHub Actions OIDC or repo secrets."
    },

    # 2. Execution & Injection
    @{
        Rule = "Arbitrary Code Execution (eval / exec)"
        Pattern = '\b(eval|exec)\s*\((?!.*(?:test|fixture))'
        Severity = "CRITICAL"
        CWE = "CWE-95"
        Guidance = "Avoid dynamic evaluation of code. Use safe parsing (ast.literal_eval or JSON.parse)."
    },
    @{
        Rule = "Command Injection (shell=True / os.system)"
        Pattern = '(subprocess\.(Popen|run|call|check_output)\s*\(.*shell\s*=\s*True|os\.system\s*\(|child_process\.exec\s*\()'
        Severity = "CRITICAL"
        CWE = "CWE-78"
        Guidance = "Avoid shell=True. Pass arguments as explicit arrays and use child_process.execFile with allowlists."
    },
    @{
        Rule = "Raw SQL String Formatting / Concatenation"
        Pattern = '(execute|raw_query|rawQuery|query)\s*\(\s*(f[''"]|[''"].*%\s*\(|[''"].*\+\s*\w+|`.*?\$\{)'
        Severity = "CRITICAL"
        CWE = "CWE-89"
        Guidance = "Use parameterized queries or prepared statements ($1, %s, :param) instead of string concatenation."
    },

    # 3. Deserialization & Cryptography
    @{
        Rule = "Unsafe Object Deserialization (pickle / unsafe yaml)"
        Pattern = '\b(pickle\.loads?|yaml\.load\s*\([^,)]+,\s*Loader\s*=\s*yaml\.(UnsafeLoader|Loader)|Marshal\.load|readObject\s*\()'
        Severity = "CRITICAL"
        CWE = "CWE-502"
        Guidance = "Deserializing untrusted data leads to Remote Code Execution. Use JSON, protobuf, or yaml.safe_load."
    },
    @{
        Rule = "Weak Hash Function (MD5 / SHA-1)"
        Pattern = '\b(hashlib\.(md5|sha1)\(|crypto\.createHash\([''"](md5|sha1)[''"]\)|MessageDigest\.getInstance\([''"](MD5|SHA-1)[''"]\))'
        Severity = "HIGH"
        CWE = "CWE-328"
        Guidance = "MD5 and SHA-1 are cryptographically broken. Use SHA-256 for integrity or Argon2id/bcrypt for passwords."
    },
    @{
        Rule = "Insecure Cipher Mode (AES-ECB)"
        Pattern = '\b(AES\.MODE_ECB|AES/ECB/|createCipheriv\([''"]aes-\d+-ecb[''"]\))'
        Severity = "HIGH"
        CWE = "CWE-327"
        Guidance = "ECB mode does not provide serious message confidentiality. Use AES-GCM or ChaCha20-Poly1305."
    },
    @{
        Rule = "Timing-Unsafe Token / Signature Equality"
        Pattern = '(hmac|signature|authToken|apiKey|secretToken)\s*(===|==)\s*'
        Severity = "MEDIUM"
        CWE = "CWE-208"
        Guidance = "String comparison leaks timing information. Use constant-time comparisons (crypto.timingSafeEqual or hmac.compare_digest)."
    },

    # 4. Network & SSRF
    @{
        Rule = "Disabled TLS / Certificate Verification"
        Pattern = '(verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*[''"]?0[''"]?|InsecureSkipVerify\s*:\s*true|rejectUnauthorized\s*:\s*false)'
        Severity = "HIGH"
        CWE = "CWE-295"
        Guidance = "Disabling certificate verification exposes traffic to Man-in-the-Middle (MitM) attacks."
    },
    @{
        Rule = "Potential SSRF Target (dynamic request URL)"
        Pattern = '(requests\.(get|post|put|delete)|axios\.(get|post)|fetch)\s*\(\s*(req\.(query|body|params)|request\.(args|json|GET|POST))'
        Severity = "HIGH"
        CWE = "CWE-918"
        Guidance = "Validate destination URLs against an allowlist. Block loopback, link-local (169.254.169.254), and private RFC1918 IPs."
    },

    # 5. Cloud & IaC
    @{
        Rule = "Container Running as Root (Dockerfile)"
        Pattern = '(?i)^\+?\s*USER\s+root'
        Severity = "MEDIUM"
        CWE = "CWE-250"
        Guidance = "Avoid running containers as root. Create and use an unprivileged user (e.g. USER nonroot)."
    },
    @{
        Rule = "Overly Permissive Ingress (0.0.0.0/0 on Sensitive Ports)"
        Pattern = 'cidr_blocks\s*=\s*\[\s*[''"]0\.0\.0\.0/0[''"]\s*\].*(?:port\s*=\s*(?:22|3389|5432|3306|27017|6379))'
        Severity = "HIGH"
        CWE = "CWE-284"
        Guidance = "Do not expose administrative or database ports to the public internet (0.0.0.0/0)."
    }
)

$Findings = [System.Collections.Generic.List[PSCustomObject]]::new()

function Test-Line {
    param([string]$Line, [int]$LineNumber, [string]$FilePath)
    foreach ($rule in $SecurityRules) {
        if ($Line -match $rule.Pattern) {
            $Findings.Add([PSCustomObject]@{
                Rule     = $rule.Rule
                Severity = $rule.Severity
                CWE      = $rule.CWE
                File     = $FilePath
                Line     = $LineNumber
                Code     = $Line.Trim().Substring(0, [Math]::Min($Line.Trim().Length, 140))
                Guidance = $rule.Guidance
            })
        }
    }
}

if ($DiffFile) {
    if (-not (Test-Path $DiffFile)) {
        Write-Error "Diff file not found: $DiffFile"
        exit 2
    }
    $currentFile = "unknown"
    $currentLine = 0
    foreach ($rawLine in Get-Content $DiffFile) {
        if ($rawLine -match '^\+\+\+ b/(.+)$') {
            $currentFile = $Matches[1]
            continue
        }
        if ($rawLine -match '^@@ -\d+(?:,\d+)? \+(\d+)') {
            $currentLine = [int]$Matches[1] - 1
            continue
        }
        if ($rawLine.StartsWith('+') -and -not $rawLine.StartsWith('+++')) {
            $currentLine++
            Test-Line -Line $rawLine.Substring(1) -LineNumber $currentLine -FilePath $currentFile
        } elseif (-not $rawLine.StartsWith('-')) {
            $currentLine++
        }
    }
} elseif ($DirectoryPath) {
    if (-not (Test-Path $DirectoryPath)) {
        Write-Error "Target directory not found: $DirectoryPath"
        exit 2
    }
    $skipDirs = @('.git', 'node_modules', 'vendor', '__pycache__', '.venv', 'dist', 'build')
    $resolvedDir = (Resolve-Path $DirectoryPath).Path
    $files = Get-ChildItem -Path $resolvedDir -Recurse -File | Where-Object {
        $rel = $_.FullName
        $skip = $false
        foreach ($sd in $skipDirs) {
            if ($rel -match "[\\/]$sd([\\/]|$)") { $skip = $true; break }
        }
        -not $skip
    }
    foreach ($file in $files) {
        $lines = Get-Content $file.FullName -ErrorAction SilentlyContinue
        $relPath = ($file.FullName.Substring($resolvedDir.Length)).TrimStart('\', '/')
        for ($i = 0; $i -lt $lines.Count; $i++) {
            Test-Line -Line $lines[$i] -LineNumber ($i + 1) -FilePath $relPath
        }
    }
} else {
    Write-Error "Must provide either -DiffFile or -DirectoryPath"
    exit 2
}

# Output report
Write-Host ("`n" + ("=" * 80))
Write-Host " 🛡️  SECURITY CODE SCAN REPORT (PowerShell 7)" -ForegroundColor Cyan
Write-Host ("=" * 80 + "`n")

if ($Findings.Count -eq 0) {
    Write-Host "✅ No critical security flags or hygiene violations detected." -ForegroundColor Green
    Write-Host ("`n" + ("=" * 80) + "`n")
    exit 0
}

$critCount = ($Findings | Where-Object { $_.Severity -eq "CRITICAL" }).Count
$highCount = ($Findings | Where-Object { $_.Severity -eq "HIGH" }).Count
$medCount  = ($Findings | Where-Object { $_.Severity -eq "MEDIUM" }).Count
$lowCount  = ($Findings | Where-Object { $_.Severity -eq "LOW" }).Count

Write-Host "Total Findings: $($Findings.Count) | Critical: $critCount | High: $highCount | Medium: $medCount | Low: $lowCount`n"

$sevOrder = @{ "CRITICAL" = 0; "HIGH" = 1; "MEDIUM" = 2; "LOW" = 3 }
$sorted = $Findings | Sort-Object { $sevOrder[$_.Severity] }

foreach ($f in $sorted) {
    $color = switch ($f.Severity) {
        "CRITICAL" { "Red" }
        "HIGH"     { "DarkRed" }
        "MEDIUM"   { "Yellow" }
        default    { "Gray" }
    }
    Write-Host "[$($f.Severity)] $($f.Rule) ($($f.CWE))" -ForegroundColor $color
    Write-Host "  📍 Location : $($f.File)#L$($f.Line)"
    Write-Host "  🔍 Matched  : $($f.Code)"
    Write-Host "  💡 Guidance : $($f.Guidance)"
    Write-Host ("-" * 80)
}

if ($JsonOut) {
    $Findings | ConvertTo-Json -Depth 4 | Set-Content $JsonOut -Encoding utf8
    Write-Host "Findings exported to: $JsonOut"
}

$sevRanks = @{ "CRITICAL" = 4; "HIGH" = 3; "MEDIUM" = 2; "LOW" = 1 }
$thresh = $sevRanks[$FailOn]
$hasBlocking = ($Findings | Where-Object { $sevRanks[$_.Severity] -ge $thresh }).Count -gt 0

if ($hasBlocking) { exit 1 } else { exit 0 }
