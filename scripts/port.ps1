# Copy one or all skills into a target project in the layout a tool expects.
#   powershell -File scripts/port.ps1 <skill|all> claude|cursor <target-dir>
# claude: copies skills/<name>/ to <target>/.claude/skills/<name>/
# cursor: writes <target>/.cursor/rules/<name>.mdc from SKILL.md and copies
#         references/, scripts/, examples/, features/ to .cursor/rules/<name>/
param(
    [Parameter(Mandatory = $true)][string]$Skill,
    [Parameter(Mandatory = $true)][ValidateSet('claude', 'cursor')][string]$Tool,
    [Parameter(Mandatory = $true)][string]$Target
)
$ErrorActionPreference = 'Stop'
$Kit = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
New-Item -ItemType Directory -Force -Path $Target | Out-Null
$Target = (Resolve-Path $Target).Path

function Get-Frontmatter([string]$path) {
    $lines = Get-Content -Path $path -Encoding UTF8
    $fm = 0; $desc = ''; $folded = $false; $body = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        if ($line -eq '---' -and $fm -lt 2) { $fm++; continue }
        if ($fm -ge 2) { $body.Add($line); continue }
        if ($fm -eq 1) {
            if ($line -match '^description:\s*(.*)$') {
                $v = $Matches[1].Trim()
                if ($v -in @('>-', '>', '|', '')) { $folded = $true } else { $desc = $v }
                continue
            }
            if ($folded -and $line -match '^\s+(.*)$') {
                if ($desc) { $desc += ' ' }
                $desc += $Matches[1].Trim()
                continue
            }
            if ($folded) { $folded = $false }
        }
    }
    return @{ Description = $desc; Body = $body }
}

function Port-One([string]$name) {
    $src = Join-Path $Kit "skills\$name"
    if (-not (Test-Path (Join-Path $src 'SKILL.md'))) { throw "no such skill: $name" }
    if ($Tool -eq 'claude') {
        $dest = Join-Path $Target ".claude\skills\$name"
        if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
        New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
        Copy-Item -Recurse -Path $src -Destination $dest
        Write-Output "claude  $dest"
    } else {
        $rules = Join-Path $Target '.cursor\rules'
        New-Item -ItemType Directory -Force -Path $rules | Out-Null
        $out = Join-Path $rules "$name.mdc"
        $fm = Get-Frontmatter (Join-Path $src 'SKILL.md')
        $desc = $fm.Description -replace '"', '\"'
        $header = @("---", "description: `"$desc`"", "globs:", "alwaysApply: false", "---")
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        $text = (($header + $fm.Body) -join "`n") + "`n"
        [System.IO.File]::WriteAllText($out, $text, $utf8)
        foreach ($d in @('references', 'scripts', 'examples', 'features')) {
            $sd = Join-Path $src $d
            if (Test-Path $sd) {
                $dd = Join-Path $rules "$name\$d"
                if (Test-Path $dd) { Remove-Item -Recurse -Force $dd }
                New-Item -ItemType Directory -Force -Path (Split-Path $dd) | Out-Null
                Copy-Item -Recurse -Path $sd -Destination $dd
            }
        }
        Write-Output "cursor  $out"
    }
}

if ($Skill -eq 'all') {
    Get-ChildItem -Directory (Join-Path $Kit 'skills') | ForEach-Object { Port-One $_.Name }
} else {
    Port-One $Skill
}
